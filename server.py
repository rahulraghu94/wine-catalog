from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, abort, g
from flask_httpauth import HTTPBasicAuth

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Catalog, Base, Wine
import random, string
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response 
import requests
from oauth2client.client import AccessTokenCredentials
import wikipedia

engine = create_engine('sqlite:///wineCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)      
session = scoped_session(DBSession)

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

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
# Display World Map that is clickable
###############################################################################
@app.route('/home')
def home():
	return render_template('world.html')

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
	country = request.json['name']
	print(country)

	this_session = session()

	if this_session.query(Catalog).filter_by(location_name = country).scalar() is None:
		print("Country does not exits...")
		catalog = Catalog(location_name = country)
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
	country = request.args.get('name')
	query = country
	query = query + " wine"
	#country_data = wikipedia.summary(query)
	this_session = session()

	catalog = this_session.query(Catalog).filter_by(location_name = country).one()
	wine = this_session.query(Wine).filter_by(loc_id = catalog.location_id).all()
	locId = catalog.location_id
	return render_template('list.html', cat = catalog, wine = wine, location_id = locId)

###############################################################################
# Addig a wine
###############################################################################
@app.route("/list/<int:locId>/new/", methods=['GET', 'POST'])
def new_wine(locId):
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
# Edit a wine
###############################################################################
@app.route("/list/<int:locId>/<int:wineId>/delete/", methods=['GET', 'POST'])
def delete_wine(locId, wineId):
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
# TEST LOGIN
###############################################################################
@app.route('/login')
def login():
	return redirect('/home')

if __name__ == '__main__':
	app.secret_key = "super_secret_key"
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)