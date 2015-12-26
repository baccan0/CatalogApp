from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, Item, User
from sqlalchemy.sql.functions import now
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import random 
import string
import requests
from requests.auth import HTTPBasicAuth

# connect to the database and establish a DBSession() instance functioning as a 'staging zone'
engine = create_engine('sqlite:///catlog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# load google client id and secrets.
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

# load github client id and secrets.
GIT_CLIENT_ID = '753c780d867642d342c3'
GIT_CLIENT_SECRET = 'a19fe519bed14ae275fdf5e35d8252036d100458'

def login_required(func):
    def wraper(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('login_page'))
        return func(*args, **kwargs)
    return wraper

# login using github.
@app.route('/gitconnect')
def git_connect_page():
    # check 'state' to prevent cross-site request forgery attacks.
    if request.args.get('state') != login_session['state']:
        response = make_response(render_template("error.html", code = 401, message = 'Invalid state parameter.'), 401)
        return response
    # use the returned authorization code to exchange the access token
    c = request.args.get('code')
    if not c:
        response = make_response(render_template("error.html", code = 401, message = 'fetch code error.'), 401)
        return response
    url = ('https://github.com/login/oauth/access_token?client_id=%s&client_secret=%s&code=%s' % (GIT_CLIENT_ID, GIT_CLIENT_SECRET, c)) 
    token_answer = json.loads(requests.get(url, headers = {'Accept': 'application/json'}).content)
    if token_answer.get('error') or not token_answer.get('access_token'):
        response = make_response(render_template("error.html", code = 401, message = "fail to fetch access token"), 401)
        return response
    # use the token to fetch personal info.
    token = token_answer.get('access_token')
    url = ('https://api.github.com/user/emails?access_token=%s' % token)
    email_request = requests.get(url)
    if email_request.status_code != 200:
        return make_response(render_template("error.html", email_request.status_code, message = "fail to get user info"), email_request.status_code)
    userinfo = json.loads(email_request.content)
    login_session['provider'] = 'github'
    login_session['token'] = token
    login_session['email'] = userinfo[0]['email']
    url = ('https://api.github.com/user?access_token=%s' % token)
    user_request = requests.get(url)
    login_session['username'] = json.loads(user_request.content)['login']
    login_session['picture'] = None
    
    # try to find the user in database, users are distinguished by user email.
    user_id = getUserID(login_session['email'])
    if user_id is None:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    flash("You have login as %s" % login_session['username'])
    # return a welcome page which will redirect to cover_page in 1 sec
    response = make_response('<html><head><meta charset="UTF-8"><script>function callback(){setTimeout(function(){window.location.href = "/";}, 1000);}</script></head><body onload="callback()"><h2>welcome, %s</h2></body></html>' % login_session['username'], 200)
    response.headers['Content-type'] = 'text/html'
    return response

# github account logout
@app.route('/gitdisconnect')
def git_disconnect_page():
    token = login_session.get('token') 
    if token is None:
        response = make_response(render_template("error.html", code =401, message = "user not log in"), 401)
        return response
    # revoke the token.
    url = ('https://api.github.com/applications/%s/tokens/%s' % (GIT_CLIENT_ID, token))
    answer = requests.get(url, auth=HTTPBasicAuth(GIT_CLIENT_ID, GIT_CLIENT_SECRET))
    if answer.status_code in [200, 204]:
        del login_session['token']
        del login_session['email']
        del login_session['username']
        del login_session['provider']
        flash("you have logout!")
        return redirect(url_for("login_page"))
    else:
        response = make_response(render_template("error.html", code =400, message = "cannot revoke token"),400)
        return response
        
# gplus logout.
@app.route('/gdisconnect',methods = ['GET'])
def g_disconnect_page():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(render_template("error.html", code =401, message = "user not log in"), 401)
        return response
    # revoke the token.
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials
    print url
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['picture']
        del login_session['email']
        del login_session['username']
        del login_session['provider']
        flash("you have logout!")
        return redirect(url_for("login_page"))
    else:
        response = make_response(render_template("error.html", code =400, message = "cannot revoke token"),400)
        return response

# login using gplus.
@app.route('/gconnect', methods = ['POST'])
def g_connect_page():
    # check 'state' to prevent cross-site request forgery attacks.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    code = request.data
    # using the authorization code to exchange access token.
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope = "")
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    access_token = credentials.access_token
    # check the token's validity.
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
    # check if any user have already login using gplus.
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        login_session['credentials'] = access_token
        response = make_response(json.dumps('Current user is already connected.', 200))
        response.headers['Content-type'] = 'application/json'
        return response
    # login and fetch userinfo. if this is the first time to login, register the user.
    login_session['credentials'] = access_token
    login_session['gplus_id'] = gplus_id
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token':access_token, 'alt': 'json'}
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

