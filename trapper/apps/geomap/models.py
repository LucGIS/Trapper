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

