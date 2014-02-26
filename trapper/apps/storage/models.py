############################################################################
#   Copyright (c) 2013  IBS PAN Bialowieza                 #
#   Copyright (c) 2013  Bialystok University of Technology         #
#                                      #
#   This file is a part of Trapper.                    #
#                                      #
#   Trapper is free software; you can redistribute it and/or modify    #
#   it under the terms of the GNU General Public License as published by   #
#   the Free Software Foundation; either version 2 of the License, or      #
#   (at your option) any later version.                    #
#                                      #
#   This program is distributed in the hope that it will be useful,    #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of     #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the      #
#   GNU General Public License for more details.               #
#                                      #
#   You should have received a copy of the GNU General Public License      #
#   along with this program; if not, write to the              #
#   Free Software Foundation, Inc.,                    #
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.          #
############################################################################

"""Module for storage application.

"""

from mimetypes import guess_type
import datetime
import itertools

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from guardian import models as Gmodels
from guardian.shortcuts import get_perms

from easy_thumbnails.fields import ThumbnailerField
from easy_thumbnails.signals import saved_file
from easy_thumbnails.signal_handlers import generate_aliases_global

from trapper.apps.geomap.models import Location


class Resource(models.Model):
    """Model describing a single resource.
    Resource is usually a video or an image.
    In order to provide some robust playback features, it is possible to upload
    up to two separate resource files (e.g. in both *.mp4* and *.webm* format for better browser compatibility).
    """

    name = models.CharField(max_length=255)
    file = ThumbnailerField(upload_to='storage/resource/file/', null=True, blank=True)
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

    TYPE_VIDEO = "V"
    TYPE_IMAGE = "I"
    TYPE_AUDIO = "A"

    TYPE_CHOICES = (
        (TYPE_VIDEO, 'Video'),
        (TYPE_IMAGE, 'Image'),
        (TYPE_AUDIO, 'Audio'),
    )
    STATUS_CHOICES = (
        ('Private', 'Private'),
        ('OnDemand', 'On demand'),
        ('Public', 'Public'),
    )

    mime_type = models.CharField(choices=MIME_CHOICES, max_length=255, null=True, blank=True)
    extra_mime_type = models.CharField(choices=MIME_CHOICES, max_length=255, null=True, blank=True)
    resource_type = models.CharField(choices=TYPE_CHOICES, max_length=1, null=True, blank=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    date_recorded = models.DateTimeField(null=True, blank=True)
    location = models.ForeignKey(Location, null=True, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=8, default='OnDemand')
    #is_public = models.BooleanField("Publicly available", default=False, help_text="Make it public")
    #is_private = models.BooleanField("Private", default=False, help_text="Make it private (only owner and managers can see this resource)")
    uploader = models.ForeignKey(User, null=True, blank=True, related_name='uploaded_resources')
    owner = models.ForeignKey(User, null=True, blank=True, related_name='owned_resources')
    managers = models.ManyToManyField(User, null=True, blank=True, related_name='managed_resources')

    class Meta:
        permissions = (
            ('view_resource_SNG', 'View Resource - Single'),
            ('view_resource_PRO', 'View Resource - In Project Collection'),
        )

    def __unicode__(self):
        return unicode(str(self.get_resource_type_display()) + ":" + self.name)

    def get_absolute_url(self):
        """Get the absolute url for an instance of this model."""
        return reverse('storage:resource_detail', kwargs={'pk':self.pk})


    def can_view(self, user):
        if self.status == 'Public':
            return True
        else:
            perms = get_perms(user, self)
            return  user in (self.owner, self.uploader) or user in self.managers.all() or 'view_resource_PRO' in perms or 'view_resource_SNG' in perms

    # helper function; has project-based access; can return 'checkset' which can tell you which collections are shared between resource and user
    def has_access(self, user, return_checkset=False):
        from trapper.apps.research.models import Project
        projects = user.research_roles.values_list('project_id', flat=True)
        # check if resource belongs to any collection of any project that user is part of
        checkset = set(self.collection_set.values_list('id', flat=True)) & set(list(itertools.chain(*[Project.objects.get(pk=k).collections.values_list('id', flat=True) for k in projects])))
        if return_checkset:
            return checkset
        elif checkset:
            return True
        else:
            return False

    def can_update_or_delete(self, user):
        return user in (self.owner, self.uploader) or user in self.managers.all()

    def can_delete(self, user):
        return self.can_update_or_delete(user)

    def can_update(self, user):
        return self.can_update_or_delete(user)

    def is_used_by_other_collection(self, user):
        # is used by other collection
        if self.collection_set.all().exclude(owner=user):
            return True
        else:
            return False

    def is_used_by_other_research_project(self, user):
        # get all research projects where user plays admin role
        admin_in_projects = [k.project for k in user.research_roles.filter(name="A")]
        # check if other projects use a resource\
        if set(list(itertools.chain(*[k.research_projects.all() for k in self.collection_set.all()]))) - set(admin_in_projects):
            return True
        else:
            return False

    def can_be_deleted(self, user):
        return not(self.is_used_by_other_collection(user) or self.is_used_by_other_research_project(user))

    def move2archive(self):
        user = User.objects.get(username="archive")
        self.owner, self.uploader = (user, user)
        self.managers.remove()
        self.save()

    def update_metadata(self, commit=False):
        """Updates the internal metadata about the resource.

        :param commit: States whether to perform self.save() at the end of this method
        :type commit: bool
        """

        self.update_mimetype(commit=False)
        self.update_resource_type(commit=False)

        if commit:
            self.save()

    def update_resource_type(self, commit=False):
        """Sets resource_type based on mime_type.

        :param commit: States whether to perform self.save() at the end of this method
        :type commit: bool
        """

        if not self.mime_type:
            self.set_mimetype()

        if self.mime_type.startswith('audio'):
            self.resource_type = Resource.TYPE_AUDIO
        elif self.mime_type.startswith('video'):
            self.resource_type = Resource.TYPE_VIDEO
        elif self.mime_type.startswith('image'):
            self.resource_type = Resource.TYPE_IMAGE

        if commit:
            self.save()

    def update_mimetype(self, commit=False):
        """Sets the mime_type for the resource.
        This is obtained by trying to *guess* the mime type based on the resource file.

        :param commit: States whether to perform self.save() at the end of this method
        :type commit: bool
        """
        self.mime_type = guess_type(self.file.path)[0]

        if commit:
            self.save()

#TODO: make a task run by celery
saved_file.connect(generate_aliases_global)


class CollectionUploadJob(models.Model):
    """Job-like model for the collection upload requests.
    A single CollectionUploadJob instance contains both the definition of the collections, as well as the archive file with the data.
    """

    definition = models.FileField(upload_to='storage/collection/jobs/')
    archive = models.FileField(upload_to='storage/collection/jobs/', null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_resolved = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(User)

    STATUS_NEW        = 1
    STATUS_PENDING    = 2
    STATUS_RESOLVED_OK    = 3
    STATUS_RESOLVED_ERROR = 4

    STATUS_CHIOCES = (
        (STATUS_NEW, 'New'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_RESOLVED_OK, 'Resolved OK'),
        (STATUS_RESOLVED_ERROR, 'Resolved Err'),
    )
    status = models.IntegerField(choices=STATUS_CHIOCES, default=STATUS_NEW)
    error_message = models.TextField(max_length=255, null=True, blank=True)

    def set_status(self, status, error_message=None):
        """Sets the status for the job.

        :param status: status code
        :type status: int
        :param error_message: optional error message
        :type error_message: str
        """

        self.status=status
        if error_message:
            self.error_message=error_message
        self.save()

    def resolve_as_error(self, error_message):
        """Shortcut function for resolving given job with an error.

        :param error_message: mandatory error_message
        :type error_message: str
        """

        self.date_resolved = datetime.datetime.now()
        self.set_status(self.STATUS_RESOLVED_ERROR, error_message)

    def resolve_as_ok(self):
        """Shortcut function for resolving given job with a success.
        """

        self.date_resolved = datetime.datetime.now()
        self.set_status(self.STATUS_RESOLVED_OK)

    def __unicode__(self):
        return unicode("Added on: %s, Status: %s"%(self.date_added, self.get_status_display(),))

class Collection(models.Model):
    """Collection of resources sharing a common origin (e.g. ownership or a recording session).

    At core, this model is just an aggregation of :class:`.Resource` objects.
    Additionally, permissions to alter given collection are given only to the users belonging to *managers* or the *owner*.
    """
    STATUS_CHOICES = (
        ('Private', 'Private'),
        ('OnDemand', 'On demand'),
        ('Public', 'Public'),
    )
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=2000, null=True, blank=True)
    resources = models.ManyToManyField(Resource)
    owner = models.ForeignKey(User, related_name='owned_collections')
    uploader = models.ForeignKey(User, null=True, blank=True, related_name='uploaded_collections')
    managers = models.ManyToManyField(User, null=True, blank=True, related_name='managed_collections', help_text='test')
    status = models.CharField(choices=STATUS_CHOICES, max_length=8, default='OnDemand')
    #is_public = models.BooleanField("Publicly available", default=False, help_text="Make it public")
    #is_private = models.BooleanField("Private", default=False, help_text="Make it private (only owner and managers can see this collection)")


    def __unicode__(self):
        return unicode("%s | %s" % (self.name, self.owner.username))

    def get_absolute_url(self):
        """Get the absolute url for an instance of this model."""

        return reverse('storage:collection_detail', kwargs={'pk':self.pk})

    def can_update_or_delete(self, user):
        return user == self.owner or user in self.managers.all()

    def can_update(self, user):
        return self.can_update_or_delete(user)

    def can_delete(self, user):
        return self.can_update_or_delete(user)


# GUARDIAN stuff

class ResourceUserObjectPermission(Gmodels.UserObjectPermissionBase):
    content_object = models.ForeignKey(Resource)

class ResourceGroupObjectPermission(Gmodels.GroupObjectPermissionBase):
    content_object = models.ForeignKey(Resource)

class CollectionUserObjectPermission(Gmodels.UserObjectPermissionBase):
    content_object = models.ForeignKey(Collection)

class CollectionGroupObjectPermission(Gmodels.GroupObjectPermissionBase):
    content_object = models.ForeignKey(Collection)


# register signals
from signals import collection_m2m_changed
from django.db.models.signals import m2m_changed

m2m_changed.connect(collection_m2m_changed, sender=Collection.resources.through)

