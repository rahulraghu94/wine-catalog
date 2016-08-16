from flask import Flask, render_template, request, url_for, redirect, flash, jsonify, abort, g
from flask_httpauth import HTTPBasicAuth

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Catalog, Base, Wine, User

engine = create_engine('sqlite:///wineCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)      
session = scoped_session(DBSession)

app = Flask(__name__)

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
	print("hello Word")
	session.remove()
	return render_template('index.html')

###############################################################################
# List out locations
###############################################################################
@app.route("/explore")
def explore():

	this_session = session()
	catalog = this_session.query(Catalog)
	return render_template('main.html', cat = catalog)
	session.remove()

@app.route("/explore/api/get")
def locationJson():
	this_session = session()
	cat = this_session.query(Catalog).all()
	session.remove()
	return jsonify(loc = [i.ser for i in cat])

###############################################################################
# Add new Location
###############################################################################
@app.route("/new/", methods=['GET', 'POST'])
def new_location():
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
		new = Catalog(location_id = count, location_name = request.form['name'])
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
	return render_template('menu.html', cat=catalog, wine=wine_list)

###############################################################################
# Addig a wine
###############################################################################

@app.route("/list/<int:locId>/new/", methods=['GET', 'POST'])
def new_wine(locId):
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
	         wine_price = request.form['price'], wine_id = count, loc_id = locId, wine = location)
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

if __name__ == '__main__':
	app.secret_key = "super_secret_key"
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000)