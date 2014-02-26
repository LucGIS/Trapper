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

from django import forms

from trapper.apps.geomap.models import Location
import trapper.tools.gpxpy as gpxpy
from django.contrib.gis.geos import Point

class LocationUploadForm(forms.Form):
    """Upload form for the locations file."""

    gpx_file=forms.FileField()
    is_public = forms.BooleanField(initial=False, required=False)

    def add_locations(self, user):
        """Parses the .gpx file and looks for the locations which aren't available in the system yet.

        :param user: user adding the locations (made the Location's owner)
        :type user: :py:class:`django.contrib.auth.models.User`
        """

        print self.cleaned_data
        gpx_file = self.cleaned_data['gpx_file']
        gpx = gpxpy.parse(gpx_file)
        no_created = 0
        for waypoint in gpx.waypoints:
            if Location.objects.filter(location_id=waypoint.name).count() == 0:
                no_created += 1
                Location.objects.create(location_id=waypoint.name,
                                        coordinates=Point(waypoint.longitude, waypoint.latitude),
                                        owner=user,
                                        is_public=self.cleaned_data['is_public']
                )
        return no_created
