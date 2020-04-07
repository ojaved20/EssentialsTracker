from flask import render_template, flash, redirect, url_for, send_file
from flask_pymongo import PyMongo
from urllib import parse
from datetime import datetime
from haversine import haversine, Unit
import time
import pytz
from tzlocal import get_localzone
from app import app
from app.forms import AddForm, SearchItemForm, SearchBusinessForm, BrowseItemsForm

mongo = PyMongo(app)

items = []
itemscount = mongo.db.items.count_documents({})
if itemscount == 0:
    items = [
        {'item': 'Hand Sanitizer', 'priority': 1, 'category': 'Hygiene', 'altnames': ['Purell'], 'timestamp': time.time()},
        {'item': 'Toilet Paper', 'priority': 1, 'category': 'Hygiene', 'altnames': ['Charmin Toilet Paper'], 'timestamp': time.time()},
        {'item': 'Masks', 'priority': 1, 'category': 'Hygiene', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Disposable Gloves', 'priority': 1, 'category': 'Hygiene', 'altnames': ['Latex Gloves', 'Nitrile Gloves'], 'timestamp': time.time()},
        {'item': 'Tissues', 'priority': 1, 'category': 'Hygiene', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Disinfecting Spray', 'priority': 1, 'category': 'Cleaning', 'altnames': ['Disinfectant Spray', 'Lysol Spray', 'Clorox Spray'], 'timestamp': time.time()},
        {'item': 'Disinfecting Wipes', 'priority': 1, 'category': 'Cleaning', 'altnames': ['Disinfectant Wipes','Lysol Wipes','Clorox Wipes'], 'timestamp': time.time()},
        {'item': 'Hand Soap', 'priority': 1, 'category': 'Cleaning', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Dish Soap', 'priority': 1, 'category': 'Cleaning', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Laundry Detergent', 'priority': 1, 'category': 'Cleaning', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Paper Towels', 'priority': 1, 'category': 'Cleaning', 'altnames': ['Bounty Paper Towels'], 'timestamp': time.time()},
        {'item': 'Multi-surface Cleaner', 'priority': 1, 'category': 'Cleaning', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Rubbing Alcohol', 'priority': 1, 'category': 'Cleaning', 'altnames': ['Liquid Alohol'], 'timestamp': time.time()},
        {'item': 'Tylenol', 'priority': 1, 'category': 'Medical', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Advil', 'priority': 1, 'category': 'Medical', 'altnames': ['Ibuprofin'], 'timestamp': time.time()},
        {'item': 'Motrin', 'priority': 1, 'category': 'Medical', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Aspirin', 'priority': 1, 'category': 'Medical', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Cold Medicine', 'priority': 1, 'category': 'Medical', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Children''s Tyleonl', 'priority': 1, 'category': 'Medical', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Children''s Motrin', 'priority': 1, 'category': 'Medical', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Milk', 'priority': 1, 'category': 'Food', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Eggs', 'priority': 1, 'category': 'Food', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Yogurt', 'priority': 1, 'category': 'Food', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Cheese', 'priority': 1, 'category': 'Food', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Produce - Fruit', 'priority': 1, 'category': 'Food', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Produce - Greens', 'priority': 1, 'category': 'Food', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Pasta', 'priority': 1, 'category': 'Food', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Canned Food', 'priority': 1, 'category': 'Food', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Cereal', 'priority': 1, 'category': 'Food', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Oatmeal', 'priority': 1, 'category': 'Food', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Meat - Chicken', 'priority': 1, 'category': 'Food', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Meat - Beef', 'priority': 1, 'category': 'Food', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Meat - Fish', 'priority': 1, 'category': 'Food', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Baby Formula', 'priority': 1, 'category': 'Baby', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Baby Food', 'priority': 1, 'category': 'Baby', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Diapers', 'priority': 1, 'category': 'Baby', 'altnames': [], 'timestamp': time.time()},
        {'item': 'Baby Wipes', 'priority': 1, 'category': 'Baby', 'altnames': [], 'timestamp': time.time()}
    ]
    mongo.db.items.insert_many(items)

itemsquery = mongo.db.items.find({}, {'item': 1, 'altnames': 1, '_id': 0}).sort('priority', -1)
for item in itemsquery:
    items.append({'item_id': item['item'], 'item_label': item['item']})
    for altname in item['altnames']:
        items.append({'item_id': item['item'], 'item_label': altname})


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


@app.context_processor
def inject_today_date():
    return {'currtime': datetime.now(pytz.utc).astimezone(get_localzone())}


@app.route('/service-worker.js')
def service_worker():
    return send_file('service-worker.js')


@app.route('/offline.html')
def offline():
    return render_template('offline.html')


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
        if form.name.data == 'None':
            flash('Invalid location')
            return render_template('add.html', form=form, items=items, place=place, title="Add an Update")
        entry = {
            'item': form.item.data.title(),
            'quantity': form.quantity.data,
            'timestamp': time.time(),
            'place_id': form.place_id.data,
            'business': form.name.data,
            'address': form.address.data,
            'lat': form.lat.data,
            'long': form.long.data,
            'comment': form.comment.data
        }
        mycol = mongo.db.entries
        entry_id = mycol.insert_one(entry)
        itemcol = mongo.db.items
        existing_item = list(
            itemcol.find(
                {'$or':[{'item': form.item.data.title()},{'altnames': {'$in': [form.item.data.title()]}}]}
            )
        )
        if not existing_item:
            new_item = itemcol.insert_one({'item': form.item.data.title(),
                                           'priority': 1,
                                           'category': None,
                                           'altnames': [],
                                           'timestamp': time.time()
                                           })

            items.append({'item_id': form.item.data.title(), 'item_label': form.item.data.title()})
        else:
            itemcol.update_one({'item': form.item.data.title()}, {'$inc': {'priority': 1}})
        flash('New entry added')
        return redirect(url_for('addsplash', place_id=parse.quote(form.place_id.data),
                                business=parse.quote(form.name.data), address=parse.quote(form.address.data),
                                lat=parse.quote(form.lat.data), long=parse.quote(form.long.data)))
    return render_template('add.html', form=form, items=items, place=place, title="Add an Update")


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
        itemcol = mongo.db.items
        existing_item = list(itemcol.find({'item': form.item.data.title()}))
        if not existing_item:
            new_item = itemcol.insert_one({'item': form.item.data.title(),
                                           'priority': 1,
                                           'category': None,
                                           'altnames': [],
                                           'timestamp': time.time()
                                           })

            items.append({'item_id': form.item.data.title(), 'item_label': form.item.data.title()})
        else:
            itemcol.update_one({'item': form.item.data.title()}, {'$inc': {'priority': 1}})
        flash('New entry added')
        return redirect(url_for('addsplash', place_id=parse.quote(form.place_id.data),
                                business=parse.quote(form.name.data), address=parse.quote(form.address.data),
                                lat=parse.quote(form.lat.data), long=parse.quote(form.long.data)))
    return render_template('add.html', form=form, items=items, place=place, title="Add an Update")


@app.route('/addsplash/<place_id>/<business>/<address>/<lat>/<long>')
def addsplash(place_id, business, address, lat, long):
    return render_template('addsplash.html', place_id=parse.unquote(place_id),
                           business=parse.unquote(business), address=parse.unquote(address),
                           lat=parse.unquote(lat), long=parse.unquote(long), title="Add an Update")


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
                                long=parse.quote(formItem.long.data), radius=parse.quote(formItem.radius.data),
                                zip=parse.quote(loc)))
    formBrowse = BrowseItemsForm()
    if formBrowse.validate_on_submit():
        loc = formBrowse.browse_loc.data
        if formBrowse.browse_loc.data == '':
            loc = 'Fairfax, VA'
        return redirect(url_for('browse', lat=parse.quote(formBrowse.browse_lat.data),
                                long=parse.quote(formBrowse.browse_long.data), radius=parse.quote(formBrowse.browse_radius.data),
                                loc=parse.quote(loc)))
    return render_template('search.html', formPlace=formPlace, formItem=formItem, formBrowse=formBrowse, place=place, items=items,
                           title="Search")


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
              'quantity': {'$first': '$quantity'},
              'comment': {'$first': '$comment'}
              }
         },
        {'$sort': {'latest': -1}}
    ]
    results = list(mycol.aggregate(pipeline))

    return render_template('searchplace.html', results=results, place=place, title="Store Search Results")


