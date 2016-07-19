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
auth = HTTPBasicAuth()

###############################################################################
# New User
###############################################################################
@auth.verify_password
def verify_password(usr, pwd):

	user_id = User.verify_auth_token(usr)

	this_session = session()
	
	if user_id:
		user = this_session.query(User).filter_by(user_name = usr).first()
	else:
		user = this_session.query(User).filter_by(user_name = usr).first()
	
	if not user or not user.verify(pwd):
		return False
	
	g.user = user

	this_session.remove()
	return True

@app.route("/users", methods = ['POST', 'GET'])
def new_user():

	this_session = session()

	users = this_session.query(User)
	global count
	count = 1
	for c in users:
		if count == c.id:
			count += 1
		else:
			break

	if request.method == 'POST':
		usr = request.form['username']
		pwd = request.form['password']

		if usr is None or pwd is None:
			abort(400)

		if this_session.query(User).filter_by(user_name = usr).first() is not None:
			abort(400)

		user = User(id = count, user_name = usr)
		user.hash(pwd)
		this_session.add(user)
		this_session.commit()
		print("New user made")

		return redirect(url_for('explore'))
	
	else:
		return render_template('new_user.html')	

	this_session.remove()

@app.route('/token')
@auth.login_required
def get_auth_token():
	token = g.user.generate_auth_token()
	return jsonify({'token':token.decode('ascii')})


@app.route("/logged")

###############################################################################
# JSON Route
###############################################################################
@app.route("/list/<int:locId>/api/get")
@auth.login_required
def wineCatalogJson(locId):

	this_session = session()

	catalog = this_session.query(Catalog).filter_by(location_id = locId).one()
	wine = this_session.query(Wine).filter_by(loc_id = locId).all()

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
	return render_template('index.html')
	this_session.remove()

###############################################################################
# List out locations
###############################################################################
@app.route("/explore")
def explore():

	this_session = session()
	catalog = this_session.query(Catalog)
	return render_template('main.html', cat = catalog)
	this_session.remove()

@app.route("/explore/api/get")
@auth.login_required
def locationJson():
	cat = session.query(Catalog).all()
	return jsonify(loc = [i.ser for i in cat])

###############################################################################
# Add new Location
###############################################################################
@app.route("/new/", methods=['GET', 'POST'])
@auth.login_required
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

		return redirect(url_for('explore'))
	else:
		return render_template('new_location.html')
###############################################################################
# Locations page
###############################################################################
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

###############################################################################
# Addig a wine
###############################################################################

@app.route("/list/<int:locId>/new/", methods=['GET', 'POST'])
@auth.login_required
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
		print("Rendering entered")
		return render_template('new.html', location_id = locId)

###############################################################################
#editing
###############################################################################

@app.route("/list/<int:locId>/<int:wineId>/edit/", methods=['GET', 'POST'])
@auth.login_required
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

###############################################################################
#Deleting
###############################################################################
@app.route("/list/<int:locId>/<int:wineId>/delete/", methods=['GET', 'POST'])
@auth.login_required
def delete_wine(locId, wineId):
	location = session.query(Catalog).filter_by(location_id=locId).one()
	wine = session.query(Wine).filter_by(wine_id = wineId).one()

	if not wine:
		return "Wine already deleted"
		
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
	app.run(host = '0.0.0.0', port = 8000)