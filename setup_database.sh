#!/bin/bash
# Sets up the database with the default data (init_db.py) as well as a dummy data (debug_db.py)

./env/bin/python manage.py syncdb --all --noinput
./env/bin/python manage.py migrate
./env/bin/python manage.py shell_plus < trapper/scripts/db_basic.py
./env/bin/python manage.py shell_plus < trapper/scripts/db_test.py
