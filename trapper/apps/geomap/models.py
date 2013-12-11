from django.contrib.gis.db import models
from django.contrib.auth.models import User

class Location(models.Model):
	"""Single location (Point) on map.
	This model is often referred by other models for establishing a spatial context.
	"""

	coordinates = models.PointField(srid=4326)
	objects = models.GeoManager()
	location_id = models.CharField(max_length=100, unique=True)

	owner = models.ForeignKey(User, related_name='owned_locations')
	managers = models.ManyToManyField(User, related_name='managed_locations', null=True, blank=True)
	is_public = models.BooleanField(default=False)

	def can_view(self, user):
		"""Determines whether user can view the location.
		:param user: user for which the test is made
		:type user: :py:class:`django.contrib.auth.User`
		:return: True if user can see the location, False otherwise
		:rtype: bool
		"""

		return self.is_public or user == self.owner or user in self.managers.all()

	def __unicode__(self): 
		return unicode("Location ID: %s" % (self.location_id, ))

