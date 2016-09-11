from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, abort, g
import random, string
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from oauth2client.client import AccessTokenCredentials
from redis import Redis
from functools import update_wrapper
import time
import pg

redis = Redis()
db = pg.DB(dbname = 'wine-database')

app = Flask(__name__)
app.secret_key = "super_secret_key"

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

###############################################################################
# Rate Limiting our API
###############################################################################
class RateLimit(object):
	exp_window = 10

	def __init__(self, key_prefix, limit, per, send_x_headers):
		self.reset = (int(time.time()) // per) * per + per
		self.key = key_prefix + str(self.reset)
		self.limit = limit
		self.per = per
		self.send_x_headers = send_x_headers
		p = redis.pipeline()
		p.incr(self.key)
		p.expireat(self.key, self.reset + self.exp_window)
		self.current = min(p.execute()[0], limit)

	remaining = property(lambda x: x.limit - x.current)
	over_limit = property(lambda x: x.current >= x.limit)


def view_rate():
	return getattr(g, '_view_rate_limit', None)

def on_over_limit(limit):
	return (jsonify({'data':'You have hit rate limit', 'error':'429'}), 429)

def rateLimit(limit, per = 300, send_x_headers = True, over_limit = on_over_limit, scope_func = lambda: request.remote_addr, key_func = lambda: request.endpoint):
	def decorator(f):
		def rate_limit(*args, **kwargs):
			key = "(rate-limit/{}/{})".format(key_func(), scope_func())
			rlimit = RateLimit(key, limit, per, send_x_headers)
			g._view_rate_limit = rlimit
			if over_limit is not None and rlimit.over_limit:
				return over_limit(rlimit)
			return f(*args, **kwargs)
		return update_wrapper(rate_limit, f)
	return decorator

@app.after_request
def after_request(response):
	limit = view_rate()
	if limit and limit.send_x_headers:
		h = response.headers
		h.add('X-RateLimit-Remaining', str(limit.remaining))
		h.add('X-RateLimit-Limit', str(limit.limit))
		h.add('X-RateLimit-Reset', str(limit.reset))
	return response


###############################################################################
# Test rate limit
###############################################################################
@app.route('/rate')
def rate():
	return jsonify({'response':'Theirs not to make reply!!!'})


###############################################################################
# Main Page
###############################################################################
@app.route("/")
def main_page():
	return render_template('intro.html')

###############################################################################
# About
###############################################################################
@app.route("/about")
def about():
	return render_template('about.html')

###############################################################################
# API Details
###############################################################################
@app.route("/api")
def api():
	return render_template('API.html')

###############################################################################
# Display World Map that is clickable
###############################################################################
@app.route('/home')
def home():
	if 'username' not in login_session:
		return redirect('/login')
	print(login_session)
	return render_template('world.html')

@app.route('/home/v1/countries')
@rateLimit(limit = 300, per = 30 * 1)
def get_countries():
	#if 'username' not in login_session:
	#	return redirect('/login')
	db.query('begin')
	catalog = db.query('select * from catalog')
	cat = catalog.dictresult()
	db.query('end')

	return jsonify(cat)

###############################################################################
# This function recieves the name of the country as clicked on the world map.
# We then check if this country is already listed/
# If listed, open up the page that will ist all the wines in it, along with
# add, delete, edit, etc.
# If not, then add the country to the catalog database and take the user to the
# page where we can add and delete wines
###############################################################################
@app.route('/location', methods = ['POST'])
def location():
	if 'username' not in login_session:
		return redirect('/login')

	country = request.json['name']
	print(country)
	db.query('begin')
	query = ("select * from catalog where location_name = '{}'").format(country)
	print(query)

	catalog = db.query(query)
	catalog = catalog.dictresult()
	print(catalog)

	if not catalog:
		db.insert('catalog', {'location_name':country, 'user_id':login_session['user_id']})
		db.query('end')
	else:
		print("Country exists ...")
		db.query('end')
		return "motherfucker"


###############################################################################
# The /location page consists of a clickable map. When clicked, the map will
# will repond with a JSON message back to the server through JQuery and AJAX
# The JSON message will be sent from the client side to /list
# The server, on /list will extract data of the country clicked from the
# database and will render a page that lists all the wines of the country
# This page can be used to add more wines, if logged in.
###############################################################################
@app.route('/list')
def list():
	if 'username' not in login_session:
		return redirect('/login')
	country = request.args.get('name')
	db.query('begin')
	query = ("select * from catalog where location_name = '{}'").format(country)

	cat = db.query(query)
	cat = cat.dictresult()

	loc_id = cat[0]['location_id']
	query = ("select * from wine where loc_id = {}").format(loc_id)
	wine = db.query(query)
	wine = wine.dictresult()

	query = ("select * from users where id = '{}'").format(cat[0]['user_id'])
	user = db.query(query)
	db.query('end')
	user = user.dictresult()


	return render_template('list.html', cat = cat, wine = wine, location_id = loc_id, user = user[0])

@app.route('/list/v1/wines', methods = ['GET', 'POST'])
@rateLimit(limit = 300, per = 30 * 1)
def get_wines():

	country = request.args.get('name')
	db.query('begin')
	query = ("select * from catalog where location_name = '{}'").format(country)

	cat = db.query(query)
	cat = cat.dictresult()
	loc_id = cat[0]['location_id']


	query = ("select * from wine where loc_id = '{}'").format(loc_id)

	wine = db.query(query)
	wine = wine.dictresult()
	db.query('end')
	return jsonify(wine)

###############################################################################
# Addig a wine
###############################################################################
@app.route("/list/<int:locId>/new/", methods=['GET', 'POST'])
def new_wine(locId):
	if 'username' not in login_session:
		return redirect('/login')

	db.query('begin')
	query = ("select * from catalog where location_id = {}").format(locId)
	location = db.query(query)
	location = location.dictresult()
	country = location[0]['location_name']
	user_id = getUserId(login_session['email'])

	if request.method == 'POST':
		new = {'wine_maker' :request.form['maker'], 'wine_vintage': request.form['vintage'],
			'wine_varietal': request.form['varietal'],
	         'wine_price' : request.form['price'], 'loc_id': locId, 'user_id':user_id}
		db.insert('wine', new)
		db.query('end')
		return redirect(url_for('list', name = country))

	else:
		print("Rendering entered")
		query = ("select * from users where id = '{}'").format(wine[0]['user_id'])
		user = db.query(query)
		user = user.dictresult()
		db.query('end')
		return render_template('list.html', cat = cat, wine = wine, location_id = loc_id, pic = user[0]['picture'])

###############################################################################
# Edit a wine
###############################################################################
@app.route("/list/<int:locId>/<int:wineId>/edit/", methods=['GET', 'POST'])
def edit_wine(locId, wineId):
	if 'username' not in login_session:
		return redirect('/login')

	db.query('begin')
	query = ("select * from catalog where location_id = '{}'").format(locId)
	catalog = db.query(query)
	catalog = catalog.dictresult()
	country = catalog[0]['location_name']

	query = ("select * from wine where wine_id = '{}'").format(wineId)
	wine_old = db.query(query)
	wine_old = wine_old.dictresult()
	wine = wine_old[0]

	if request.method == 'POST':
		if request.form['maker']:
			wine['wine_maker'] = request.form['maker']
		if request.form['varietal']:
			wine['wine_varietal'] = request.form['varietal']
		if request.form['vintage']:
			wine['wine_vintage'] = request.form['vintage']
		if request.form['price']:
			wine['wine_price'] = request.form['price']

		db.update('wine', wine)
		db.query('end')

		return redirect(url_for('list', name = country))

	else:
		query = ("select * from users where id = '{}'").format(wine[0]['user_id'])
		user = db.query(query)
		user = user.dictresult()
		db.query('end')
		return render_template('list.html', cat = cat, wine = wine, location_id = loc_id, pic = user[0]['picture'])

###############################################################################
# Delete a wine
###############################################################################
@app.route("/list/<int:locId>/<int:wineId>/delete/", methods=['GET', 'POST'])
def delete_wine(locId, wineId):
	if 'username' not in login_session:
		return redirect('/login')

	db.query('begin')
	query = ("select * from catalog where location_id = '{}'").format(locId)
	catalog = db.query(query)
	catalog = catalog.dictresult()

	country = catalog[0]['location_name']

	query = ("select * from wine where wine_id = '{}'").format(wineId)
	wine = db.query(query)
	wine = wine.dictresult()
	wine = wine[0]

	if not wine:
		db.query('end')
		return "Wine already deleted"

	if request.method == 'POST':
		print("wine had been deleted!")
		db.delete('wine', wine)
		db.query('end')
		return redirect(url_for('list', name = country))
	else:
		query = ("select * from users where id = '{}'").format(wine[0]['user_id'])
		user = db.query(query)
		user = user.dictresult()
		db.query('end')
		return render_template('list.html', cat = cat, wine = wine, location_id = loc_id, pic = user[0]['picture'])

###############################################################################
# Login
###############################################################################
def getUserId(email):
	try:
		db.query('begin')
		print("Email is: ", email)
		query = ("select * from users where email = '{}'").format(email)
		user = db.query(query)
		user = user.dictresult()
		print("(getUserId) Found user is: ", user)
		db.query('end')
		return user[0]['id']
	except:
		return None

def getUserInfo(user_id):
	#this_session = session()
	print("Trying to get user id...")
	db.query('begin')
	user = ("select * from users where id = '{}'").format(user_id)
	user = user.dictresult()
	user = user[0]
	db.query('end')
	#user = this_session.query(User).filter_by(id = user_id).one()
	#session.remove()
	print("Get user info done...Returning ", user)
	return user

def createUser(login_session):
	new_user = {'name' : login_session['username'], 'email' : login_session['email'], 'picture' : login_session['picture']}

	#this_session = session();
	#this_session.add(newUser)
	#this_session.commit()
	#

	print("Creating user info: ", new_user)

	db.query('begin')
	db.insert('users', new_user)
	query = ("select * from users where email = '{}'").format(login_session['email'])
	user = db.query(query)
	user = user.dictresult()
	user = user[0]
	#user = this_session.query(User).filter_by(email = login_session['email']).one()
	#session.remove()

	db.query('end')
	return user['id']

@app.route('/gconnect', methods = ['POST'])
def gconnect():
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter you mofofs'), 401)
		response.headers['Content-tyoe'] = 'application/json'
		return response

	code = request.data

	try:
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(json.dumps('Auth Code Upgradation Failure'), 401)
		response.headers['Content-tyoe'] = 'application/json'
		return response

	access_token = credentials.access_token
	url = 'https://www.googleapis.com/oauth2/v2/tokeninfo?access_token='
	url = url + access_token
	h = httplib2.Http()

	result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))

	if result.get('error') is not None:
		response - make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-tyoe'] = 'application/json'

	gplus_id = credentials.id_token['sub']

	if result['user_id'] != gplus_id:
		response = make_response(json.dumps("Token ID mismatch"), 401)
		response.headers['Content-tyoe'] = 'application/json'
		return response

	if result['issued_to'] != CLIENT_ID:
		response = make_response(json.dumps('Client ID mismatch'), 401)
		print("Check client ID")
		response.headers['Content-tyoe'] = 'application/json'
		return response

	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')

	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('User is already logged in'), 200)
		response.headers['Content-tyoe'] = 'application/json'

	login_session['credentials'] = credentials.access_token
	credentials = AccessTokenCredentials(login_session['credentials'], 'user-agent-value')
	login_session['gplus_id'] = gplus_id

	userinfo_url = ("https://www.googleapis.com/oauth2/v2/userinfo")
	params = {'access_token' : credentials.access_token, 'alt' : 'json'}

	answer = requests.get(userinfo_url, params=params)
	data = json.loads(answer.text)

	#print(data)

	login_session['username'] = data["name"]
	login_session['picture'] = data["picture"]
	login_session['email'] = data["link"]

	user_id = getUserId(login_session['email'])

	if not user_id:
		print("User ID not got... :(")
		user_id = createUser(login_session)
	login_session['user_id'] = user_id

	return "rmuterfucker"

@app.route("/gdisconnect")
def gdisconnect():
	credentials = login_session['credentials']
	print("Credentials are:", credentials)
	if credentials is None:
		response = make_response(json.dumps('The currant user is not logged in'), 401)
		response.headers['Content-tyoe'] = 'application/json'
		return response

	access_token = credentials
	url = "https://accounts.google.com/o/oauth2/revoke?token="
	url += access_token

	print(url)

	h = httplib2.Http()
	result = h.request(url, 'GET')[0]

	print(result)

	if result['status'] == '200':
		del login_session['username']
		del login_session['picture']
		del login_session['email']

		response = make_response(json.dumps('Successfully disconnected!'), 200)
		response.headers['Content-tyoe'] = 'application/json'
		return redirect('/home')

	else:
		response = make_response(json.dumps("Something went wrong... Try again"), 400)
		response.headers['Content-tyoe'] = 'application/json'
		return response

@app.route('/login')
def login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)