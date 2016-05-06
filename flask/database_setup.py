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

class Catalog(Base):
    __tablename__ = 'catalog'
    location_id = Column(Integer, primary_key = True)
    location_name = Column(String(250), nullable = False)

class Wine(Base):
    __tablename__ = 'wine'
    wine_maker = Column(String(250), nullable = False)
    wine_vintage = Column(Integer, nullable = False)
    wine_varietal = Column(String(250), nullable = False)
    wine_price = Column(Integer, nullable = False)
    wine_id = Column(Integer, primary_key = True)
    loc_id = Column(Integer, ForeignKey('catalog.location_id'))
    wine = relationship(Catalog)

# To go at end of file
# Create a new engine and point to the data base that we will use
engine = create_engine('sqlite:///wineCatalog.db')
Base.metadata.create_all(engine)
