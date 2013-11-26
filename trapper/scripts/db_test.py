# This is the script which initializes the database with few instances of data for the basic models
# This script is also used by the test suite, alter it with caution.
#
# Apply this script using the following:
# 	./env/bin/python manage.py shell_plus < testing_db.py

from django.contrib.auth.models import User, Group
from django.contrib.gis.geos import Point
from trapper.apps.storage.models import ResourceType, Resource, Collection
from trapper.apps.animal_observation.models import Feature, FeatureScope, FeatureSet, Project, ResourceExtra, ProjectRole, ProjectCollection
#from trapper.apps.geomap.models import Location

def init():
	# Users
	u0 = User.objects.get(username='alice')
	
	g0 = Group.objects.get(name='Admin')
	g1 = Group.objects.get(name='Staff')
	
	u1 = User.objects.create_user('admin1','admin1@trapper.pl','admin1')
	u1.groups.add(g0)
	u2 = User.objects.create_user('staff1','staff1@trapper.pl','staff1')
	u2.groups.add(g1)
	u3 = User.objects.create_user('user1','user1@foo.com','user1')
	u4 = User.objects.create_user('user2','user2@foo.com','user2')
	
	# Feature and FeatureScope
	f1 = Feature.objects.create(name="Age", short_name="Age", feature_type=Feature.TYPE_STR)
	fs1_1 = FeatureScope.objects.create(name="Young", feature = f1)
	fs1_2 = FeatureScope.objects.create(name="Adult", feature = f1)
	fs1_3 = FeatureScope.objects.create(name="Old", feature = f1)
	
	f2 = Feature.objects.create(name="Gender", short_name="Gender", feature_type=Feature.TYPE_STR)
	fs2_1 = FeatureScope.objects.create(name="Male", feature = f2)
	fs2_2 = FeatureScope.objects.create(name="Female", feature = f2)
	
	f3 = Feature.objects.create(name="Count", short_name="Count", feature_type=Feature.TYPE_INT)
	
	f4 = Feature.objects.create(name="ApproxCount", short_name="Count", feature_type=Feature.TYPE_STR)
	fs3_1 = FeatureScope.objects.create(name="1", feature = f4)
	fs3_2 = FeatureScope.objects.create(name="2-5", feature = f4)
	fs3_3 = FeatureScope.objects.create(name="6+", feature = f4)
	
	# ResourceType, Resource
	
	rt1 = ResourceType.objects.create(name="Video")
	rt2 = ResourceType.objects.create(name="Audio")
	rt3 = ResourceType.objects.create(name="Image")
	
	r_data = (
		("video_mp4", rt1, u1, u2, 'video_1.mp4', "video/mp4" , 'video_1_thumb.jpg'),
		("video_ogv", rt1, u2, u2, 'video_1.ogv', "video/ogg" , 'video_1_thumb.jpg'),
		("audio_mp3", rt2, u3, u4, 'audio_1.mp3', "audio/mpeg", None),
		("audio_ogg", rt2, u1, u3, 'audio_2.wav', "audio/ogg" , None),
		("audio_wav", rt2, u3, u3, 'audio_3.ogg', "audio/wav" , None),
		("image_jpg", rt3, u3, u3, 'image_1.jpg', "image/jpeg", None),
	)
	
	r_filepath = "trapper/media_samples/"
	
	from django.core.files import File
	
	for name, rt, owner, uploader, filename, mime, thumb in r_data:
		r = Resource(name=name, resource_type=rt, owner=owner, uploader=uploader, mime_type=mime)
		if filename:
			with open(r_filepath + filename,'rb') as r_file:
				r.file.save(filename, File(r_file), save=False)
		if thumb:
			with open(r_filepath + thumb,'rb') as r_file:
				r.thumbnail.save(thumb, File(r_file), save=False)
		r.save()
	
	r1, r2, r3, r4, r5, r6 = Resource.objects.all()
	
	ResourceExtra.objects.filter(resource__in=[r1,r2,r3,r6]).update(public=True, cs_enabled=True)
	
	# Collection
	c1 = Collection.objects.create(name="Video2013", owner=u3)
	c1.resources.add(r1, r2, r3)
	
	c2 = Collection.objects.create(name="Audio2013", owner=u4)
	c2.resources.add(r4, r5)
	
	c3 = Collection.objects.create(name="Image2013", owner=u4)
	c3.resources.add(r6)
	
	# FeatureSet
	fs1 = FeatureSet.objects.create(name="SimpleMammalVideo", resource_type = rt1)
	fs1.features.add(f1, f2, f3)
	
	fs2 = FeatureSet.objects.create(name="SimpleMammalAudio", resource_type = rt2)
	fs2.features.add(f4)
	
	fs3 = FeatureSet.objects.create(name="SimpleMammalImage", resource_type = rt3)
	fs3.features.add(f1, f2, f3)
	
	# Project
	p1 = Project.objects.create(name="PhDProject1")
	p1.feature_sets.add(fs1, fs2, fs3)
	pc1 = ProjectCollection.objects.create(project=p1, collection=c1, active=True)
	pc2 = ProjectCollection.objects.create(project=p1, collection=c2, active=True)
	pc3 = ProjectCollection.objects.create(project=p1, collection=c3, active=True)
	
	pr0 = ProjectRole.objects.create(name=ProjectRole.ROLE_PROJECT_ADMIN, user=u0, project=p1)
	pr2 = ProjectRole.objects.create(name=ProjectRole.ROLE_EXPERT, user=u4, project=p1)
	
	## Locations
	#loc1 = Location.objects.create(coordinates=Point(23.8607, 52.7015))
	#loc2 = Location.objects.create(coordinates=Point(23.1510, 53.1367))
	#loc3 = Location.objects.create(coordinates=Point(22.3027, 54.3076))

if __name__ == "__builtin__":
	init()

