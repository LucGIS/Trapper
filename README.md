# Trapper

Welcome to Tr@pper!

The project is developed using:

* Python 2.7.x
* Django 1.6

System requirements

* virtualenv
* PostgreSQL 9.1 (tested on version 9.1.9)
* Geospatial libraries: GEOS and PROJ.4
* PostGIS (preferably 2.0.x)


## Installation
Django and other python requirements will be installed locally inside the project using [virtualenv](www.virtualenv.org):

### Install system requirements

1. Install virtualenv, postgresql, geospatial libraries and PostGIS:
Debian/Ubuntu:
```
apt-get install python-virtualenv postgresql-9.1 binutils libproj-dev gdal-bin postgresql-9.1-postgis postgresql-server-dev-9.1
```

Useful:
* https://docs.djangoproject.com/en/1.6/ref/contrib/gis/install/geolibs/
* https://docs.djangoproject.com/en/1.6/ref/contrib/gis/install/postgis/

### Prepare the PostgreSQL database

2. Create spatial database

PostGIS 2.0.x:
```
su - postgres
psql trapper_db
trapper_db# CREATE EXTENSION postgis;
```

Instructions for PostGIS 1.X:
* https://docs.djangoproject.com/en/1.6/ref/contrib/gis/install/postgis/#creating-a-spatial-database-template-for-earlier-versions

3. Create a postgresql user 'trapper'
* http://www.cyberciti.biz/faq/howto-add-postgresql-user-account/
```
adduser trapper
su - postgres
psql template1
template1# CREATE USER trapper WITH PASSWORD 'trapper';
template1# GRANT ALL PRIVILEGES ON DATABASE trapper_db TO trapper;
```

### Prepare the project

4. Clone the repository and install the requirements:
```
git clone http://github.com/kiryx/Trapper.git
cd Trapper/
virtualenv env
./env/bin/pip install -r requirements.txt
```

### Run the application

5. Initialize the database along with the dummy data and run the server:
```
./reset_database.sh
./runserver.sh
```
