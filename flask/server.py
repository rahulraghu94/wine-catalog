from flask import Flask, render_template, request, url_for, redirect, flash, jsonify

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Catalog, Base, Wine

engine = create_engine('sqlite:///wineCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)      
session = DBSession()

app = Flask(__name__)


################################################################################
# JSON Route
################################################################################
@app.route("/list/<int:locId>/JSON")
def wineCatalogJson(locId):
	catalog = session.query(Catalog).filter_by(location_id = locId).one()
	wine = session.query(Wine).filter_by(loc_id = locId).all()

	return jsonify(wine=[i.serialize for i in wine])


################################################################################
# Main Page
################################################################################
@app.route("/")
def main_page():
	catalog = session.query(Catalog)
	print("hello Wo rd")
	return render_template('main.html', cat = catalog)

################################################################################
# Add new Location
################################################################################
@app.route("/new/", methods=['GET', 'POST'])
def new_location():
	cat = session.query(Catalog)
	global count
	count = 1
	for c in cat:
		if count == c.location_id:
			count += 1
		else:
			break

	if request.method == 'POST':
		new = Catalog(location_id = count, location_name = request.form['name'])
		session.add(new)
		session.commit()

		return redirect(url_for('main_page'))
	else:
		return render_template('new_location.html')
################################################################################
# Locations page
################################################################################
@app.route("/list/<int:locId>/")
def list(locId):
	catalog = session.query(Catalog).filter_by(location_id=locId).one()
	num = catalog.location_id
	wine_list = session.query(Wine).filter_by(loc_id = locId)

	wine = session.query(Wine)
	count = 1

	for w in wine:
		if count == w.wine_id:
			count += 1
		else:
			break

	return render_template('menu.html', cat=catalog, wine=wine_list)

################################################################################
# Addig a wine
################################################################################

@app.route("/list/<int:locId>/new/", methods=['GET', 'POST'])
def new_wine(locId):

	global oount 
	count = 1
	wine = session.query(Wine)
	for w in wine:
		if count == w.wine_id:
			count += 1
		else:
			break

	print(count)

	location = session.query(Catalog).filter_by(location_id=locId).one()

	if request.method == 'POST':
		new = Wine(wine_maker = request.form['maker'], wine_vintage = request.form['vintage'], 
			wine_varietal = request.form['varietal'], 
	         wine_price = request.form['price'], wine_id = count, loc_id = locId, wine = location)
		session.add(new)
		session.commit()
		flash("New wine added!")
		return redirect(url_for('list', locId = locId))

	else:
		return render_template('new.html', location_id = locId)

################################################################################
#editing
################################################################################

@app.route("/list/<int:locId>/<int:wineId>/edit/", methods=['GET', 'POST'])
def edit_wine(locId, wineId):
	location = session.query(Catalog).filter_by(location_id=locId).one()
	wine = session.query(Wine).filter_by(wine_id = wineId).one()

	if request.method == 'POST':
		if request.form['maker']:
			wine.wine_maker = request.form['maker']
		if request.form['varietal']:
			wine.wine_varietal = request.form['varietal']
		if request.form['vintage']:
			wine.wine_vintage = request.form['vintage']
		if request.form['price']:
			wine.wine_price = request.form['price']

		session.add(wine)
		session.commit()
		flash("Wine has been Edited!")

		return redirect(url_for('list', locId = locId))

	else:
		return render_template('edit.html', location_id = locId, wine_id = wineId, wine = wine)

################################################################################
#Deleting
################################################################################
@app.route("/list/<int:locId>/<int:wineId>/delete/", methods=['GET', 'POST'])
def delete_wine(locId, wineId):
	location = session.query(Catalog).filter_by(location_id=locId).one()
	wine = session.query(Wine).filter_by(wine_id = wineId).one()
	if request.method == 'POST':
		session.delete(wine)
		session.commit
		flash("wine had been deleted!")
		return redirect(url_for('list', locId = locId))
	else:	
		return render_template('delete.html', location_id = locId, wine_id = wineId, wine = wine)

if __name__ == '__main__':
	app.secret_key = "super_secret_key"
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)