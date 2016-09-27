import pg

db = pg.DB(dbname = "wine-databse")

# Create the tables in the Database
# Create a User table
db.query("create table users(id serial primary key, name varchar(250), email varchar(250), picture varchar (250))")

# Create a Catalog Table
db.query("create table catalog(location_id serial primary key, location_name varchar(60), user_id integer references users(id) on delete cascade on update cascade)")

# Create a Wine Table
db.query("create table wine(wine_id serial primary key, wine_maker varchar(60), wine_varietal varchar(60), wine_vintage integer, wine_price integer, loc_id integer references catalog(location_id) on delete cascade on update cascade, user_id integer references users(id) on delete cascade on update cascade)")