# login page
@app.route('/login')
def login_page():
    state = "".join([random.choice(string.ascii_uppercase + string.digits) for i in range(0,32)])
    login_session['state'] = state
    return render_template("login.html", state = state, login_session = login_session)

# logout page, redirect according to login provider.
@app.route('/logout')
def logout_page():
    if login_session.get('username'):
        if login_session['provider'] == 'gplus':
            return redirect(url_for('g_disconnect_page'))
        if login_session['provider'] == 'github':
            return redirect(url_for('git_disconnect_page'))
    else:
         return redirect(url_for('login_page'))  

# json pages.
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

# cover_page which shows the latest items.
@app.route('/')
@app.route('/catalog/')
def cover_page():
    catalog = session.query(Catalog).all()
    lastest = session.query(Item).order_by(Item.last_edit.desc()).limit(10).all()
    return render_template("catalog.html", catalog = catalog, item = lastest, login_session = login_session, cat = None)

# create a new catalog.
@login_required
@app.route('/catalog/new', methods = ['POST'])
def new_catalog_page():
    # only logined users can make a new catagory in database.
    if request.method == 'POST':
        new_catalog = Catalog(name = request.form['name'], user = getUserInfo(login_session['user_id']))
        session.add(new_catalog)
        flash('New Catalog %s sucessfully created' % new_catalog.name)
        session.commit()
        catalog_id = session.query(Catalog).filter_by(name = request.form['name']).one().id
        
        return redirect(url_for("catalog_page", catalog_id = catalog_id))

# the page to show each catagory.
@app.route('/catalog/<int:catalog_id>')
def catalog_page(catalog_id):
    try:
        catalog = session.query(Catalog).all()
        cat = session.query(Catalog).filter_by(id = catalog_id).one()
        item = session.query(Item).filter_by(catalog_id = cat.id).all()
        return render_template("catalog.html",catalog = catalog, item = item, login_session = login_session, cat = cat)
    except:
        return make_response(render_template("error.html", code =404, message = "file not found"), 404)

# edit catagory's name.
@login_required
@app.route('/catalog/<int:catalog_id>/edit',methods=['POST'])
def catalog_edit_page(catalog_id):
    if request.method == "POST":
        # only the author can change the catagory.
        selected_catalog = session.query(Catalog).filter_by(id = catalog_id).one()
        if login_session['user_id'] != selected_catalog.user_id:
            return make_response(render_template("error.html", code =401, message = "you don't have authorization to make this change"), 401)
        selected_catalog.name = request.form['name']
        selected_catalog.last_edit = now()
        session.add(selected_catalog)
        flash('Catalog %s sucessfully updated' % selected_catalog.name)
        session.commit()
        return redirect(url_for("catalog_page", catalog_id = catalog_id))

# delete catagory
@login_required
@app.route('/catalog/<int:catalog_id>/delete',methods=['POST'])
def catalog_delete_page(catalog_id):
    if request.method == "POST":
        selected_catalog = session.query(Catalog).filter_by(id = catalog_id).one()
        # only the author can delete the catagory.
        if login_session['user_id'] != selected_catalog.user_id:
            return make_response(render_template("error.html", code =401, message = "you don't have authorization to make this change"), 401)
        affected_items = session.query(Item).filter_by(catalog_id = catalog_id).all()
        for item in affected_items:
            session.delete(item)
            flash('Item %s successfully deleted' % item.name)
        session.commit()
        session.delete(selected_catalog)
        flash('Catalog %s successfully deleted' % selected_catalog.name)
        session.commit()
        return redirect(url_for("cover_page"))

# page to display an item.
@app.route('/item/<int:item_id>')
def item_page(item_id):
    try:
        item = session.query(Item).filter_by(id = item_id).one()
        return render_template("item.html", item = item, login_session = login_session)
    except:
        return make_response(render_template("error.html", code =404, message = "file not found"), 404)

# create a new item.
@login_required
@app.route('/item/<int:catalog_id>/new', methods=['POST'])
def item_new_page(catalog_id):
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

# edit an item.
@login_required
@app.route('/item/<int:item_id>/edit', methods=['POST'])
def item_edit_page(item_id):
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
        if request.form['name'] or request.form['picture'] or request.form['description']:
            selected_item.last_edit = now()
        session.add(selected_item)
        flash(' Item %s sucessfully updated' % selected_item.name)
        session.commit()
        return redirect(url_for("item_page", item_id = selected_item.id))

# delete an item.
@login_required
@app.route('/item/<int:item_id>/delete', methods=['POST'])
def item_delete_page(item_id):
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
