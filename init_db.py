"""
This is the script which initializes the database with the initial data.

Apply this script using the following:
	./env/bin/python manage.py shell_plus < init_db.py
"""

from django.contrib.auth.models import User, Group

# Users

u0 = User.objects.create_user('alice','alice@alice.alice','alice') # 'alice' is a superadmin
u0.is_staff=True
u0.is_superuser=True
u0.save()

# Groups

g0 = Group.objects.create(name='Admin')
g1 = Group.objects.create(name='Staff')
g2 = Group.objects.create(name='User')

u0.groups.add(g0)
