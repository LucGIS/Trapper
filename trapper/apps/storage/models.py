from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class ResourceType(models.Model):
	name = models.CharField(max_length=255)

	def __unicode__(self):
		return unicode(self.name)

class Resource(models.Model):
	name = models.CharField(max_length=255)
	file = models.FileField(upload_to='storage/resource/file/')

	# TODO: mime_type as choices
	MIME_CHOICES = (
		('audio/ogg', 'audio/ogg'),
		('audio/mp3', 'audio/mp3'),
		('audio/wav', 'audio/wav'),
		('video/mp4', 'video/mp4'),
		('video/ogg', 'video/ogg'),
		('image/jpeg', 'image/jpeg'),
	)
	mime_type = models.CharField(choices=MIME_CHOICES, max_length=255)
	thumbnail = models.ImageField(upload_to='storage/resource/thumbnail/', null=True, blank=True)
	resource_type = models.ForeignKey(ResourceType)
	date_uploaded = models.DateTimeField(auto_now_add=True)
	uploader = models.ForeignKey(User, null=True, blank=True, related_name='uploaded_resources')
	owner = models.ForeignKey(User, null=True, blank=True, related_name='owned_resources')

	def __unicode__(self):
		return unicode(self.resource_type.name + ":" + self.name)

	def get_absolute_url(self):
		return reverse('storage:resource_detail', kwargs={'pk':self.pk})

class ResourceCollection(models.Model):
	name = models.CharField(max_length=255)
	resources = models.ManyToManyField(Resource)
	owner = models.ForeignKey(User, related_name='owned_collections')
	managers = models.ManyToManyField(User, null=True, blank=True, related_name='managed_collections')

	def __unicode__(self):
		return unicode("%s | %s" % (self.name, self.owner.username))

	def get_absolute_url(self):
		return reverse('storage:collection_detail', kwargs={'pk':self.pk})
