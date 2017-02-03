from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from flask import Flask, render_template, request, redirect, \
                  url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
import random
import string
app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    # YOU SHOULD PASS THE LOGIN SESSION SOMEHOW SO YOU CAN ACCESS IT FROM HTML
    return render_template('login.html', STATE=state)


########################
# GOOGLE SIGN IN STUFF #
########################
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; ' \
              'border-radius: 150px;-webkit-border-radius: 150px;' \
              '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s' % access_token
    print 'user name is'
    print login_session['username']
    if access_token is None:
        print 'Credentials is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(
            json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

############################
# GOOGLE SIGN IN STUFF END #
############################


##########################
# FACEBOOK SIGN IN STUFF #
##########################

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?' \
          'grant_type=fb_exchange_token&' \
          'client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
           app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the info before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&' \
          'height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;' \
              '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s'\
          % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

##############################
# FACEBOOK SIGN IN STUFF END #
##############################


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            flash("Successfully disconnected")
            return redirect(url_for('showCategories'))
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['user_id']
            del login_session['provider']
            flash("You have successfully been logged out.")
            return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


@app.route('/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/categories/<int:category_id>/item/<int:item_id>/JSON')
def ItemJSON(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


@app.route('/categories/<int:category_id>/items/JSON')
def ItemsJSON(category_id):
    restaurant = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id)
    return jsonify(Items=[i.serialize for i in items])


@app.route('/')
@app.route('/categories/')
def showCategories():
    # return "This page will show all my categories"
    categories = session.query(Category).order_by(Category.name).all()
    if 'username' not in login_session:
        return render_template('categories.html',
                               categories=categories,
                               username="USER_NOT_LOGGED_IN")
    else:
        return render_template('categories.html',
                               categories=categories,
                               username=login_session['username'])


@app.route('/category/<int:category_id>/')
@app.route('/category/<int:category_id>/items/')
def showItems(category_id):
    # return "This page shows the items for category %s" % category_id
    categories = session.query(Category).order_by(Category.name).all()
    category = session.query(Category).filter_by(id=category_id).one()
    creator = getUserInfo(category.user_id)
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template('items.html',
                           category=category,
                           items=items,
                           creator=creator,
                           categories=categories)


@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    # this page will be for making a new category"
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'].strip(),
                               user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        flash("new category created!")
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')


@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    # return "This page will be for editing category %s" % category_id
    if 'username' not in login_session:
        return redirect('/login')
    editedCategory = session.query(Category).filter_by(id=category_id).one()
    if editedCategory.user_id != login_session['user_id']:
        flash('You do not have access to edit %s.' % editedCategory.name)
        return redirect(url_for('showItems', category_id=category_id))
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        session.add(editedCategory)
        session.commit()
        flash("Category successfully edited")
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('editCategory.html',
                               category_id=category_id,
                               category=editedCategory)


@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    # return "This page will be for deleting category %s" % category_id
    categoryToDelete = session.query(Category).filter_by(id=category_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if categoryToDelete.user_id != login_session['user_id']:
        flash('You do not have access to delete %s.' % categoryToDelete.name)
        return redirect(url_for('showItems', category_id=category_id))
    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        flash("Category successfully deleted")
        return redirect(url_for('showCategories', category_id=category_id))
    else:
        return render_template('deleteCategory.html',
                               category_id=category_id,
                               category=categoryToDelete)


@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
def newItem(category_id):
    # return "This page is for making new item for category %s" % category_id
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()

    if request.method == 'POST':
        newItem = Item(name=request.form['name'].strip(),
                       description=request.form['description'],
                       category_id=category_id,
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("New item created!")
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('newItem.html', category_id=category_id)


@app.route('/category/<int:category_id>/item/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    # return "This page is for editing  item %s" % item_id
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Item).filter_by(id=item_id).one()
    if editedItem.user_id != login_session['user_id']:
        flash('You do not have access to edit item %s.' % editedItem.name)
        return redirect(url_for('showItems', category_id=category_id))
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash("Item successfully edited")
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('editItem.html',
                               category_id=category_id,
                               item_id=item_id,
                               item=editedItem)


@app.route('/category/<int:category_id>/item/<int:item_id>/delete/',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    # return "This page is for deleting  item %s" % item_id
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if itemToDelete.user_id != login_session['user_id']:
        flash('You do not have access to delete item %s.' % itemToDelete.name)
        return redirect(url_for('showItems', category_id=category_id))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("Item successfully deleted")
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('deleteItem.html',
                               category_id=category_id,
                               item_id=item_id,
                               item=itemToDelete)


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
