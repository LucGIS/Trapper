rm ./trapper_db.sqlite
./env/bin/python manage.py syncdb --noinput
#../env/bin/python manage.py loaddata init_camera.json
