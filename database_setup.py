#used while writing the mapper code of ORM
from sqlalchemy import Column, ForeignKey, Integer, String
# Used for configuration and class code
from sqlalchemy.ext.declarative import declarative_base
#used to create our foreign ey relationships
from sqlalchemy.orm  import relationship
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import create_engine
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

# Create an instance of declarative base that we will use
# to correspond to databases across the project
Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits)for x in range(32))


# Stores each location along with an ID
class Catalog(Base):
    __tablename__ = 'catalog'
    location_id = Column(Integer, primary_key = True)
    location_name = Column(String(250), nullable = False)

    # For JSON API retrieval
    @property 
    def ser(self):
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
    wine = relationship(Catalog)

    @property
    def serialize(self):
        return {
            'make' : self.wine_maker,
            'varietal' : self.wine_varietal,
            'vintage' : self.wine_vintage,
            'price' : self.wine_price,
        }


# Stores each user along with their password hashes
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key = True)
    user_name = Column(String(20), index = True)
    pswd_hash = Column(String(500))

    def hash(self, pwd):
        self.password_hash = pwd_context.encrypt(pwd)

    def verify(self, pwd):
        self.password_hash = pwd_context.encrypt(pwd)
        return pwd_context.verify(pwd, self.password_hash)

    def generate_auth_token(self, expiration = 600):
        s = Serializer(secret_key, expires_in = expiration)
        return s.dumps({'id':self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)

        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None

        user_id = data['id']
        return user_id

# To go at end of file
# Create a new engine and point to the data base that we will use
engine = create_engine('sqlite:///wineCatalog.db')
Base.metadata.create_all(engine)
