from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Catalog, Base, Wine

engine = create_engine('sqlite:///wineCatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

count = 0

##############################################################################

location1 = Catalog(location_id = 1, location_name = "Italy", user_id = 1)
session.add(location1)
session.commit()
print("Location 1 Added!")

wine1 = Wine(wine_maker = "Zonin", wine_vintage = 2012, wine_varietal = "Chianti",
	         wine_price = 1900, wine_id = 1, loc_id = 1, wine = location1, user_id = 1)
session.add(wine1)
session.commit()
print(count, " wine added!")
count += 1

wine1 = Wine(wine_maker = "Mateus", wine_vintage = 2010, wine_varietal = "Syrah",
	         wine_price = 2900, wine_id = 2, loc_id = 1, wine = location1, user_id = 1)
session.add(wine1)
session.commit()
print(count, " wine added!")
count += 1

wine1 = Wine(wine_maker = "Zonin", wine_vintage = 2011, wine_varietal = "Montepulciano D'Abruzzo",
	         wine_price = 1600, wine_id = 3, loc_id = 1, wine = location1, user_id = 1)
session.add(wine1)
session.commit()
print(count, " wine added!")
count += 1

##############################################################################

location2 = Catalog(location_id = 2, location_name = "France", user_id = 1)
session.add(location2)
session.commit()
print("Location 2 Added!")

wine2 = Wine(wine_maker = "Domaine De Claire", wine_vintage = 2012, wine_varietal = "Chardonnay",
	         wine_price = 2200, wine_id = 4, loc_id = 2, wine = location2, user_id = 1)
session.add(wine2)
session.commit()
print(count, " wine added!")
count += 1

wine2 = Wine(wine_maker = "Chateau La Tour", wine_vintage = 2010, wine_varietal = "Cabernet Sauvignon",
	         wine_price = 3800, wine_id = 5, loc_id = 2, wine = location2, user_id = 1)
session.add(wine2)
session.commit()
print(count, " wine added!")
count += 1

wine2 = Wine(wine_maker = "Martin trichard", wine_vintage = 2011, wine_varietal = "Beaujolais",
	         wine_price = 4400, wine_id = 6, loc_id = 2, wine = location2, user_id = 1)
session.add(wine2)
session.commit()
print(count, " wine added!")
count += 1

wine2 = Wine(wine_maker = "Moet&Chandon", wine_vintage = 2001, wine_varietal = "Champagne",
	         wine_price = 9900, wine_id = 7, loc_id = 2, wine = location2, user_id = 1)
session.add(wine2)
session.commit()
print(count, " wine added!")
count += 1


##############################################################################

location3 = Catalog(location_id = 3, location_name = "United States of America", user_id = 1)
session.add(location3)
session.commit()
print("Location 3 Added!")

wine3 = Wine(wine_maker = "Witchcraft", wine_vintage = 2001, wine_varietal = "Pinot Noir",
	         wine_price = 9900, wine_id = 8, loc_id = 3, wine = location3, user_id = 1)
session.add(wine3)
session.commit()
print(count, " wine added!")
count += 1

wine3 = Wine(wine_maker = "Andrew Murray", wine_vintage = 2001, wine_varietal = "Estate Syrah",
	         wine_price = 9900, wine_id = 9, loc_id = 3, wine = location3, user_id = 1)
session.add(wine3)
session.commit()
print(count, " wine added!")
count += 1

wine3 = Wine(wine_maker = "Chateau Montelena", wine_vintage = 2001, wine_varietal = "Chardnnay",
	         wine_price = 9900, wine_id = 10, loc_id = 3, wine = location3, user_id = 1)
session.add(wine3)
session.commit()
print(count, " wine added!")
count += 1

##############################################################################

location4 = Catalog(location_id = 4, location_name = "Argentina", user_id = 1)
session.add(location4)
session.commit()
print("Location 4 Added!")

wine4 = Wine(wine_maker = "Finca Don Cano", wine_vintage = 2010, wine_varietal = "Malbec",
	         wine_price = 2450, wine_id = 11, loc_id = 4, wine = location4, user_id = 1)
session.add(wine4)
session.commit()
print(count, " wine added!")
count += 1

wine4 = Wine(wine_maker = "Bodegas López", wine_vintage = 2012, wine_varietal = "Malbec",
	         wine_price = 1980, wine_id = 12, loc_id = 4, wine = location4, user_id = 1)
session.add(wine4)
session.commit()
print(count, " wine added!")
count += 1

##############################################################################

location5 = Catalog(location_id = 5, location_name = "Germany", user_id = 1)
session.add(location5)
session.commit()
print("Location 5 Added!")

wine5 = Wine(wine_maker = "Gunderloch Estate", wine_vintage = 2012, wine_varietal = "Reisling",
	         wine_price = 2300, wine_id = 13, loc_id = 5, wine = location5, user_id = 1)
session.add(wine5)
session.commit()
print(count, " wine added!")
count += 1

wine5 = Wine(wine_maker = "Willm", wine_vintage = 2013, wine_varietal = "Gewurztraminer",
	         wine_price = 2140, wine_id = 14, loc_id = 5, wine = location5, user_id = 1)
session.add(wine5)
session.commit()
print(count, " wine added!")
count += 1

##############################################################################

location6 = Catalog(location_id = 6, location_name = "Australia", user_id = 1)
session.add(location6)
session.commit()
print("Location 6 Added!")

wine6 = Wine(wine_maker = "Castle Rock Estate", wine_vintage = 2014, wine_varietal = "Pinot Noir",
	         wine_price = 1560, wine_id = 15, loc_id = 6, wine = location6, user_id = 1)
session.add(wine6)
session.commit()
print(count, " wine added!")
count += 1

wine6 = Wine(wine_maker = "Tar & Roses", wine_vintage = 2009, wine_varietal = "Shiraz Rose",
	         wine_price = 2200, wine_id = 16, loc_id = 6, wine = location6, user_id = 1)
session.add(wine6)
session.commit()
print(count, " wine added!")
count += 1

wine6 = Wine(wine_maker = "Jacobs Creek", wine_vintage = 2015, wine_varietal = "Cabernet Sauvignon",
	         wine_price = 1300, wine_id = 17, loc_id = 6, wine = location6, user_id = 1)
session.add(wine6)
session.commit()
print(count, " wine added!")
count += 1

##############################################################################

location7 = Catalog(location_id = 7, location_name = "Chile", user_id = 1)
session.add(location7)
session.commit()
print("Location 7 Added!")

wine7 = Wine(wine_maker = "Como Sur", wine_vintage = 2015, wine_varietal = "Pinot Noir",
	         wine_price = 1290, wine_id = 18, loc_id = 7, wine = location7, user_id = 1)
session.add(wine7)
session.commit()
print(count, " wine added!")
count += 1

##############################################################################

location8 = Catalog(location_id = 8, location_name = "India", user_id = 1)
session.add(location8)
session.commit()
print("Location 8 Added!")

wine8 = Wine(wine_maker = "Grover", wine_vintage = 2012, wine_varietal = "Cabernet Sauvignon",
	         wine_price = 1160, wine_id = 19, loc_id = 8, wine = location8, user_id = 1)
session.add(wine8)
session.commit()
print(count, " wine added!")
count += 1

wine8 = Wine(wine_maker = "Fratelli", wine_vintage = 2013, wine_varietal = "Viognier",
	         wine_price = 990, wine_id = 20, loc_id = 8, wine = location8, user_id = 1)
session.add(wine8)
session.commit()
print(count, " wine added!")
count += 1

wine8 = Wine(wine_maker = "Grover", wine_vintage = 2013, wine_varietal = "Cabernet Shiraz",
	         wine_price = 990, wine_id = 21, loc_id = 8, wine = location8, user_id = 1)
session.add(wine8)
session.commit()
print(count, " wine added!")
count += 1

wine8 = Wine(wine_maker = "Big Banyan", wine_vintage = 2014, wine_varietal = "Chardnnay",
	         wine_price = 1100, wine_id = 22, loc_id = 8, wine = location8, user_id = 1)
session.add(wine8)
session.commit()
print(count, " wine added!")
count += 1

wine8 = Wine(wine_maker = "Charosa", wine_vintage = 2012, wine_varietal = "Tampranillo",
	         wine_price = 1200, wine_id = 23, loc_id = 8, wine = location8, user_id = 1)
session.add(wine8)
session.commit()
print(count, " wine added!")
count += 1

wine8 = Wine(wine_maker = "Fratelli", wine_vintage = 2013, wine_varietal = "Syrah Rose",
	         wine_price = 990, wine_id = 24, loc_id = 8, wine = location8, user_id = 1)
session.add(wine8)
session.commit()
print(count, " wine added!")
count += 1

wine8 = Wine(wine_maker = "Nine Hills", wine_vintage = 2009, wine_varietal = "Shiraz",
	         wine_price = 900, wine_id = 25, loc_id = 8, wine = location8, user_id = 1)
session.add(wine8)
session.commit()
print(count, " wine added!")
count += 1

wine8 = Wine(wine_maker = "Grover", wine_vintage = 2013, wine_varietal = "Savignon Blanc",
	         wine_price = 1100, wine_id = 26, loc_id = 8, wine = location8, user_id = 1)
session.add(wine8)
session.commit()
print(count, " wine added!")
count += 1

wine8 = Wine(wine_maker = "Sula", wine_vintage = 2012, wine_varietal = "Chenin Blanc",
	         wine_price = 600, wine_id = 27, loc_id = 8, wine = location8, user_id = 1)
session.add(wine8)
session.commit()
print(count, " wine added!")
count += 1

wine8 = Wine(wine_maker = "Sula", wine_vintage = 20014, wine_varietal = "Shiraz",
	         wine_price = 700, wine_id = 28, loc_id = 8, wine = location8, user_id = 1)
session.add(wine8)
session.commit()
print(count, " wine added!")
count += 1

##############################################################################

location9 = Catalog(location_id = 9, location_name = "Portugal", user_id = 1)
session.add(location9)
session.commit()
print("Location 9 Added!")

wine9 = Wine(wine_maker = "Adega Mayor", wine_vintage = 2001, wine_varietal = "Tempranillo Port",
	         wine_price = 2200, wine_id = 29, loc_id = 9, wine = location9, user_id = 1)
session.add(wine9)
session.commit()
print(count, " wine added!")
count += 1

##############################################################################

location10 = Catalog(location_id = 10, location_name = "Spain", user_id = 1)
session.add(location10)
session.commit()
print("Location 10 Added!")

wine10 = Wine(wine_maker = "Bodegas Beronia Rioja Reserva", wine_vintage = 2010, wine_varietal = "Tempranillo",
	         wine_price = 3400, wine_id = 30, loc_id = 10, wine = location10, user_id = 1)
session.add(wine10)
session.commit()
print(count, " wine added!")
count += 1

wine10 = Wine(wine_maker = "Zerran Tinto", wine_vintage = 2009, wine_varietal = "Granacha",
	         wine_price = 5000, wine_id = 31, loc_id = 10, wine = location10, user_id = 1)
session.add(wine10)
session.commit()
print(count, " wine added!")
count += 1


print(count, "number of wines added!")
##############################################################################