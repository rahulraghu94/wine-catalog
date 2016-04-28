from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Wine, Base, WineDetails

engine = create_engine('sqlite:///wineCatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
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








# Menu for UrbanBurger
wine1 = Wine(id = 1, name="Gato Negro Sauvignon Blanc")

session.add(wine1)
session.commit()


wineDetails1 = WineDetails(name="Sauvignon Blanc", vintage = 2012,
                     price="950", id = 1, wine=wine1)

session.add(wineDetails1)
session.commit()









# Menu for Super Stir Fry
wine1 = Wine(name="Rombaurt Zinfandel", id = 2)

session.add(wine1)
session.commit()


wineDetails1 = WineDetails(name="Zinfandel", vintage = 2012,
                     price="950", id = 2, wine=wine1)

session.add(wineDetails1)
session.commit()








# Menu for Panda Garden
wine1 = Wine(name="Tar&Roses Shiraz Rose", id = 3)

session.add(wine1)
session.commit()


wineDetails1 = WineDetails(name="Shiraz", vintage = 2012,
                     price="950", id = 3, wine=wine1)                                                                                                                            

session.add(wineDetails1)
session.commit()










# Menu for Thyme for that
wine1 = Wine(name="Sula Merlot", id = 4)

session.add(wine1)
session.commit()


wineDetails1 = WineDetails(name="Merlot", vintage = 2012,
                     price="950", id = 4, wine=wine1)

session.add(wineDetails1)
session.commit()










# Menu for Tony's Bistro
wine1 = Wine(name="Mosaic Grenache Syrah Blend", id = 5)

session.add(wine1)
session.commit()


wineDetails1 = WineDetails(name="Grenache Syrah", vintage = 2012,
                     price="950", id = 5, wine=wine1)

session.add(wineDetails1)
session.commit()









# Menu for Andala's
wine1 = Wine(name="Big Banyan Chardonay", id = 6)

session.add(wine1)
session.commit()


wineDetails1 = WineDetails(name="Chanrdonay", vintage = 2012,
                     price="950", id = 6, wine=wine1)

session.add(wineDetails1)
session.commit()










# Menu for Auntie Ann's
wine1 = Wine(name="Fratelli Merlot", id = 7)

session.add(wine1)
session.commit()

wineDetails9 = WineDetails(name="Merlot", vintage = 2012,
                     price="950", id = 7, wine=wine1)

session.add(wineDetails9)
session.commit()










# Menu for Cocina Y Amor
wine1 = Wine(name="Grover Zampa Cabernet Franc", id = 8)

session.add(wine1)
session.commit()


wineDetails1 = WineDetails(name="Cabernet Franc", vintage = 2012,
                     price="950", id = 8, wine=wine1)

session.add(wineDetails1)
session.commit()


print ("added menu items!")
