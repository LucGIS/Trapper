# This is the script which initializes the database with the initial data.
# 
# Apply this script using the following:
# 	./env/bin/python manage.py shell_plus < init_db.py

from django.db.models import Q
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

from trapper.apps.storage.models import ResourceType

def init():
	# Users
	u0 = User.objects.create_user('alice','alice@alice.alice','alice') # 'alice' is a superadmin
	u0.is_staff=True
	u0.is_superuser=True
	u0.save()
	
	# Groups
	g0, created = Group.objects.get_or_create(name='Admin')
	g1, created = Group.objects.get_or_create(name='Staff')
	
	# Add group permissions
	admin_cts = ContentType.objects.filter(app_label__in=['media_classification','accounts','storage','auth'])
	staff_cts = ContentType.objects.filter(app_label__in=['media_classification','storage'])
	
	# ResourceTypes
	rt1, created = ResourceType.objects.get_or_create(name="Video")
	rt2, created = ResourceType.objects.get_or_create(name="Audio")
	rt3, created = ResourceType.objects.get_or_create(name="Image")
	
	for g, cts in zip([g0, g1], [admin_cts, staff_cts]):
		query = Q()
		for ct in cts:
			query |= Q(content_type__app_label=ct.app_label, content_type__name=ct.name, codename__in=['%s_%s' % (perm_name, ct.model) for perm_name in ['change','add','delete']])
		perms = Permission.objects.filter(query)
		for p in perms:
			g.permissions.add(p)
		g.save()

if __name__ == "__builtin__":
	init()

