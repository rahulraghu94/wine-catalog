from flask import Flask, render_template, request, url_for, redirect

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Catalog, Base, Wine

engine = create_engine('sqlite:///wineCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)      
session = DBSession()

app = Flask(__name__)

################################################################################
# Main Page
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

	print(count)

	print(catalog.location_name)
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
			print("varieta changed")
			wine.wine_varietal = request.form['varietal']
		if request.form['vintage']:
			print("vintage changed")
			wine.wine_vintage = request.form['vintage']
		if request.form['price']:
			print("price changed")
			wine.wine_price = request.form['price']

		session.add(wine)
		session.commit()

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
		return redirect(url_for('list', locId = locId))
	else:	
		return render_template('delete.html', location_id = locId, wine_id = wineId, wine = wine)

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)