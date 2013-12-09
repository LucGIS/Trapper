from ffvideo import VideoStream
import StringIO
from PIL import Image, ImageOps
from mimetypes import guess_type

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from trapper.apps.geomap.models import Location


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
	resource_type = models.ForeignKey(ResourceType, null=True, blank=True)
	date_uploaded = models.DateTimeField(auto_now_add=True)
	location = models.ForeignKey(Location, null=True, blank=True)

	is_public = models.BooleanField("Publicly available", default=False)
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

	def update_metadata(self, commit=False):
		"""
		Updates the internal metadata about the resource:

		* mime_type - based on uploaded filetype
		* resource_type - based on the mime_type
		* thumbnail - generated from the file itself (correct mime_type is required)
		"""

		self.update_mimetype(commit=False)
		self.update_resource_type(commit=False)
		self.update_thumbnail(commit=False)

		if commit:
			self.save()

	def update_thumbnail(self, commit=False):
		"""
		Generates the thumbnail for video and image resources.
		"""
		if not self.mime_type:
			self.update_mimetype()

		if self.mime_type.startswith('video'):
			# FIXME: There's a problem with seeking in ogg files
			s = VideoStream(self.file.path)
			i = s.get_frame_at_sec(1).image()
			self._set_thumbnail(i)
		elif self.mime_type.startswith('image'):
			i = Image.open(self.file.path)
			self._set_thumbnail(i)
		# TODO/FEATUE: possibly create a soundwave thumbnail out of the audio files

		if commit:
			self.save()

	def update_resource_type(self, commit=False):
		"""
		Sets resource_type based on mime_type
		"""

		if not self.mime_type:
			self.set_mimetype()

		if self.mime_type.startswith('audio'):
			self.resource_type = ResourceType.objects.get(name="Audio")
		elif self.mime_type.startswith('video'):
			self.resource_type = ResourceType.objects.get(name="Video")
		elif self.mime_type.startswith('image'):
			self.resource_type = ResourceType.objects.get(name="Image")

		if commit:
			self.save()

	def update_mimetype(self, commit=False):
		self.mime_type = guess_type(self.file.path)[0]

		if commit:
			self.save()

class CollectionUploadJob(models.Model):
	gpx_file = models.FileField(upload_to='storage/collection/jobs/')
	resources_archive = models.FileField(upload_to='storage/collection/jobs/', null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)
	date_resolved = models.DateTimeField(null=True, blank=True)
	owner = models.ForeignKey(User)

	def __unicode__(self):
		return unicode("Added on: %s. Resolved on: %s"%(self.date_added, self.date_resolved,))

class Collection(models.Model):
	"""
	Collection of resources sharing a common origin (e.g. ownership or a recording session).
	"""

	name = models.CharField(max_length=255)
	resources = models.ManyToManyField(Resource)

	owner = models.ForeignKey(User, related_name='owned_collections')
	managers = models.ManyToManyField(User, null=True, blank=True, related_name='managed_collections')

	def __unicode__(self):
		return unicode("%s | %s" % (self.name, self.owner.username))

	def get_absolute_url(self):
		return reverse('storage:collection_detail', kwargs={'pk':self.pk})
