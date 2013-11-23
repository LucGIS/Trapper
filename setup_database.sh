#!/bin/bash
# Sets up the database with the default data (init_db.py) as well as a dummy data (debug_db.py)

./env/bin/python manage.py syncdb --noinput
./env/bin/python manage.py shell_plus < init_db.py
./env/bin/python manage.py shell_plus < debug_db.py