@app.route('/search/item/<item>/<lat>/<long>/<zip>/<radius>')
def search_item(item, lat, long, zip, radius):
    item = parse.unquote(item)
    zip = parse.unquote(zip)
    mycol = mongo.db.entries
    term = item
    for itemterm in items:
        labels = itemterm['item_label']
        itemid = itemterm['item_id']
        if item in labels and item not in itemid:
            term= item+' '+itemterm['item_id']

    try:
        pipeline = [
            {
                '$searchBeta': {
                    'search': {
                        'query': term.title(),
                        'path': 'item'
                    }
                }
            },
            {'$sort': {'timestamp': -1}},
            {'$group':
                 {'_id': {'place_id': '$place_id', 'item': '$item'},
                  'latest': {'$first': '$timestamp'},
                  'quantity': {'$first': '$quantity'},
                  'business': {'$first': '$business'},
                  'address': {'$first': '$address'},
                  'lat': {'$first': '$lat'},
                  'long': {'$first': '$long'},
                  'comment': {'$first': '$comment'},
                  'score': {'$first': {'$meta': 'searchScore'}}
                  }
             },
            {'$project':
                {
                    '_id': 1,
                    'latest': 1,
                    'quantity': 1,
                    'business': 1,
                    'address': 1,
                    'lat': 1,
                    'long': 1,
                    'comment': 1,
                    'score': 1
                }
            },
            {'$sort': {'score': -1, 'latest': -1}}
        ]

        results = list(mycol.aggregate(pipeline))
    except:
        pipeline = [
            {
                '$match': {
                    'item': item.title()
                }
            },
            {'$sort': {'timestamp': -1}},
            {'$group':
                 {'_id': {'place_id': '$place_id', 'item': '$item'},
                  'latest': {'$first': '$timestamp'},
                  'quantity': {'$first': '$quantity'},
                  'business': {'$first': '$business'},
                  'address': {'$first': '$address'},
                  'lat': {'$first': '$lat'},
                  'long': {'$first': '$long'},
                  'comment': {'$first': '$comment'}
                  }
             },
            {'$project':
                {
                    '_id': 1,
                    'latest': 1,
                    'quantity': 1,
                    'business': 1,
                    'address': 1,
                    'lat': 1,
                    'long': 1,
                    'comment': 1
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

    return render_template('searchitem.html', results=results, curritem=item, lat=lat, long=long, radius=radius,
                           zip=zip, title="Item Search Results", term=term)


@app.route('/browse/<lat>/<long>/<loc>/<radius>')
def browse(lat, long, loc, radius):
    loc = parse.unquote(loc)
    mycol = mongo.db.entries
    pipeline = [
        {'$sort': {'timestamp': -1}},
        {'$group':
             {'_id': {'place_id':'$place_id', 'item':'$item'},
              'latest': {'$first': '$timestamp'},
              'quantity': {'$first': '$quantity'},
              'business': {'$first': '$business'},
              'address': {'$first': '$address'},
              'lat': {'$first': '$lat'},
              'long': {'$first': '$long'},
              'comment': {'$first': '$comment'}
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

    return render_template('browse.html', results=results, lat=lat, long=long, radius=radius,
                           loc=loc, title="All Updates Near You")


@app.route('/browse/item/<lat>/<long>/<loc>/<radius>')
def browseitem(lat, long, loc, radius):
    loc = parse.unquote(loc)
    mycol = mongo.db.entries

    item_pipleine = [
        {'$group':
             {'_id': '$item'},
         },
        {'$sort': {'_id': 1}}
    ]

    item_results = list(mycol.aggregate(item_pipleine))
    output = []
    for item in item_results:
        pipeline = [
            {'$match': {'item': item['_id']}},
            {'$sort': {'timestamp': -1}},
            {'$group':
                 {'_id': '$place_id',
                  'latest': {'$first': '$timestamp'},
                  'quantity': {'$first': '$quantity'},
                  'business': {'$first': '$business'},
                  'address': {'$first': '$address'},
                  'lat': {'$first': '$lat'},
                  'long': {'$first': '$long'},
                  'comment': {'$first': '$comment'}
                  }
             },
            {'$sort': {'latest': -1}}
        ]

        results = mycol.aggregate(pipeline)

        inventory = []
        user = (float(parse.unquote(lat)), float(parse.unquote(long)))
        for result in results:
            business = (float(result['lat']), float(result['long']))
            distance = haversine(user, business, unit='mi')
            if distance <= int(500):
                result['distance'] = distance
                inventory.append(result)
        item['inventory'] = inventory
        output.append(item)

    results = output

    return render_template('browseitem.html', results=results, lat=lat, long=long, radius=radius,
                           loc=loc, title="All Updates Near You")


@app.route('/browse/stores/<lat>/<long>/<loc>/<radius>')
def browsestore(lat, long, loc, radius):
    loc = parse.unquote(loc)
    mycol = mongo.db.entries
    user = (float(parse.unquote(lat)), float(parse.unquote(long)))

    store_pipleine = [
        {'$group':
             {'_id': '$place_id',
              'business': {'$first': '$business'},
              'address': {'$first': '$address'},
              'lat': {'$first': '$lat'},
              'long': {'$first': '$long'},
              }
         },
        {'$sort': {'business': 1}}
    ]

    store_results = list(mycol.aggregate(store_pipleine))
    output = []
    for store in store_results:
        business = (float(store['lat']), float(store['long']))
        distance = haversine(user, business, unit='mi')
        if distance <= int(500):
            store['distance'] = distance

            inventory = []
            pipeline = [
                {'$match': {'place_id': store['_id']}},
                {'$sort': {'timestamp': -1}},
                {'$group':
                     {'_id': '$item',
                      'latest': {'$first': '$timestamp'},
                      'quantity': {'$first': '$quantity'},
                      'comment': {'$first': '$comment'}
                      }
                 },
                {'$sort': {'latest': -1}}
            ]

            results = mycol.aggregate(pipeline)

            for result in results:
                inventory.append(result)

            store['inventory'] = inventory
            output.append(store)

    results = output
    results.sort(key= lambda x: int(x['distance']))

    return render_template('browsestore.html', results=results, lat=lat, long=long, radius=radius,
                           loc=loc, title="All Updates Near You")


@app.route('/about')
def about():
    return render_template('about.html', title="About")