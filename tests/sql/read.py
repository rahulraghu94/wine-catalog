from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Wine, WineDetails

engine = create_engine('sqlite:///wineCatalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

items = session.query(Wine).all()

for item in items:
    print (item.name)
