############################################################################
#   Copyright (c) 2013  IBS PAN Bialowieza                                 #
#   Copyright (c) 2013  Bialystok University of Technology                 #
#                                                                          #
#   This file is a part of Trapper.                                        #
#                                                                          #
#   Trapper is free software; you can redistribute it and/or modify        #
#   it under the terms of the GNU General Public License as published by   #
#   the Free Software Foundation; either version 2 of the License, or      #
#   (at your option) any later version.                                    #
#                                                                          #
#   This program is distributed in the hope that it will be useful,        #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#   GNU General Public License for more details.                           #
#                                                                          #
#   You should have received a copy of the GNU General Public License      #
#   along with this program; if not, write to the                          #
#   Free Software Foundation, Inc.,                                        #
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.              #
############################################################################

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from trapper.apps.storage.models import Resource, Collection
from trapper.apps.research.models import Project

class Message(models.Model):
	"""E-mail like messaging features among the users."""

	subject = models.CharField(max_length=50)
	"""Message subject"""

	text = models.TextField(max_length=1000)
	"""Message text (body)"""

	user_from = models.ForeignKey(User, related_name='sent_messages')
	user_to = models.ForeignKey(User, related_name='received_messages')
	date_sent = models.DateTimeField(auto_now_add=True)
	date_received = models.DateTimeField(blank=True, null=True)

	def __unicode__(self):
		return unicode("%s -> %s (sent: %s)" % (self.user_from, self.user_to, self.date_sent))

	def get_absolute_url(self):
		return reverse('messaging:message_detail', kwargs={'pk':self.pk})

class SystemNotification(models.Model):
	"""Abstract class for various types of system notifications directed towards a user."""

	name = models.CharField(max_length=50)
	resolved = models.BooleanField(default=False)

	def __unicode__(self):
		return unicode("%s (%s)" % (self.name, self.__class__.__name__))

	def resolve(self):
		self.resolved=True
		self.save()

	class Meta:
		abstract = True


# TODO: more general approach needed i.e. combine CollectionRequest and ResourceRequest
class CollectionRequest(SystemNotification):
	"""Notification about an incoming collection request for the media classification project"""

	user = models.ForeignKey(User, related_name='collection_notifications')
	message = models.ForeignKey(Message)
	project = models.ForeignKey(Project)
	collections = models.ManyToManyField(Collection, blank=True, null=True, related_name='collection_request')

	def resolve_yes(self):
		"""Resolves the request positively and creates a ProjectCollection object."""

		self.resolve()
                for collection in self.collections.all(): 
                        self.project.collections.through.objects.create(project=self.project, collection=collection)

	def resolve_no(self):
		"""Resolves the request negatively."""
		self.resolve()

class ResourceRequest(SystemNotification):
	"""Notification about an incoming collection request for the media classification project"""

	user = models.ForeignKey(User, related_name='resource_notifications')
        user_from = models.ForeignKey(User)
	message = models.ForeignKey(Message)
	resources = models.ManyToManyField(Resource, blank=True, null=True, related_name='resource_request')

	def resolve_yes(self):
		"""Resolves the request positively and assign to a user view-permissions to requested resources"""
                from guardian.shortcuts import assign_perm
		self.resolve()
                for resource in self.resources.all():
                        assign_perm("view_resource_SNG", self.user_from, resource)

	def resolve_no(self):
		"""Resolves the request negatively."""
		self.resolve()
