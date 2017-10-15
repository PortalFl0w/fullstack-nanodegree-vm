from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
import sys
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# import our tables from database_setup module
from database_setup import Restaurant, Base, MenuItem

engine = create_engine(
'sqlite:///restaurantmenu.db')

Base.metadata.bind = engine

# session instance
DBSession = sessionmaker(bind=engine)

# store session globally
session = DBSession()

# test print
# print session.query(Restaurant).all()

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                # headers
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # query a list of all restaurants - returns array
                res = session.query(Restaurant).all()

                # output
                output = ""

                output += "<html><body><a href='/restaurants/new'>Add New Restaurant</a>"

                output += "<ul>"

                # loop through array of restaurants
                for restaurant in res:
                    output += "<li>"
                    output += restaurant.name
                    output += " <a href='restaurants/%s/edit'>Edit</a> <a href='restaurants/%s/delete'>Delete</a>" % (restaurant.id, restaurant.id)
                    output += "</li>"

                output += "</ul></html></body>"

                # write output
                self.wfile.write(output)
                return

            if self.path.endswith("/restaurants/new"):
                # headers
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # output
                output = ""
                output += "<form action='/restaurants/new/submit' enctype='multipart/form-data' method='POST'><label for='Name'>Name of the restaurant:</label><input type='text' name='Name'><input type='submit' value='Submit'></form>"

                # write output
                self.wfile.write(output)
                return
            if self.path.endswith("/edit"):
                # headers
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # split url and find the ID string
                editId = self.path.split("/")[2]

                # query for a restaurant with matching ID
                restaurant = session.query(Restaurant).filter_by(id=editId).one()


                # check if restaurant exists and is not array
                if restaurant != []:

                    # output
                    output = "<h1>Edit %s</h1>" % restaurant.name
                    output += "<form action='/restaurants/edit/submit' enctype='multipart/form-data' method='POST'><label for='Name'> Name of the restaurant: </label><input type='number' value='%s' name='id' hidden><input type='text' name='Name'><input type='submit' value='Submit'></form>" % restaurant.id

                    # write output
                    self.wfile.write(output)

                return

            if self.path.endswith("/delete"):
                # headers
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # split url
                deleteId = self.path.split("/")[2]

                # find restaurant with matching ID
                restaurant = session.query(Restaurant).filter_by(id=deleteId).one()

                # check if restaurant exists and is not array
                if restaurant != []:

                    # output
                    output = "<h1>Do you want to delete %s?</h1>" % restaurant.name
                    output += "<form action='/restaurants/delete/submit' enctype='multipart/form-data' method='POST'><input type='number' value='%s' name='id' hidden><input type='submit' value='Delete'></form>" % restaurant.id

                    # write output
                    self.wfile.write(output)

                return

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new/submit"):
                # get content type
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('Name')

                # new Restaurant object
                new_restaurant = Restaurant(name=messagecontent[0])

                # add restaurant to session
                session.add(new_restaurant)

                # commit restaurant to database
                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')

                # New Path Location Header
                new_path = '%s%s' % ('http://localhost:8080', "/restaurants")
                self.send_header('Location', new_path)

                self.end_headers()

                return
            if self.path.endswith("/restaurants/edit/submit"):
                # get content type
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    name = fields.get('Name')
                    id = fields.get('id')

                # Get a single restaurant with the matching UNIQUE id
                restaurant = session.query(Restaurant).filter_by(id=id[0]).one()

                # If something was found by restaurant query
                if restaurant != []:
                    restaurant.name = name[0] # change name of the query to name from the form
                    session.commit() # commit session

                    # upon success send headers and redirect
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')

                    # New Path Location Header
                    new_path = '%s%s' % ('http://localhost:8080', "/restaurants")
                    self.send_header('Location', new_path)

                    self.end_headers()

                return
            if self.path.endswith("/restaurants/delete/submit"):
                # get content type
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    id = fields.get('id')

                # Get a single restaurant with the matching UNIQUE id
                restaurant = session.query(Restaurant).filter_by(id=id[0]).one()

                session.delete(restaurant)

                session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')

                # New Path Location Header
                new_path = '%s%s' % ('http://localhost:8080', "/restaurants")
                self.send_header('Location', new_path)

                self.end_headers()

                return

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('',port), webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()
