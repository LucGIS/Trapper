from django.db import models
from django.contrib.auth.models import User


class ResourceType(models.Model):
	name = models.CharField(max_length=255)

	def __unicode__(self):
		return unicode(self.name)

class Resource(models.Model):
	name = models.CharField(max_length=255)
	resource_type = models.ForeignKey(ResourceType)
	date_uploaded = models.DateTimeField(auto_now_add=True)
	uploader = models.ForeignKey(User, null=True, blank=True, related_name='uploaded_resources')
	owner = models.ForeignKey(User, null=True, blank=True, related_name='owned_resources')

	def __unicode__(self):
		return unicode(self.resource_type.name + ":" + self.name)

class ResourceCollection(models.Model):
	name = models.CharField(max_length=255)
	resources = models.ManyToManyField(Resource)

	def __unicode__(self):
		return unicode(self.name)
