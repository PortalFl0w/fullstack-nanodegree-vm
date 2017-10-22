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
@app.route('/restaurants/')
def showRestaurants():

    restaurants = session.query(Restaurant)

    return render_template('index.html', restaurants=restaurants)


@app.route('/restaurant/new/', methods=['GET', 'POST'])
def newRestaurant():

    if request.method == 'POST':
        restaurant = Restaurant(name=request.form['name'])
        session.add(restaurant)
        session.commit()
        flash("Restaurant Added!")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')


@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):

    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

    if request.method == 'POST':
        restaurant.name = request.form['name']
        session.add(restaurant)
        session.commit()
        flash("Restaurant Edited!")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('editRestaurant.html', restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):

    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        flash("Restaurant Deleted!")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleteRestaurant.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):

    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)

    return render_template('singleRestaurant.html', restaurant=restaurant, items = items)

@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):

    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

    if request.method == 'POST':
        menuItem = MenuItem(name = request.form['name'], price= request.form['price'], description= request.form['description'], course= request.form['course'],restaurant_id = restaurant_id)
        session.add(menuItem)
        session.commit()
        flash("New Menu Dish Added!")
        return redirect(url_for('showMenu', restaurant_id=restaurant.id))
    else:
        return render_template('newMenuItem.html', restaurant=restaurant)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):

    item = session.query(MenuItem).filter_by(id = menu_id).one()

    if request.method == 'POST':
        item.name = request.form['name']
        item.price = request.form['price']
        item.description = request.form['description']
        item.course = request.form['course']
        session.add(item)
        session.commit()
        flash("Menu Item Edited Successfully!")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editMenuItem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=item)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):

    item = session.query(MenuItem).filter_by(id = menu_id).one()

    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Menu Item Deleted!")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deleteMenuItem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=item)


############ JSON API ###############

@app.route('/restaurants/JSON')
def showRestaurantsJSON():

    restaurants = session.query(Restaurant)
    json = []
    for i in restaurants:
        json.append(i.serialize)
    return jsonify(Restaurants=json)

@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def showMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    menu = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    json = []
    for i in menu:
        json.append(i.serialize)
    return jsonify(Menu=json, Restaurant=restaurant.serialize)

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def singleMenuItemJSON(restaurant_id,menu_id):
    menu = session.query(MenuItem).filter_by(id = menu_id).one()
    return jsonify(MenuItem=menu.serialize)


if __name__ == "__main__":
    app.secret_key = "key"
    app.debug = True
    app.run(host = '0.0.0.0', port = 8080)
