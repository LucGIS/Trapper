# Trapper

Welcome to Tr@pper!

In order to run the application you will need the following:

* Python 2.7.x
* PostgreSQL (tested on version 9.1.9)

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

1. Create a postgresql user 'trapper' with password 'trapper'
```
su - postgres
psql template1
template1# CREATE USER trapper WITH PASSWORD 'trapper';
```

2. Create a database 'trapper_db' and give all privileges to user 'trapper'
```
template1# CREATE DATABASE trapper_db;
template1# GRANT ALL PRIVILEGES ON DATABASE trapper_db TO trapper;
```

### Run the application

3. Initialize the database along with the data:
```
./reset_database.sh
```

4. Run the server:
```
./runserver.sh
```
