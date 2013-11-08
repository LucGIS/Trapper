"""
This is the script which initializes the database with few instances of data for the basic models such as Resource etc.

Apply this script using the following:
	./env/bin/python manage.py shell_plus < init_db.py
"""

from django.contrib.auth.models import User, Group
from trapper.apps.storage.models import ResourceType, Resource, ResourceCollection
from trapper.apps.animal_observation.models import AnimalFeature, AnimalFeatureScope, ResourceFeatureSet, ClassificationProject, ResourceExtra, ClassificationProjectRole, ClassificationProjectResourceCollection

# Users
u0 = User.objects.get(username='alice')

g0 = Group.objects.get(name='Admin')
g1 = Group.objects.get(name='Staff')

u1 = User.objects.create_user('admin1','admin1@trapper.pl','admin1')
u1.groups.add(g0)
u2 = User.objects.create_user('staff1','admin1@trapper.pl','staff1')
u2.groups.add(g1)
u3 = User.objects.create_user('user1','user1@gmail.com','user1')
u4 = User.objects.create_user('user2','user1@gmail.com','user2')

# AnimalFeature and AnimalFeatureScope
af1 = AnimalFeature.objects.create(name="Age", short_name="Age", feature_type=AnimalFeature.TYPE_STR)
afs1_1 = AnimalFeatureScope.objects.create(name="Young", feature = af1)
afs1_2 = AnimalFeatureScope.objects.create(name="Adult", feature = af1)
afs1_3 = AnimalFeatureScope.objects.create(name="Old", feature = af1)

af2 = AnimalFeature.objects.create(name="Gender", short_name="Gender", feature_type=AnimalFeature.TYPE_STR)
afs2_1 = AnimalFeatureScope.objects.create(name="Male", feature = af2)
afs2_2 = AnimalFeatureScope.objects.create(name="Female", feature = af2)

af3 = AnimalFeature.objects.create(name="Count", short_name="Count", feature_type=AnimalFeature.TYPE_INT)

af4 = AnimalFeature.objects.create(name="ApproxCount", short_name="Count", feature_type=AnimalFeature.TYPE_STR)
afs3_1 = AnimalFeatureScope.objects.create(name="1", feature = af4)
afs3_2 = AnimalFeatureScope.objects.create(name="2-5", feature = af4)
afs3_3 = AnimalFeatureScope.objects.create(name="6+", feature = af4)

# ResourceType, Resource

rt1 = ResourceType.objects.create(name="Video")
rt2 = ResourceType.objects.create(name="Audio")

r1 = Resource.objects.create(name="VIDEO001.mp4", resource_type=rt1, owner=u1, uploader=u2)
r2 = Resource.objects.create(name="VIDEO002.mp4", resource_type=rt1, owner=u2, uploader=u2)
r3 = Resource.objects.create(name="VIDEO003.mp4", resource_type=rt1, owner=u3, uploader=u4)
r4 = Resource.objects.create(name="AUDIO001.mp4", resource_type=rt2, owner=u1, uploader=u3)
r5 = Resource.objects.create(name="AUDIO002.mp4", resource_type=rt2, owner=u3, uploader=u3)
r6 = Resource.objects.create(name="AUDIO003.mp4", resource_type=rt2, owner=u3, uploader=u3)

ResourceExtra.objects.filter(resource__in=[r1,r2,r6]).update(public=True, cs_enabled=True)

# ResourceCollection
rc1 = ResourceCollection.objects.create(name="Video2013")
rc1.resources.add(r1, r2, r3)

rc2 = ResourceCollection.objects.create(name="Audio2013")
rc2.resources.add(r4, r5, r6)

# ResourceFeatureSet
rfs1 = ResourceFeatureSet.objects.create(name="SimpleMammalVideo", resource_type = rt1)
rfs1.features.add(af1, af2, af3)

rfs2 = ResourceFeatureSet.objects.create(name="SimpleMammalAudio", resource_type = rt2)
rfs2.features.add(af4)

# ClassificationProject
cp1 = ClassificationProject.objects.create(name="PhDProject1")
cp1.resource_feature_sets.add(rfs1, rfs2)
cprc1 = ClassificationProjectResourceCollection.objects.create(project=cp1, collection=rc2, active=True)

cpr1 = ClassificationProjectRole.objects.create(name=ClassificationProjectRole.ROLE_PROJECT_ADMIN, user=u3, project=cp1)
cpr2 = ClassificationProjectRole.objects.create(name=ClassificationProjectRole.ROLE_EXPERT, user=u4, project=cp1)
