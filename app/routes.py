from flask import render_template, flash, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from urllib import parse
from datetime import datetime
from haversine import haversine, Unit
import time
from app import app
from app.forms import AddForm, SearchItemForm, SearchBusinessForm

mongo = PyMongo(app)

items = []
itemscount = mongo.db.items.count_documents({})
if itemscount == 0:
    items = [
        {'item': 'Hand Sanitizer', 'priority': 1},
        {'item': 'Sanitizing Wipes', 'priority': 1},
        {'item': 'Sanitizing Spray', 'priority': 1},
        {'item': 'Toilet Paper', 'priority': 1},
        {'item': 'Hand Soap', 'priority': 1},
        {'item': 'Milk', 'priority': 1},
        {'item': 'Eggs', 'priority': 1},
        {'item': 'Yogurt', 'priority': 1},
        {'item': 'Bread', 'priority': 1},
        {'item': 'Cereal', 'priority': 1}
    ]
    mongo.db.items.insert_many(items)

itemsquery = mongo.db.items.find({}, {'item': 1, '_id': 0}).sort('priority', -1)
for item in itemsquery:
    items.append(item['item'])


def humanize_ts(timestamp=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    now = datetime.now()
    diff = now - datetime.fromtimestamp(timestamp)
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(int(second_diff)) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(int(second_diff / 60)) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(int(second_diff / 3600)) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(int(day_diff / 7)) + " weeks ago"
    if day_diff < 365:
        return str(int(day_diff / 30)) + " months ago"
    return str(int(day_diff / 365)) + " years ago"


app.jinja_env.filters['humanize'] = humanize_ts


@app.route('/')
@app.route('/index')
def index():
    entries = mongo.db.entries.find().sort('timestamp', -1).limit(10)
    return render_template('index.html', entries=entries)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddForm()
    place = {
        'place_id': None,
        'business': None,
        'address': None,
        'lat': None,
        'long': None
    }
    if form.validate_on_submit():
        entry = {
            'item': form.item.data.title(),
            'quantity': form.quantity.data,
            'timestamp': time.time(),
            'place_id': form.place_id.data,
            'business': form.name.data,
            'address': form.address.data,
            'lat': form.lat.data,
            'long': form.long.data
        }
        mycol = mongo.db.entries
        entry_id = mycol.insert_one(entry)
        itemcol = mongo.db.items
        existing_item = list(itemcol.find({'item': form.item.data.title()}))
        if not existing_item:
            new_item = itemcol.insert_one({'item': form.item.data.title(),
                                           'priority': 1
                                           })
            items.append(form.item.data.title())
        else:
            itemcol.update_one({'item': form.item.data.title()}, {'$inc': {'priority': 1}})
        flash('New entry added')
        return redirect(url_for('addsplash', place_id=parse.quote(form.place_id.data),
                                business=parse.quote(form.name.data), address=parse.quote(form.address.data),
                                lat=parse.quote(form.lat.data), long=parse.quote(form.long.data)))
    return render_template('add.html', form=form, items=items, place=place)


@app.route('/add/<place_id>/<business>/<address>/<lat>/<long>',
           methods=['GET', 'POST'])
def addplus(place_id, business, address, lat, long):
    form = AddForm()
    place = {
        'place_id': parse.unquote(place_id),
        'business': parse.unquote(business),
        'address': parse.unquote(address),
        'lat': parse.unquote(lat),
        'long': parse.unquote(long)
    }
    if form.validate_on_submit():
        entry = {
            'item': form.item.data.title(),
            'quantity': form.quantity.data,
            'timestamp': time.time(),
            'place_id': form.place_id.data,
            'business': form.name.data,
            'address': form.address.data,
            'lat': form.lat.data,
            'long': form.long.data
        }
        mycol = mongo.db.entries
        entry_id = mycol.insert_one(entry)
        flash('New entry added')
        return redirect(url_for('addsplash', place_id=parse.quote(form.place_id.data),
                                business=parse.quote(form.name.data), address=parse.quote(form.address.data),
                                lat=parse.quote(form.lat.data), long=parse.quote(form.long.data)))
    return render_template('add.html', form=form, items=items, place=place)


@app.route('/addsplash/<place_id>/<business>/<address>/<lat>/<long>')
def addsplash(place_id, business, address, lat, long):
    return render_template('addsplash.html', place_id=parse.unquote(place_id),
                           business=parse.unquote(business), address=parse.unquote(address),
                           lat=parse.unquote(lat), long=parse.unquote(long))


@app.route('/search', methods=['GET', 'POST'])
def search():
    formPlace = SearchBusinessForm()
    place = {
        'place_id': None,
        'business': None,
        'address': None
    }
    if formPlace.validate_on_submit():
        return redirect(url_for('search_place', place_id=parse.quote(formPlace.place_id.data),
                                business=parse.quote(formPlace.name.data), address=parse.quote(formPlace.address.data)))

    formItem = SearchItemForm()
    if formItem.validate_on_submit():
        loc = formItem.zip.data
        if formItem.zip.data == '':
            loc = 'Fairfax, VA'
        return redirect(url_for('search_item', item=parse.quote(formItem.item.data), lat=parse.quote(formItem.lat.data),
                                long=parse.quote(formItem.long.data), radius=parse.quote(formItem.radius.data), zip=parse.quote(loc)))
    return render_template('search.html', formPlace=formPlace, formItem=formItem, place=place, items=items)


@app.route('/search/store/<place_id>/<business>/<address>', methods=['GET', 'POST'])
def search_place(place_id, business, address):
    form = SearchBusinessForm()
    place = {
        'place_id': parse.unquote(place_id),
        'business': parse.unquote(business),
        'address': parse.unquote(address)
    }
    mycol = mongo.db.entries
    pipeline = [
        {'$match': {'place_id': parse.unquote(place_id)}},
        {'$sort': {'timestamp': -1}},
        {'$group':
             {'_id': '$item',
              'latest': {'$first': '$timestamp'},
              'quantity': {'$first': '$quantity'}
              }
         },
        {'$sort': {'latest': -1}}
    ]
    results = list(mycol.aggregate(pipeline))

    return render_template('searchplace.html', results=results, place=place)


@app.route('/search/item/<item>/<lat>/<long>/<zip>/<radius>')
def search_item(item, lat, long, zip, radius):
    item = parse.unquote(item)
    zip = parse.unquote(zip)
    mycol = mongo.db.entries
    pipeline = [
        {'$match': {'item': item.title()}},
        {'$sort': {'timestamp': -1}},
        {'$group':
             {'_id': '$place_id',
              'latest': {'$first': '$timestamp'},
              'quantity': {'$first': '$quantity'},
              'business': {'$first': '$business'},
              'address': {'$first': '$address'},
              'lat': {'$first': '$lat'},
              'long': {'$first': '$long'}
              }
         },
        {'$sort': {'latest': -1}}
    ]
    results = list(mycol.aggregate(pipeline))

    output = []
    user = (float(parse.unquote(lat)), float(parse.unquote(long)))
    for result in results:
        business = (float(result['lat']), float(result['long']))
        distance = haversine(user, business, unit='mi')
        if distance <= int(radius):
            result['distance'] = distance
            output.append(result)

    results = output

    return render_template('searchitem.html', results=results, curritem=item, lat=lat, long=long, radius=radius, zip=zip)
