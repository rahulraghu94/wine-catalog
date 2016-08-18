from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, abort, g
from flask_httpauth import HTTPBasicAuth

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

engine = create_engine('sqlite:///wineCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)      
session = scoped_session(DBSession)

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

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

	login_session['username'] = data["name"]
	login_session['picture'] = data["picture"]
	login_session['email'] = data["link"]

	user_id = getUserId(login_session['email'])

	if not user_id:
		print("User ID not got... :(")
		user_id = createUser(login_session)
	login_session['user_id'] = user_id

	return render_template('after_login.html', NAME=login_session['username'], PIC=login_session['picture'])

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

	h = httplib2.Http()
	result = h.request(url, 'GET')[0]

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

@app.route("/login")
def login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))

	login_session['state'] = state
	return render_template('login.html', STATE=state)

###############################################################################
# JSON Route
###############################################################################
@app.route("/list/<int:locId>/api/get")
def wineCatalogJson(locId):

	this_session = session()

	catalog = this_session.query(Catalog).filter_by(location_id = locId).one()
	wine = this_session.query(Wine).filter_by(loc_id = locId).all()
	session.remove()
	return jsonify(wine=[i.serialize for i in wine])


###############################################################################
# About
###############################################################################
@app.route("/about")
def about():
	return render_template('about.html')

###############################################################################
# Main Page
###############################################################################
@app.route("/")
def main_page():

	this_session = session()

	catalog = this_session.query(Catalog)
	print("hello Woord")
	session.remove()
	return render_template('index.html')

###############################################################################
# List out locations
###############################################################################
@app.route("/explore")
def explore():
	this_session = session()
	catalog = this_session.query(Catalog)
	if 'username' not in login_session:
		return render_template('main_public.html', cat = catalog)
	else: 
		return render_template('main.html', cat = catalog)
	session.remove()

@app.route("/explore/api/get")
def locationJson():
	if 'username' not in login_session:
		return redirect('/login')
	this_session = session()
	cat = this_session.query(Catalog).all()
	session.remove()
	return jsonify(loc = [i.ser for i in cat])

###############################################################################
# Add new Location
###############################################################################
@app.route("/new/", methods=['GET', 'POST'])
def new_location():
	if 'username' not in login_session:
		return redirect('/login')

	this_session = session()
	cat = this_session.query(Catalog)
	global count
	count = 1
	for c in cat:
		if count == c.location_id:
			count += 1
		else:
			break

	if request.method == 'POST':
		new = Catalog(location_id = count, location_name = request.form['name'], user_id = login_session['user_id'])
		this_session.add(new)
		this_session.commit()
		session.remove()
		return redirect(url_for('explore'))
	else:
		session.remove()
		return render_template('new_location.html')
###############################################################################
# Locations page
###############################################################################
@app.route("/list/<int:locId>/")
def list(locId):
	this_session = session()
	catalog = this_session.query(Catalog).filter_by(location_id=locId).one()
	num = catalog.location_id
	wine_list = this_session.query(Wine).filter_by(loc_id = locId)

	wine = this_session.query(Wine)
	count = 1

	for w in wine:
		if count == w.wine_id:
			count += 1
		else:
			break

	session.remove()
	if 'username' not in login_session:
		return render_template('menu_public.html', cat = catalog, wine = wine_list)
	else:
		return render_template('menu.html', cat=catalog, wine=wine_list)

###############################################################################
# Addig a wine
###############################################################################

@app.route("/list/<int:locId>/new/", methods=['GET', 'POST'])
def new_wine(locId):
	if 'username' not in login_session:
		return redirect('/login')
	this_session = session()
	global oount 
	count = 1
	wine = this_session.query(Wine)
	for w in wine:
		if count == w.wine_id:
			count += 1
		else:
			break

	print(count)

	location = this_session.query(Catalog).filter_by(location_id=locId).one()

	if request.method == 'POST':
		new = Wine(wine_maker = request.form['maker'], wine_vintage = request.form['vintage'], 
			wine_varietal = request.form['varietal'], 
	         wine_price = request.form['price'], wine_id = count, loc_id = locId, wine = location, user_id = login_session['user_id'])
		this_session.add(new)
		this_session.commit()
		flash("New wine added!")
		session.remove()
		return redirect(url_for('list', locId = locId))

	else:
		print("Rendering entered")
		session.remove()
		return render_template('new.html', location_id = locId)

###############################################################################
#editing
###############################################################################

@app.route("/list/<int:locId>/<int:wineId>/edit/", methods=['GET', 'POST'])
def edit_wine(locId, wineId):
	if 'username' not in login_session:
		return redirect('/login')
	this_session = session()
	location = this_session.query(Catalog).filter_by(location_id=locId).one()
	wine = this_session.query(Wine).filter_by(wine_id = wineId).one()

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
		flash("Wine has been Edited!")
		session.remove()
		return redirect(url_for('list', locId = locId))

	else:
		session.remove()
		return render_template('edit.html', location_id = locId, wine_id = wineId, wine = wine)

###############################################################################
#Deleting
###############################################################################
@app.route("/list/<int:locId>/<int:wineId>/delete/", methods=['GET', 'POST'])
def delete_wine(locId, wineId):
	if 'username' not in login_session:
		return redirect('/login')
	this_session = session()
	location = this_session.query(Catalog).filter_by(location_id=locId).one()
	wine = this_session.query(Wine).filter_by(wine_id = wineId).one()

	if not wine:
		return "Wine already deleted"
		
	if request.method == 'POST':
		this_session.delete(wine)
		this_session.commit
		flash("wine had been deleted!")
		session.remove()
		return redirect(url_for('list', locId = locId))
	else:	
		session.remove()
		return render_template('delete.html', location_id = locId, wine_id = wineId, wine = wine)

###############################################################################
# Handle New users
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

if __name__ == '__main__':
	app.secret_key = "super_secret_key"
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)