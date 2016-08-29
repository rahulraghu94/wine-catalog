#used while writing the mapper code of ORM
from sqlalchemy import Column, ForeignKey, Integer, String
# Used for configuration and class code
from sqlalchemy.ext.declarative import declarative_base
#used to create our foreign ey relationships
from sqlalchemy.orm  import relationship
#from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import create_engine
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask import session as login_session
import random, string

# Create an instance of declarative base that we will use
# to correspond to databases across the project
Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)for x in range(32))


#Stores all the users
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    email = Column(String(100), nullable = False)
    picture = Column(String(250), nullable = False)


# Stores each location along with an ID
class Catalog(Base):
    __tablename__ = 'catalog'
    location_id = Column(Integer, primary_key = True)
    location_name = Column(String(250), nullable = False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # For JSON API retrieval
    @property
    def serialize(self):
        return {
            'id' : self.location_id,
            'name' : self.location_name,
        }


# Stores wines in sequnce based on their location ID
class Wine(Base):
    __tablename__ = 'wine'
    wine_maker = Column(String(250), nullable = False)
    wine_vintage = Column(Integer, nullable = False)
    wine_varietal = Column(String(250), nullable = False)
    wine_price = Column(Integer, nullable = False)
    wine_id = Column(Integer, primary_key = True)
    loc_id = Column(Integer, ForeignKey('catalog.location_id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    wine = relationship(Catalog)

    @property
    def serialize(self):
        return {
            'make' : self.wine_maker,
            'varietal' : self.wine_varietal,
            'vintage' : self.wine_vintage,
            'price' : self.wine_price,
        }

# To go at end of file
# Create a new engine and point to the data base that we will use
engine = create_engine('sqlite:///wineCatalog.db')
Base.metadata.create_all(engine)
