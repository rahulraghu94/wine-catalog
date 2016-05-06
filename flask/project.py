from flask import Flask, render_template

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Catalog, Base, Wine

engine = create_engine('sqlite:///wineCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)      
session = DBSession()


app = Flask(__name__)

@app.route("/list/<int:locId>/")
def list(locId):
	catalog = session.query(Catalog).filter_by(location_id=locId).one()
	num = catalog.location_id
	wine_list = session.query(Wine).filter_by(loc_id = locId)
	print(catalog.location_name)
	return render_template('menu.html', cat=catalog, wine=wine_list)

@app.route("/list/<int:locId>/new/")
def new_location(locId):
	return "Create a new location!"

@app.route("/list/<int:locId>/<int:wineId>/edit/")
def edit_wine(locId, wineId):
	return "Editing a wine"

@app.route("/list/<int:locId>/<int:wineId>/delete/")
def delete_wine(locId, wineId):
	return "Deleting a wine"

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)