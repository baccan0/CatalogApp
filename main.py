from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, Item, User
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import random 
import string
import requests


engine = create_engine('sqlite:///catlog.db')
Base.metadata.bind = engine

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/gdisconnect',methods = ['GET'])
def g_disconnect_page():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(render_template("error.html", code =401, message = "user not log in"), 401)
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials.access_token
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['picture']
        del login_session['email']
        del login_session['username']
        flash("you have logout!")
        return redirect(url_for("login_page"))
    else:
        response = make_response(render_template("error.html", code =400, message = "cannot revoke token"),400)
        return response

@app.route('/gconnect', methods = ['POST'])
def g_connect_page():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope = "")
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    print "*"
    access_token =credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token) 
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID"), 500)
        response.headers['Content-type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps('Token client ID does not match app'), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        login_session['credentials'] = credentials
        response = make_response(json.dumps('Current user is already connected.', 200))
        response.headers['Content-type'] = 'application/json'
        return response
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token':credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url,params = params)
    data = answer.json()
    login_session['provider'] = 'gplus'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    user_id = getUserID(login_session['email'])
    if user_id is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 150px; height: 150px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/login')
def login_page():
    state = "".join([random.choice(string.ascii_uppercase + string.digits) for i in range(0,32)])
    login_session['state'] = state
    return render_template("login.html", state = state, login_session = login_session)

@app.route('/logout')
def logout_page():
    if login_session['credentials']:
        if login_session['provider'] == 'gplus':
            return redirect(url_for('g_disconnect_page'))
    else:
         return redirect(url_for('login_page'))  

@app.route('/catalog/<int:catalog_id>/json')
def catalog_page_json(catalog_id):
    item = session.query(Item).filter_by(catalog_id = catalog_id).all()
    return jsonify(Items = [i.serialize for i in item])    

@app.route('/catalog/json')
def cover_page_json():
    catalog = session.query(Catalog).all()
    return jsonify(catalog = [c.serialize for c in catalog])

@app.route('/item/<int:item_id>/json')
def item_page_json(item_id):
    item = session.query(Item).filter_by(id = item_id).one()
    return jsonify(Item = item.serialize)

@app.route('/')
@app.route('/catalog/')
def cover_page():
    catalog = session.query(Catalog).all()
    lastest = session.query(Item).order_by(Item.last_edit.desc()).limit(10).all()
    return render_template("catalog.html", catalog = catalog, item = lastest, login_session = login_session, cat = None)

@app.route('/catalog/new', methods = ['POST'])
def new_catalog_page():
    if 'username' not in login_session:
        return redirect(url_for('login_page'))
    if request.method == 'POST':
        new_catalog = Catalog(name = request.form['name'], user = getUserInfo(login_session['user_id']))
        session.add(new_catalog)
        flash('New Catalog %s sucessfully created' % new_catalog.name)
        session.commit()
        catalog_id = session.query(Catalog).filter_by(name = request.form['name']).one().id
        
        return redirect(url_for("catalog_page", catalog_id = catalog_id))

@app.route('/catalog/<int:catalog_id>')
def catalog_page(catalog_id):
    try:
        catalog = session.query(Catalog).all()
        cat = session.query(Catalog).filter_by(id = catalog_id).one()
        item = session.query(Item).filter_by(catalog_id = cat.id).all()
        return render_template("catalog.html",catalog = catalog, item = item, login_session = login_session, cat = cat)
    except:
        return make_response(render_template("error.html", code =404, message = "file not found"), 404)

@app.route('/catalog/<int:catalog_id>/edit',methods=['POST'])
def catalog_edit_page(catalog_id):
    if 'username' not in login_session:
        return redirect(url_for('login_page'))
    if request.method == "POST":
        selected_catalog = session.query(Catalog).filter_by(id = catalog_id).one()
        if login_session['user_id'] != selected_catalog.user_id:
            return make_response(render_template("error.html", code =401, message = "you don't have authorization to make this change"), 401)
        selected_catalog.name = request.form['name']
        session.add(selected_catalog)
        flash('Catalog %s sucessfully updated' % selected_catalog.name)
        session.commit()
        return redirect(url_for("catalog_page", catalog_id = catalog_id))

@app.route('/catalog/<int:catalog_id>/delete',methods=['POST'])
def catalog_delete_page(catalog_id):
    if 'username' not in login_session:
        return redirect(url_for('login_page'))
    if request.method == "POST":
        selected_catalog = session.query(Catalog).filter_by(id = catalog_id).one()
        if login_session['user_id'] != selected_catalog.user_id:
            return make_response(render_template("error.html", code =401, message = "you don't have authorization to make this change"), 401)
        session.delete(selected_catalog)
        flash('Catalog %s sucessfully deleted' % selected_catalog.name)
        session.commit()
        return redirect(url_for("cover_page"))
 
@app.route('/item/<int:item_id>')
def item_page(item_id):
    try:
        item = session.query(Item).filter_by(id = item_id).one()
        return render_template("item.html", item = item, login_session = login_session)
    except:
        return make_response(render_template("error.html", code =404, message = "file not found"), 404)

@app.route('/item/<int:catalog_id>/new', methods=['POST'])
def item_new_page(catalog_id):
    if 'username' not in login_session:
        return redirect(url_for('login_page'))
    if request.method == 'POST':
        cat = session.query(Catalog).filter_by(id = catalog_id).one()
        new_item = Item(name = request.form['name'], catalog = cat, user = getUserInfo(login_session['user_id']))
        if request.form['picture']:
            new_item.picture = request.form['picture']
        if request.form['description']:
            new_item.description = request.form['description']
        session.add(new_item)
        flash('New Item %s sucessfully created' % new_item.name)
        session.commit()
        item = session.query(Item).filter_by(catalog_id = catalog_id, name = request.form['name'] ).one()
        return redirect(url_for("item_page", item_id = item.id))

@app.route('/item/<int:item_id>/edit', methods=['POST'])
def item_edit_page(item_id):
    if 'username' not in login_session:
        return redirect(url_for('login_page'))
    if request.method == "POST":
        selected_item = session.query(Item).filter_by(id = item_id).one()
        if login_session['user_id'] != selected_item.user_id:
            return make_response(render_template("error.html", code =401, message = "you don't have authorization to make this change"), 401)
        if request.form['name']:
            selected_item.name = request.form['name']
        if request.form['picture']:
            selected_item.picture = request.form['picture']
        if request.form['description']:
            selected_item.description = request.form['description']
        session.add(selected_item)
        flash(' Item %s sucessfully updated' % selected_item.name)
        session.commit()
        return redirect(url_for("item_page", item_id = selected_item.id))

@app.route('/item/<int:item_id>/delete', methods=['POST'])
def item_delete_page(item_id):
    if 'username' not in login_session:
        return redirect(url_for('login_page'))
    if request.method == "POST":
        selected_item = session.query(Item).filter_by(id = item_id).one()
        if login_session['user_id'] != selected_item.user_id:
            return make_response(render_template("error.html", code =401, message = "you don't have authorization to make this change"), 401)
        session.delete(selected_item)
        flash('Item %s sucessfully deleted' % selected_item.name)
        session.commit()
        return redirect(url_for("cover_page"))

def createUser(login_session):
    newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user

def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 8000)
