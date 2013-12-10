from ffvideo import VideoStream
import StringIO
from PIL import Image, ImageOps
from mimetypes import guess_type
import datetime

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
	file = models.FileField(upload_to='storage/resource/file/', null=True, blank=True)
	extra_file = models.FileField(upload_to='storage/resource/file/', null=True, blank=True)

	THUMBNAIL_SIZE = (96,96)

	MIME_CHOICES = (
		('audio/ogg', 'audio/ogg'),
		('audio/mp3', 'audio/mp3'),
		('audio/x-wav', 'audio/x-wav'),
		('audio/wav', 'audio/wav'),
		('video/mp4', 'video/mp4'),
		('video/webm', 'video/webm'),
		('video/ogg', 'video/ogg'),
		('image/jpeg', 'image/jpeg'),
	)
	mime_type = models.CharField(choices=MIME_CHOICES, max_length=255, null=True, blank=True)
	extra_mime_type = models.CharField(choices=MIME_CHOICES, max_length=255, null=True, blank=True)
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
	definition = models.FileField(upload_to='storage/collection/jobs/')
	archive = models.FileField(upload_to='storage/collection/jobs/', null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)
	date_resolved = models.DateTimeField(null=True, blank=True)
	owner = models.ForeignKey(User)

	STATUS_NEW				= 1
	STATUS_PENDING			= 2
	STATUS_RESOLVED_OK		= 3
	STATUS_RESOLVED_ERROR	= 4

	STATUS_CHIOCES = (
		(STATUS_NEW, 'New'),
		(STATUS_PENDING, 'Pending'),
		(STATUS_RESOLVED_OK, 'Resolved OK'),
		(STATUS_RESOLVED_ERROR, 'Resolved Err'),
	)
	status = models.IntegerField(choices=STATUS_CHIOCES, default=STATUS_NEW)
	error_message = models.TextField(max_length=255, null=True, blank=True)

	def set_status(self, status, error_message=None):
		self.status=status
		if error_message:
			self.error_message=error_message
		self.save()

	def resolve_as_error(self, error_message):
		self.date_resolved = datetime.datetime.now()
		self.set_status(self.STATUS_RESOLVED_ERROR, error_message)

	def resolve_as_ok(self):
		self.date_resolved = datetime.datetime.now()
		self.set_status(self.STATUS_RESOLVED_OK)

	def __unicode__(self):
		return unicode("Added on: %s, Status: %s"%(self.date_added, self.get_status_display(),))

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
