Trapper
=======

Welcome to Tr@pper!

In order to run the application you will need the following:

* Python 2.7.x
* Django 1.6
* Sqlite3


Installation
------------

It is suggested to install Django and other requirements using [virtualenv](www.virtualenv.org).

1. Clone the repository:
```
https://github.com/kiryx/Trapper.git
```

2. Once you're inside the **Trapper/** directory, initialize the virtual environment:

```
virtualenv env
./env/bin/pip install -r requirements.txt **
```

3. Run the script which initializes the database along with the initial data:

```
./reset_database.sh
```

Run the server:

```
./env/bin/python manage.py runserver
```
