*This documentation only covers our installation on a Ubuntu 12.04 machine. Other platforms are not tested.*

Update the machine:

```
sudo apt-get update
sudo apt-get upgrade
```

Install dependencies:

```
sudo apt-get install git postgresql postgresql-contrib postgresql-client libpq-dev python-dev g++ libffi-dev libxml2-dev
libxslt1-dev apache2 apache2-dev
```

Install python, pip and virtualenv:

```
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
sudo pip install virtualenv
```

Globally install requests:

```
sudo pip install requests[security]
```

Check out the repository:

```
git clone https://github.com/Datafable/epu-index.git
```

Create a virtualenv in the `epu-index` folder and activate it:

```
cd epu-index
virtualenv ENV
source ENV/bin/activate
```

Install the projects requirements:

```
pip install -r requirements
```

# Set up the database

Launch `psql` for the following commands. (We're using Postgres 9.3.9)

Create an application user:

```
CREATE USER username PASSWORD 'password';
```

Create a database for the application:

```
CREATE DATABASE epuindex OWNER username;
```

Edit the `pg_hba.conf` file and allow the application user to log in using a password.

# Configure the Django web application

Leave psql, cd into the `webapp` dir and manually create a `settings_local.py` file in the `webapp` module and write
the following lines in there:

```
# Parse database configuration from $DATABASE_URL
DATABASES = {}

import dj_database_url
DATABASES['default'] = dj_database_url.config(default="postgres://username:password@localhost:5432/databasename")
```

Now django should be able to connect to the database. Lastly, do:

```
python manage.py syncdb
```

Django will now synchronize the database and ask you to set up an administrator account. When ready, you can start using
the app. You'll probably want to load some data first. Do that using the appropriate [custom django
commands](webapp/epu_index/management/commands).