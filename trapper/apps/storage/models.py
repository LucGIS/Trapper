from ffvideo import VideoStream
import StringIO
from PIL import Image, ImageOps
from mimetypes import guess_type

from django.core.files.uploadedfile import InMemoryUploadedFile
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

	THUMBNAIL_SIZE = (96,96)

	MIME_CHOICES = (
		('audio/ogg', 'audio/ogg'),
		('audio/mp3', 'audio/mp3'),
		('audio/x-wav', 'audio/x-wav'),
		('audio/wav', 'audio/wav'),
		('video/mp4', 'video/mp4'),
		('video/ogg', 'video/ogg'),
		('image/jpeg', 'image/jpeg'),
	)
	mime_type = models.CharField(choices=MIME_CHOICES, max_length=255, null=True, blank=True)
	thumbnail = models.ImageField(upload_to='storage/resource/thumbnail/', null=True, blank=True)
	resource_type = models.ForeignKey(ResourceType)
	date_uploaded = models.DateTimeField(auto_now_add=True)

	uploader = models.ForeignKey(User, null=True, blank=True, related_name='uploaded_resources')
	owner = models.ForeignKey(User, null=True, blank=True, related_name='owned_resources')
	managers = models.ManyToManyField(User, null=True, blank=True, related_name='managed_resources')

	def __unicode__(self):
		return unicode(self.resource_type.name + ":" + self.name)

	def get_absolute_url(self):
		return reverse('storage:resource_detail', kwargs={'pk':self.pk})

	def _set_thumbnail(self, image):
		thumb_io = StringIO.StringIO()
		image = ImageOps.fit(image, self.THUMBNAIL_SIZE, Image.ANTIALIAS)
		image.save(thumb_io, format="JPEG")
		thumb_file = InMemoryUploadedFile(thumb_io, None, self.name, 'image/jpeg', thumb_io.len, None)
		self.thumbnail = thumb_file

	def update_thumbnail(self, commit=True):
		if not self.mime_type:
			self.set_mimetype()

		if self.mime_type.startswith('video'):
			s = VideoStream(self.file.path)
			i = s.get_frame_at_sec(1).image()
			self._set_thumbnail(i)
		elif self.mime_type.startswith('image'):
			i = Image.open(self.file.path)
			self._set_thumbnail(i)
		# TODO: elif: create a soundwave thumbnail

		if commit:
			self.save()

	def set_mimetype(self):
		self.mime_type = guess_type(self.file.path)[0]

class Collection(models.Model):
	name = models.CharField(max_length=255)
	resources = models.ManyToManyField(Resource)

	owner = models.ForeignKey(User, related_name='owned_collections')
	managers = models.ManyToManyField(User, null=True, blank=True, related_name='managed_collections')

	def __unicode__(self):
		return unicode("%s | %s" % (self.name, self.owner.username))

	def get_absolute_url(self):
		return reverse('storage:collection_detail', kwargs={'pk':self.pk})
