from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
app = Flask(__name__)

# DATABASE IMPORT

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


@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    res = session.query(Restaurant).filter_by(id = restaurant_id).one()

    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)

    return render_template('menu.html', restaurant=res, items = items)

@app.route('/restaurants/<int:restaurant_id>/json')
def restaurantMenuJSON(restaurant_id):
    res = session.query(Restaurant).filter_by(id = restaurant_id).one()

    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)

    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/json')
def menuSingleItemJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()

    return jsonify(MenuItems=item.serialize)

@app.route('/restaurants/<int:restaurant_id>/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'], restaurant_id = restaurant_id)
        session.add(newItem)
        session.commit()
        flash("New Menu Item Created!")
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('newMenuItem.html', restaurant_id = restaurant_id)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):

    item = session.query(MenuItem).filter_by(id = menu_id).one()

    if request.method == 'POST':
        item.name = request.form['name']
        session.add(item)
        session.commit()
        flash("Menu Item Edited!")
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editMenuItem.html', restaurant_id=restaurant_id,menu_id=menu_id,item=item)



@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id = menu_id).one()

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Menu Item Deleted!")
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deleteMenuItem.html', restaurant_id=restaurant_id,menu_id=menu_id,item=item)


if __name__ == "__main__":
    app.secret_key = "key"
    app.debug = True
    app.run(host = '0.0.0.0', port = 8080)
