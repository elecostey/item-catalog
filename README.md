My Linux Server Configuration project version 1.0.0 04/02/2017

GENERAL USAGE NOTES
-------------------------------------------------------------------------------
 - The purpose of this project is to setup a Linux virtual machine Configuration
  to support the Item Catalog website.

 - The website can be reviewed at http://52.26.162.36 .

REQUIREMENTS
-------------------------------------------------------------------------------
- Launch your Virtual Machine with your Udacity account
- Follow the instructions provided to SSH into your server
- Create a new user named grader
- Give the grader the permission to sudo
- Update all currently installed packages
- Change the SSH port from 22 to 2200
- Configure the Uncomplicated Firewall (UFW) to only allow incoming connections for SSH (port 2200), HTTP (port 80), and NTP (port 123)
- Configure the local timezone to UTC
- Install and configure Apache to serve a Python mod_wsgi application
- Install and configure PostgreSQL:
	- Do not allow remote connections
	- Create a new user named catalog that has limited permissions to your catalog application database
- Install git, clone and setup your Catalog App project (from your GitHub repository from earlier in the Nanodegree program) so that it functions correctly when visiting your server’s IP address in a browser. Remember to set this up appropriately so that your .git directory is not publicly accessible via a browser!

LAUNCH THE VIRTUAL MACHINE
-------------------------------------------------------------------------------
 - Download the Udacity RSA Key
 - `mv ~/Downloads/udacity_key.rsa ~/.ssh/`
 - restrict the key access
 - `chmod 644 ~/.ssh/udacity_key.rsa`
 -  SSH into the server
 - `ssh -i ~/.ssh/udacity_key.rsa root@52.26.162.36`

USER CREATION & SUDO RIGHTS
-------------------------------------------------------------------------------
- Create a new user named grader

- `sudo adduser grader`
-  give our hero a password
- `nano /etc/sudoers`
- `touch /etc/sudoers.d/grader`
- `nano /etc/sudoers.d/grader`, type in `grader ALL=(ALL:ALL) PASSWD: ALL`
- `CTRL + O` confirm save and exit with `CTRL + X`

- DISABLE SSH LOGIN FOR ROOT USER
- `sudo nano /etc/ssh/sshd_config`
- Set `PermitRootLogin` from `without-password` to `no`
- restart the service with `/etc/init.d/sshd restart`

SSH LOGIN SETUP
-------------------------------------------------------------------------------
- generate keys on the local machine using`ssh-keygen`
- afterwards save the private key in `~/.ssh` on the local machine
- copy & paste the public key to the developement enviroment 

- log in as root:
	```
	$ su grader
	$ mkdir .ssh
	$ touch .ssh/authorized_keys
	$ nano .ssh/authorized_keys
	```
	Paste the public key generated on the local machine to this file and save
	```
	$ chmod 700 .ssh
	$ chmod 644 .ssh/authorized_keys
	```
	
- reload SSH using `service ssh restart`
- SSH login is now available

	`ssh -i [privateKeyFilename] grader@52.26.162.36`


UPDATE ALL CURRENTLY INSTALLED PACKAGES
-------------------------------------------------------------------------------
- Since grader has sudo privileges we can skip the sudo in the next commands:

 - `apt-get update`
 - `apt-get upgrade`
 -  Input `y` when prompted

FIREWALL CONFIGURATION
-------------------------------------------------------------------------------
- Initially check the status with `ufw status` 

 - `ufw status`
 -  We need to remove SSH 22 port that is allowed by default
 - `ufw delete allow 22`
 - `ufw allow 2200/tcp`
 - `ufw allow 80/tcp`
 - `ufw allow 123/udp`
 - `ufw enable`
 - `service ufw restart`
 - `exit` (Log off)

UTC CONFIGURATION
-------------------------------------------------------------------------------
- Configure the time zone `sudo dpkg-reconfigure tzdata`
- Timezone is already set to UTC.

APACHE INSTALLATION
-------------------------------------------------------------------------------
- Install Apache `sudo apt-get install apache2`
- Install mod_wsgi `sudo apt-get install python-setuptools libapache2-mod-wsgi`
- Restart Apache `sudo service apache2 restart`

PYTHON INSTALLATION
-------------------------------------------------------------------------------
 - `apt-get install python-pip`
 - `pip install virtualenv`
 - `virtualenv venv` 
 - `chmod -R 777 venv`
 - `pip install Flask-Seasurf`
 - `pip install requests`
 - `pip install --upgrade oauth2client`
 - `pip install sqlalchemy`
 - `apt-get install python-psycopg2`
 - `pip install bleach`

