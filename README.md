# Trapper

Welcome to Tr@pper!

The project is developed using:

* Python 2.7.x
* Django 1.6

Database backend:

* PostgreSQL 9.1 (tested on version 9.1.9)
* PostGIS

## Installation

Django and other requirements will be installed locally inside the project using [virtualenv](www.virtualenv.org):

### Prepare the project

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
### Prepare the PostgreSQL database
4. Install PosgreSQL:
```
sudo apt-get install postgresql-9.1
```

3. Create a postgresql user 'trapper' with password 'trapper' and the database 'trapper_db'
(userful: http://www.cyberciti.biz/faq/howto-add-postgresql-user-account/)
```
adduser trapper
passwd trapper
su - postgres
psql template1
template1# CREATE USER trapper WITH PASSWORD 'trapper';
template1# CREATE DATABASE trapper_db;
template1# GRANT ALL PRIVILEGES ON DATABASE trapper_db TO trapper;
```

5. Install the required Geospatial libraries (Debian/Ubuntu):
(useful: https://docs.djangoproject.com/en/1.6/ref/contrib/gis/install/geolibs/)
```
sudo apt-get install binutils libproj-dev gdal-bin
```

6. Install PostGIS
(useful: https://docs.djangoproject.com/en/1.6/ref/contrib/gis/install/postgis/)
```
sudo apt-get install postgresql-9.1-postgis postgresql-server-dev-9.1
```

7. Create spatial database
(useful: https://docs.djangoproject.com/en/1.6/ref/contrib/gis/install/postgis/#creating-a-spatial-database-with-postgis-2-0-and-postgresql-9-1)
```
su - postgres
psql trapper_db
trapper_db# CREATE EXTENSION postgis;
```

### Run the application

8. Initialize the database along with the data:
```
./reset_database.sh
```

9. Run the server:
```
./runserver.sh
```
