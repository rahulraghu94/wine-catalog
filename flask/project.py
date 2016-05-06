from flask import Flask

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Catalog, Base, Wine

engine = create_engine('sqlite:///wineCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)      
session = DBSession()


app = Flask(__name__)

@app.route("/")
@app.route("/hello")
def helloWorld():
	catalog = session.query(Catalog).first()
	num = catalog.location_id
	print(num)
	wine_list = session.query(Wine).filter_by(loc_id = 8)

	output = ""

	for wine in wine_list:
		output += wine.wine_maker
		output += "<br>"
		output += wine.wine_varietal
		output += "<br>"
		output += str(wine.wine_vintage)
		output += "<br>"
		output += str(wine.wine_price)
		output += "<br>"
		output += "<hr>"

	return output

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)