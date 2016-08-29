from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, abort, g
#from flask_httpauth import HTTPBasicAuth

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Catalog, Base, Wine, User
import random, string
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from oauth2client.client import AccessTokenCredentials
#import wikipedia
from redis import Redis
from functools import update_wrapper
import time

redis = Redis()

engine = create_engine('sqlite:///wineCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = scoped_session(DBSession)

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

	ses = session()

	catalog = ses.query(Catalog).all()

	return jsonify(cat = [c.serialize for c in catalog])

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

	this_session = session()

	if this_session.query(Catalog).filter_by(location_name = country).scalar() is None:
		print("Country does not exits...")
		catalog = Catalog(location_name = country, user_id = login_session['user_id'])
		this_session.add(catalog)
		this_session.commit()
		session.remove()
		return "motherfucker"
	else:
		print("Country exists ...")
		session.remove()
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
	query = country
	query = query + " wine"
	#country_data = wikipedia.summary(query)
	this_session = session()

	catalog = this_session.query(Catalog).filter_by(location_name = country).one()
	wine = this_session.query(Wine).filter_by(loc_id = catalog.location_id).all()
	locId = catalog.location_id
	return render_template('list.html', cat = catalog, wine = wine, location_id = locId, name = login_session['username'])

@app.route('/list/v1/wines', methods = ['GET', 'POST'])
@rateLimit(limit = 300, per = 30 * 1)
def get_wines():
	#if 'username' not in login_session:
	#	return redirect('/login')

	ses = session()
	country = request.args.get('name')
	print("country is: ", country)
	cat = ses.query(Catalog).filter_by(location_name = country).one()
	wine = ses.query(Wine).filter_by(loc_id = cat.location_id).all()
	session.remove()
	return jsonify(wine = [w.serialize for w in wine])

###############################################################################
# Addig a wine
###############################################################################
@app.route("/list/<int:locId>/new/", methods=['GET', 'POST'])
def new_wine(locId):
	if 'username' not in login_session:
		return redirect('/login')
	this_session = session()

	location = this_session.query(Catalog).filter_by(location_id=locId).one()

	country = location.location_name

	if request.method == 'POST':
		new = Wine(wine_maker = request.form['maker'], wine_vintage = request.form['vintage'],
			wine_varietal = request.form['varietal'],
	         wine_price = request.form['price'], loc_id = locId, wine = location)
		this_session.add(new)
		this_session.commit()
		flash("New wine added!")
		session.remove()
		return redirect(url_for('list', name = country))

	else:
		print("Rendering entered")
		session.remove()
		return render_template('add.html', location_id = locId)


###############################################################################
# Edit a wine
###############################################################################
@app.route("/list/<int:locId>/<int:wineId>/edit/", methods=['GET', 'POST'])
def edit_wine(locId, wineId):
	if 'username' not in login_session:
		return redirect('/login')
	this_session = session()
	location = this_session.query(Catalog).filter_by(location_id=locId).one()
	wine = this_session.query(Wine).filter_by(wine_id = wineId).one()

	country = location.location_name

	if request.method == 'POST':
		if request.form['maker']:
			wine.wine_maker = request.form['maker']
		if request.form['varietal']:
			wine.wine_varietal = request.form['varietal']
		if request.form['vintage']:
			wine.wine_vintage = request.form['vintage']
		if request.form['price']:
			wine.wine_price = request.form['price']

		this_session.add(wine)
		this_session.commit()
		session.remove()
		return redirect(url_for('list', name = country))

	else:
		session.remove()
		return render_template('edit.html', location_id = locId, wine_id = wineId, wine = wine)

###############################################################################
# Delete a wine
###############################################################################
@app.route("/list/<int:locId>/<int:wineId>/delete/", methods=['GET', 'POST'])
def delete_wine(locId, wineId):
	if 'username' not in login_session:
		return redirect('/login')
	this_session = session()
	location = this_session.query(Catalog).filter_by(location_id=locId).one()
	wine = this_session.query(Wine).filter_by(wine_id = wineId).one()

	country = location.location_name

	if not wine:
		return "Wine already deleted"

	if request.method == 'POST':
		this_session.delete(wine)
		this_session.commit()
		print("wine had been deleted!")
		session.remove()
		return redirect(url_for('list', name = country))
	else:
		session.remove()
		return render_template('delete.html', location_id = locId, wine_id = wineId, var = wine.wine_varietal, maker = wine.wine_maker)


###############################################################################
# Login
###############################################################################
def getUserId(email):
	this_session = session()
	try:
		user = this_session.query(User).filter_by(email = email).one()
		session.remove()
		return user.id
	except:
		session.remove()
		return None

def getUserInfo(user_id):
	this_session = session()

	user = this_session.query(User).filter_by(id = user_id).one()
	session.remove()
	return user

def createUser(login_session):
	newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])

	this_session = session();
	this_session.add(newUser)
	this_session.commit()

	user = this_session.query(User).filter_by(email = login_session['email']).one()
	session.remove()
	return user.id

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

	print(data)

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
		return response

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
