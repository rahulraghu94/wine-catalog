from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Wine, Base, WineDetails

def populate():
    # Menu for UrbanBurger
    wine1 = Wine(id = 1, name="Gato Negro Sauvignon Blanc")
    session.add(wine1)
    session.commit()
    wineDetails1 = WineDetails(name="Sauvignon Blanc", vintage = 2012,
                         price="950", id = 1, wine=wine1)
    session.add(wineDetails1)
    session.commit()
    print("Wine 1 added!")

    # Menu for Super Stir Fry
    wine1 = Wine(name="Rombaurt Zinfandel", id = 2)
    session.add(wine1)
    session.commit()
    wineDetails1 = WineDetails(name="Zinfandel", vintage = 2012,
                         price="950", id = 2, wine=wine1)
    session.add(wineDetails1)
    session.commit()
    print("Wine 2 added!")

    # Menu for Panda Garden
    wine1 = Wine(name="Tar&Roses Shiraz Rose", id = 3)
    session.add(wine1)
    session.commit()
    wineDetails1 = WineDetails(name="Shiraz", vintage = 2012,
                         price="950", id = 3, wine=wine1)                                                                                                                            
    session.add(wineDetails1)
    session.commit()
    print("Wine 3 added!")

    # Menu for Thyme for that
    wine1 = Wine(name="Sula Merlot", id = 4)
    session.add(wine1)
    session.commit()
    wineDetails1 = WineDetails(name="Merlot", vintage = 2012,
                         price="950", id = 4, wine=wine1)
    session.add(wineDetails1)
    session.commit()
    print("Wine 4 added!")

    # Menu for Tony's Bistro
    wine1 = Wine(name="Mosaic Grenache Syrah Blend", id = 5)
    session.add(wine1)
    session.commit()
    wineDetails1 = WineDetails(name="Grenache Syrah", vintage = 2012,
                         price="950", id = 5, wine=wine1)
    session.add(wineDetails1)
    session.commit()
    print("Wine 5 added!")

    # Menu for Andala's
    wine1 = Wine(name="Big Banyan Chardonay", id = 6)
    session.add(wine1)
    session.commit()
    wineDetails1 = WineDetails(name="Chanrdonay", vintage = 2012,
                         price="950", id = 6, wine=wine1)
    session.add(wineDetails1)
    session.commit()
    print("Wine 6 added!")

    # Menu for Auntie Ann's
    wine1 = Wine(name="Fratelli Merlot", id = 7)
    session.add(wine1)
    session.commit()
    wineDetails9 = WineDetails(name="Merlot", vintage = 2012,
                         price="950", id = 7, wine=wine1)
    session.add(wineDetails9)
    session.commit()
    print("Wine 7 added!")

    # Menu for Cocina Y Amor
    wine1 = Wine(name="Grover Zampa Cabernet Franc", id = 8)
    session.add(wine1)
    session.commit()
    wineDetails1 = WineDetails(name="Cabernet Franc", vintage = 2012,
                         price="950", id = 8, wine=wine1)
    session.add(wineDetails1)
    session.commit()
    print("Wine 8 added!")


    print ("Added arbitrary menu items!")



class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/list"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                items = session.query(Wine).all()
                output = ""
                for item in items:
                        output += (item.name)

                self.wfile.write(output.encode(encoding = 'utf_8'))
                return

        except Exception e:
                print (e)

    def do_POST(self):
        try:
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            ctype, pdict = cgi.parse_header(
                self.headers.get('content-type'))
            
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')
            
            output = b""
            output += b"<html><body>"
            output += b" <h2> Okay, how about this: </h2>"
            output += b"<h1> </h1>" 
            output += messagecontent[0]
            output += b'''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
            output += b"</body></html>"
            
            self.wfile.write(output)

        except Exception as e:
            print (e)


def main():
    try:
        engine = create_engine('sqlite:///wineCatalog.db')
        print("Engine created")
        Base.metadata.bind = engine
        print("Engine bound")
        DBSession = sessionmaker(bind=engine)
        # A DBSession() instance establishes all conversations with the database
        # and represents a "staging zone" for all the objects loaded into the
        # database session object. Any change made against the objects in the
        # session won't be persisted into the database until you call
        # session.commit(). If you're not happy about the changes, you can
        # revert all of them back to the last commit by calling
        # session.rollback()
        session = DBSession()
        print("Started a new session")
        populate()
        print("Populate called")

        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print ("Web Server running on port ", port)
        server.serve_forever()
    except KeyboardInterrupt:
        print (" ^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    main()
