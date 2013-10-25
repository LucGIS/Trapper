from django.db import models


class ResourceType(models.Model):
	name = models.CharField(max_length=255)

	def __unicode__(self):
		return unicode(self.name)

class Resource(models.Model):
	name = models.CharField(max_length=255)
	resource_type = models.ForeignKey(ResourceType)
	# date
	# gps_coords

	def __unicode__(self):
		return unicode(self.resource_type.name + ":" + self.name)
