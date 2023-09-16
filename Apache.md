# Setting Up Django Applications with Apache and mod_wsgi on Ubuntu

These instructions will guide you through the process of setting up a Django application with Apache and mod_wsgi on an Ubuntu server. This setup allows you to deploy your Django project on a production server.

## Prerequisites

Before you begin, make sure you have the following prerequisites:

- Ubuntu server
- `python3-pip`, `apache2`, and `libapache2-mod-wsgi-py3` installed:

   ```bash
   sudo apt-get update
   sudo apt-get install python3-pip apache2 libapache2-mod-wsgi-py3
   ```
note - libapache2-mod-wsgi-py3 this modul only for Python3 interpreter.
## Create a Python Virtual Environment

We'll use `virtualenv` to create a Python virtual environment. Install it using `pip3`:

```bash
sudo pip3 install virtualenv
```

Create a directory for your Django project and set up the virtual environment:

```bash
mkdir django_project
cd django_project
virtualenv env
```

Activate the virtual environment:

```bash
. env/bin/activate
```

## Install Django and Create Your Project

Install Django inside the virtual environment:

```bash
pip3 install django
```

Now, create a Django project within the `django_project` directory:

```bash
django-admin startproject my_django_project .
```

## Complete Initial Project Setup

Use the Django management script to migrate your data to the database:

```bash
cd ~/django_project
python3 manage.py makemigrations
python3 manage.py migrate
```

Create an admin user for your project:

```bash
python3 manage.py createsuperuser
```

Gather static content into the configured directory:

```bash
python3 manage.py collectstatic
```

Verify that your project is working by running the Django local web server:

```bash
python3 manage.py runserver
```

Access your project at [http://127.0.0.1:8000/](http://127.0.0.1:8000/) or [http://localhost:8000/](http://localhost:8000/). To stop the server, use `CTRL-C`.

## Deploying Django Application on Apache Server

### Create a Virtual Host Configuration

Create a virtual host file for your project. Use your text editor to create a `.conf` file in the `/etc/apache2/sites-available/` directory:

```bash
sudo vi /etc/apache2/sites-available/djangoproject.conf
```

Add the following configuration to `djangoproject.conf`:

```apache
<VirtualHost twiddle.campus2pro.co.in:443>
#<VirtualHost *:80>
    ServerAdmin admin@twiddle.campus2pro.co.in
    ServerName twiddle.campus2pro.co.in
    #ServerName twiddle.os3.com
    ServerAlias twiddle.campus2pro.co.in
    DocumentRoot /home/user/twitter-clone-app
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
 
    # SSL Configuration
    SSLEngine on
    #SSLCertificateFile /etc/ssl/certs/twiddle.crt
    #SSLCertificateKeyFile /etc/ssl/private/twiddle.key
 
    Alias /static /home/user/twitter-clone-app/static
        <Directory /home/user/twitter-clone-app/static>
                Require all granted
        </Directory>
 
                   Alias /media /home/user/twitter-clone-app/media
        <Directory /home/user/twitter-clone-app/media>
                Require all granted
        </Directory>
 
        <Directory /home/user/twitter-clone-app/config>
                <Files wsgi.py>
                        Require all granted
                </Files>
        </Directory>
 
    WSGIDaemonProcess twitter-clone-app python-path=/home/user/twitter-clone-app python-home=/home/user/twitter-clone-app/env-twiddle
    WSGIProcessGroup twitter-clone-app
    WSGIScriptAlias / /home/user/twitter-clone-app/config/wsgi.py
    Include /etc/letsencrypt/options-ssl-apache.conf
    SSLCertificateFile /etc/letsencrypt/live/twiddle.campus2pro.co.in/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/twiddle.campus2pro.co.in/privkey.pem
    Header always set Strict-Transport-Security "max-age=31536000;includeSubDomains"
</VirtualHost>

```

Save and close the file.

### Enable the Virtual Host

Enable the virtual host file you created:

```bash
cd /etc/apache2/sites-available
sudo a2ensite djangoproject.conf
```

Reload Apache to apply the changes:

```bash
sudo service apache2 reload
```

### Set Up Local Hosts File (Optional)

Edit your local hosts file to make it easier to access your Django project:

```bash
sudo vi /etc/hosts
```

Add the following line at the end of the file:

```
127.0.0.1 djangoproject.localhost
```

## Permissions and Security

Configure permissions and security:

```bash
sudo ufw allow 'Apache Full'
```

If you're using SQLite as your database, give appropriate permissions:

```bash
sudo chmod 664 /home/user/django_project/db.sqlite3
sudo chown :www-data /home/user/django_project/db.sqlite3
sudo chown :www-data /home/user/django_project
```

Check your Apache configuration for syntax errors:

```bash
sudo apache2ctl configtest
```

If you see "Syntax OK," there are no errors.

## Update Django Settings

Edit your `settings.py` file to add the allowed host URL:

```bash
sudo nano my_django_project/settings.py
```

Add the URL in the `ALLOWED_HOSTS` list:

```python
ALLOWED_HOSTS = ['djangoproject.localhost']
```

Save and exit the file.

## Restart Apache

Restart Apache to apply the changes:

```bash
sudo service apache2 restart
```

You're done! Access your Django project at [http://djangoproject.localhost/](http://djangoproject.localhost/).

These instructions provide a step-by-step guide to set up your Django application on an Apache server with mod_wsgi on Ubuntu.
