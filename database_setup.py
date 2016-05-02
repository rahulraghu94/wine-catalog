#used while writing the mapper code of ORM
from sqlalchemy import Column, ForeignKey, Integer, String

# Used for configuration and class code
from sqlalchemy.ext.declarative import declarative_base

#used to create our foreign ey relationships
from sqlalchemy.orm  import relationship

from sqlalchemy import create_engine

# Create an instance of declarative base that we will use
# to correspond to databases across the project
Base = declarative_base()

class Wine(Base):
    __tablename__ = 'wine'
    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)

class WineDetails(Base):
    __tablename__ = 'wine_details'
    name = Column(String(250), nullable = False)
    vintage = Column(Integer, nullable = False)
    terroir = Column(String(250))
    price = Column(Integer, nullable = False)
    notes = Column(String(1024))
    pair = Column(String(1024))
    id = Column(Integer, primary_key = True)
    wine_id = Column(Integer, ForeignKey('wine.id'))
    wine = relationship(Wine)

# To go at end of file
# Create a new engine and point to the data base that we will use
engine = create_engine('sqlite:///wineCatalog.db')
Base.metadata.create_all(engine)
