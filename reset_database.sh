./env/bin/python manage.py flush --noinput
./env/bin/python manage.py syncdb --noinput
./env/bin/python manage.py shell_plus < init_db.py
./env/bin/python manage.py shell_plus < debug_db.py
./env/bin/python manage.py runserver 0.0.0.0:8000