POSTGRES INSTALLATION
-------------------------------------------------------------------------------
- Fetch PostgreSQL `sudo apt-get install postgresql`
- Switch to "postgres" `sudo su postgres`
- Start the postgreSQL shell `psql`
- Create a new database named "catalog" and create a new user named "catalog" through postgreSQL shell
	
	```
	postgres=# CREATE DATABASE catalog;
	postgres=# CREATE USER catalog;
	```
- Assign a password to the user "catalog"
	
	```
	postgres=# ALTER ROLE catalog WITH PASSWORD 'catalog';
	```
- Grant permissions to the user "catalog" on the "catalog" application database
	
	```
	postgres=# GRANT ALL PRIVILEGES ON DATABASE catalog TO catalog;
	```
- Quit postgreSQL `postgres=# \q`
- Exit from user "postgres" 
	
	```
	exit
	```

GIT INSTALLATION, PROJECT CLONE & DATABASE POPULATING
-------------------------------------------------------------------------------
 - `apt-get install git`
 - `git config --global user.name "Elodie Lecostey"`
 - `git config --global user.email "lecostey.e@gmail.com"`
 - `git config --list` to be sure

- Use `cd /var/www` to navigate to the /var/www directory 
- Create the application directory `sudo mkdir FlaskApp`
- Navigate inside this directory using `cd FlaskApp`
- Clone the Item Catalog App to the virtual machine `git clone https://github.com/elecostey/item-catalog.git`
- Rename the project `sudo mv ./item-catalog ./FlaskApp`
- Move to the inner FlaskApp directory using `cd FlaskApp`
- Rename `application.py` to `__init__.py` using `sudo mv application.py __init__.py`
- We need to modify our database connection string
- Edit `database_setup.py`, `website.py` and `functions_helper.py` and change `engine = create_engine('sqlite:///itemcatalog.db')` to `engine = create_engine('postgresql://catalog:catalog@localhost/catalog')`
- We can populate our database now by running our helper scripts:
- `sudo python database_setup.py`
- `sudo python itemcatalog.py`

PREPARE OUR APP TO RUN WITH APACHE - VIRTUAL HOST
-------------------------------------------------------------------------------
- Create the FlaskApp.conf: `sudo nano /etc/apache2/sites-available/FlaskApp.conf`
	
	```
	<VirtualHost *:80>
		ServerName 52.26.162.36
		ServerAdmin lecostey.e@gmail.com
		WSGIScriptAlias / /var/www/FlaskApp/flaskapp.wsgi
		<Directory /var/www/FlaskApp/FlaskApp/>
			Order allow,deny
			Allow from all
		</Directory>
		Alias /static /var/www/FlaskApp/FlaskApp/static
		<Directory /var/www/FlaskApp/FlaskApp/static/>
			Order allow,deny
			Allow from all
		</Directory>
		ErrorLog ${APACHE_LOG_DIR}/error.log
		LogLevel warn
		CustomLog ${APACHE_LOG_DIR}/access.log combined
	</VirtualHost>
	```
- Enable the virtual host with the following command: `sudo a2ensite FlaskApp`
- We should be offered a suggestion to restart Apache but we can wait.

- Create the .wsgi File under /var/www/FlaskApp: 
	
	```
	cd /var/www/FlaskApp
	sudo nano flaskapp.wsgi 
	```
- Add the following lines of code to the flaskapp.wsgi file:
	
	```
	#!/usr/bin/python
	import sys
	import logging
	logging.basicConfig(stream=sys.stderr)
	sys.path.insert(0,"/var/www/FlaskApp/")

	from FlaskApp import app as application
	application.secret_key = 'super_secret_key'
	```

- Finally Restart Apache `sudo service apache2 restart`
- Project can now be accessed on http://52.26.162.36

ERRORS 
-------------------------------------------------------------------------------
- In case of any errors you can check the apache log for clues
- `cat /var/log/apache2/error.log`

REFERENCES 
-------------------------------------------------------------------------------
https://help.ubuntu.com/community/PostgreSQL
https://wiki.archlinux.org/index.php/SSH_keys
https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
https://www.digitalocean.com/community/tutorials/how-to-setup-a-firewall-with-ufw-on-an-ubuntu-and-debian-cloud-server

CONTACT
-------------------------------------------------------------------------------
Author: Elodie Lecostey
E-mail: elodie_lecostey@hotmail.com
Github: https://github.com/elecostey/item-catalog
