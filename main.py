from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Catalog, Item, User
from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

engine = create_engine('sqlite:///catlog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

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
    return render_template("catalog.html", catalog = catalog, item = lastest, active_id = 0, subtitle = "Lastest 10 items")

@app.route('/catalog/new', methods = ['POST'])
def new_catalog_page():
    if request.method == 'POST':
        new_catalog = Catalog(name = request.form['name'], user = session.query(User).filter_by(id =1).one())
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
        return render_template("catalog.html",catalog = catalog, item = item, active_id = catalog_id, subtitle = cat.name)
    except:
        return make_response("file not found", 404)

@app.route('/catalog/<int:catalog_id>/edit',methods=['POST'])
def catalog_edit_page(catalog_id):
    if request.method == "POST":
        selected_catalog = session.query(Catalog).filter_by(id = catalog_id).one()
        selected_catalog.name = request.form['name']
        session.add(selected_catalog)
        flash('Catalog %s sucessfully updated' % selected_catalog.name)
        session.commit()
        return redirect(url_for("catalog_page", catalog_id = catalog_id))

@app.route('/catalog/<int:catalog_id>/delete',methods=['POST'])
def catalog_delete_page(catalog_id):
    if request.method == "POST":
        selected_catalog = session.query(Catalog).filter_by(id = catalog_id).one()
        session.delete(selected_catalog)
        flash('Catalog %s sucessfully deleted' % selected_catalog.name)
        session.commit()
        return redirect(url_for("cover_page"))
 
@app.route('/item/<int:item_id>')
def item_page(item_id):
    try:
        item = session.query(Item).filter_by(id = item_id).one()
        return render_template("item.html", item = item)
    except:
        return make_response("file not found", 404)

@app.route('/item/<int:catalog_id>/new', methods=['POST'])
def item_new_page(catalog_id):
    if request.method == 'POST':
        cat = session.query(Catalog).filter_by(id = catalog_id).one()
        new_item = Item(name = request.form['name'], catalog = cat, user = session.query(User).filter_by(id =1).one())
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
    if request.method == "POST":
        selected_item = session.query(Item).filter_by(id = item_id).one()
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
    if request.method == "POST":
        selected_item = session.query(Item).filter_by(id = item_id).one()
        session.delete(selected_item)
        flash('Item %s sucessfully deleted' % selected_item.name)
        session.commit()
        return redirect(url_for("cover_page"))

if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 8000)
