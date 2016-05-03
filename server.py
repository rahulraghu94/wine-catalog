from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Wine, Base, WineDetails

engine = create_engine('sqlite:///wineCatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)       
session = DBSession()

#global count 

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
                                output += "<h1> <i> Your Wines </i></h1> <br>"
                                output += "<h5 align='right'> <a href = '/list/new'> Add a New Wine </a> </h5>"
                                
                                for item in items:
                                        #count += 1decode
                                        output += str(item.name)
                                        output += "<br>"
                                        output += "<a href = /"
                                        output += str(item.id)
                                        output += "/edit> Edit </a>"
                                        output += "<br>"
                                        output += "<a href = /"
                                        output += str(item.id)
                                        output += "/delete> Delete </a>"
                                        output += "<br> <hr>"

                                self.wfile.write(output.encode(encoding = 'utf_8'))
                                #print(count)
                                return

                        if self.path.endswith("list/new"):
                                self.send_response(200)
                                self.send_header('Content-type', 'text/html')
                                self.end_headers()
                                
                                output = ""
                                output += '''<form method='POST' enctype='multipart/form-data' action='/list/new'>'''
                                output += '''<h2> Varietal </h2><input name="maker" type="text" >'''
                                output += '''<input type="submit" value="Submit"> </form>'''
                                output += ""

                                self.wfile.write(output.encode(encoding = 'utf_8'))
                                return 

                        if self.path.endswith("/edit"):
                                print("edit entered")
                                IDPath = self.path.split("/")[1]
                                print(IDPath)
                                wineName = session.query(Wine).filter_by(id=IDPath).one()
                
                                if wineName:
                                        self.send_response(200)
                                        self.send_header('Content-type', 'text/html')
                                        self.end_headers()
                                        output = "<html><body>"
                                        output += "<h1>"
                                        output += "Edit " 
                                        output += str(wineName.name)
                                        output += " ?</h1>"
                                        output += "<form method='POST' enctype='multipart/form-data' action = '/list/"
                                        output += IDPath
                                        output += "/edit' >" 
                                        output += "<input name = 'wineName' type='text' placeholder =" 
                                        output += str(wineName.name) 
                                        output += ">" 
                                        output += "<input type = 'submit' value = 'Rename'>"
                                        output += "</form>"
                                        output += "</body></html>"

                                        self.wfile.write(output.encode(encoding = 'utf_8'))
                                        return

                        if self.path.endswith("/delete"):
                                print("delete entered")
                                IDPath = self.path.split("/")[1]
                                print(IDPath)
                                wineName = session.query(Wine).filter_by(id=IDPath).one()
                                if wineName:
                                        self.send_response(200)
                                        self.send_header('Content-type', 'text/html')
                                        self.end_headers()
                                        output = ""
                                        output += "<html><body>"
                                        output += "<h1>Are you sure you want to delete "
                                        output += str(wineName.name)
                                        output += "?"
                                        output += "<form method='POST' enctype = 'multipart/form-data' action = '/restaurants/"
                                        output += IDPath 
                                        output += "/delete'>" 
                                        output += "<input type = 'submit' value = 'Delete'>"
                                        output += "</form>"
                                        output += "</body></html>"
                                        self.wfile.write(output.encode(encoding = 'utf_8'))

                except:
                        traceback.print_exc()

        def do_POST(self):
                count = 1
                items = session.query(Wine).all()
                for item in items:
                        count += 1

                try:
                        if self.path.endswith("/delete"):
                                IDPath = self.path.split("/")[2]
                                wineName = session.query(Wine).filter_by(id=IDPath).one()
                                if wineName:
                                        session.delete(wineName)
                                        session.commit()
                                        self.send_response(301)
                                        self.send_header('Content-type', 'text/html')
                                        self.send_header('Location', '/list')
                                        self.end_headers()

                        if self.path.endswith("/edit"):
                                ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
                                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                                if ctype == 'multipart/form-data':
                                        fields = cgi.parse_multipart(self.rfile, pdict)
                                        messagecontent = fields.get('wineName')
                                        print(messagecontent[0])
                                        IDPath = self.path.split("/")[2]

                                        wineQuery = session.query(Wine).filter_by(id=IDPath).one()
                    
                                        if wineQuery != []:
                                                wineQuery.name = messagecontent[0].decode("utf-8")
                                                session.add(wineQuery)
                                                session.commit()
                                                
                                                self.send_response(301)
                                                self.send_header('Content-type', 'text/html')
                                                self.send_header('Location', '/list')
                                                self.end_headers()
                        
                        if self.path.endswith("/list/new"):
                                print("if enteres")
                                ctype, pdict = cgi.parse_header(
                                self.headers.get('content-type'))
                            
                                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                                if ctype == 'multipart/form-data':
                                        fields = cgi.parse_multipart(self.rfile, pdict)
                                        maker = fields.get('maker')
                            
                                print(maker)

                                wine1 = Wine(id = count, name=maker[0].decode("utf-8"))
                                session.add(wine1)
                                session.commit()
                            
                                self.send_response(301)
                                self.send_header('Content-type', 'text/html')
                                self.send_header('Location', '/list')
                                self.end_headers()

                except Exception as e:
                        print (e)

def hello():
        print("hello!")

def main():
    try:
        port = 8080
        hello()
        #populate()
        server = HTTPServer(('', port), webServerHandler)
        print ("Web Server running on port ", port)
        server.serve_forever()
    except KeyboardInterrupt:
        print (" ^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    main()
