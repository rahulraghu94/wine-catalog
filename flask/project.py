from flask import Flask

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Wine, Base, WineDetails

engine = create_engine('sqlite:///wineCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)       
session = DBSession()


app = Flask(__name__)

@app.route("/")
@app.route("/hello")
def helloWorld():
	wine = session.query(Wine).first()
	details = session.query(WineDetails).filter_by(wine_id = wine.id)

	output = ""

	for det in details:
		output += det.name
		output += "<br>"
		output += str(det.vintage)
		output += "<br>"
		output += str(det.price)
		output += "<br>"
		output += "<hr>"

	return output

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)