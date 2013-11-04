rm ./trapper/trapper_db.sqlite
./env/bin/python manage.py syncdb --noinput
#../env/bin/python manage.py loaddata init_camera.json
./env/bin/python manage.py shell_plus < init_db.py
./env/bin/python manage.py shell_plus < debug_db.py
