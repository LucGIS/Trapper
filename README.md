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
git clone http://github.com/kiryx/Trapper.git
cd Trapper/
```

2. Initialize the virtual environment:
```
virtualenv env
./env/bin/pip install -r requirements.txt
```

3. Initialize the database along with the data:
```
./reset_database.sh
```

4. Run the server:
```
./runserver.sh
```
