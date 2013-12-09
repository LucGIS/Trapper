from django.contrib.gis.db import models
from django.contrib.auth.models import User

class Location(models.Model):
	coordinates = models.PointField(srid=4326)
	objects = models.GeoManager()
	location_id = models.CharField(max_length=100, unique=True)

	owner = models.ForeignKey(User, related_name='owned_locations')
	managers = models.ManyToManyField(User, related_name='managed_locations', null=True, blank=True)
	is_public = models.BooleanField(default=False)

	def can_view(self, user):
		return self.is_public or user == self.owner or user in self.managers.all()

	def __unicode__(self): 
		return unicode("Location ID: %s" % (self.location_id, ))

