My Item Catalog Project version 1.0.0 21/01/2017

GENERAL USAGE NOTES
-------------------------------------------------------------------------------
- This Web App is a catalog for sport items. It displays the name and description
for a given sport item.
- To be able to add a new category (sport) or a new item you need to login with
google or facebook account.
- A logged in user is able to add an item to a category he did not created but
cannot edit or delete the category itself or items he did not create.
- A logged in user can create, edit and delete a category and its items.

REQUIREMENTS
-------------------------------------------------------------------------------
- This software requires Python Interpreter 2.X.X to run.
- This software was built using Python 2.7.12
- Flask
- SQLAlchemy
- VirtualBox
- Vagrant

RUNNING THE APP
-------------------------------------------------------------------------------
- Set up VirtualBox and Vagrant to create your server.
- Once Vagrant is installed, run:
```
$ vagrant up
$ vagrant ssh
$ cd <PATH TO REPOSITORY>
```
- Initialize the database:
```
$ python database_setup.py
```
- Populate the database:
```
$ python lots_of_items.py
```
- Run the App:
```
$ python application.py
```
- You can now view the web app on http://localhost:5000/


API Endpoints
-------------------------------------------------------------------------------

Available in JSON at the following endpoints:

List all categories:
http://localhost:5000/categories/JSON

List all items for a given category_id (here snowboarding items)
http://localhost:5000/categories/2/items/JSON

List a single item (here EVERLAST BOXING GLOVES item)
http://localhost:5000/categories/3/item/7/JSON


CONTACT
-------------------------------------------------------------------------------
Author: Elodie Lecostey
E-mail: elodie_lecostey@hotmail.com
Github: https://github.com/elecostey/Udacity/tree/master/itemCatalog
