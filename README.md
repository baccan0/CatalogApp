Catagory app

- This is a web page based application for managing a catagory-item system, which uses flask-sqlalchemy framework.

1. Quick Start:
   a) install with python 2.7.x
   b) install with Flask-sqlalchemy(version 0.9)
   c) install with oauth2client package
   c) clone the CatalogApp folder
   d) setup the database by running >python database_setup.py
   e) add some instances into the database
      optional: >python populate.py
   f) run the server end > python main.py
   g) open http://localhost:8000 in your browser


2. what's included

CatalogApp
|-static/
| |-github-logo.png
| |-plus.png
| |-question.png
| |-style.css
|-templates/
| |-catalog.html
| |-error.html
| |-icon_copyright.html
| |-item.html
| |-login.html
| |-main.html
| |-nav.html
|-client_secrets.json
|-database_setup.py
|-main.py
|-populate.py

we provide the template files and basic resources for running the application.
If necessary, you can change the client_secrets.json into your own's. You can also
restylize the application with ./static/style.css.

3. Endpoint APIs:
   
   GET '/' or '/catalog':
     -return catagories and latest 10 items
   GET '/catalog/json':
     -return a json listing all the catalogies
   GET '/login':
     -direct the user to a login page providing gplus and github oauth 
      login
   GET '/logout':
     -let the user logout according to login method and redirect to 
      the '/login'
   GET '/catalog/:catalog_id':
     -return catagories and the items in the catagory having id equal 
      to catalog_id
   POST '/catalog/new':
     -create catagory called request.form['name'] and redirect 
      to '/catalog/:new_catalog_id'
   POST '/catalog/:catlog_id/edit':
     -change the catagory's name into request.form['name'] and redirect 
      to '/catalog/:catalog_id'
   POST '/catalog/:catlog_id/edit':
     -delete the catagory and redirect to '/catalog/'
   GET '/catalog/:catalog_id/json'
     -return a json listing all the details of all catagories
   GET '/item/:item_id':
     -return the page displaying an item
   POST '/item/:catalog_id/new':
     -create an item in the catagory whose id is equal to catalog_id 
      and redirect to '/item/:new_item_id'
   POST '/item/:item_id/edit':
     -change the item's name/picture/description into request.form['name']
      /request.form['picture']/request.form['description'] and redirect 
      to '/item/:item_id'
   POST '/catalog/:catlog_id/edit':
     delete the item and redirect to '/catalog/'
   GET '/catalog/:item_id/json'
     return a json listing the property of the item

