############################################################################
#   Copyright (c) 2013  Trapper development team                           #
#                                                                          #
#   This file is a part of Trapper.                                        #
#                                                                          #
#   This program is free software; you can redistribute it and/or modify   #
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

from django.contrib import messages
from django.views import generic
from django.core.urlresolvers import reverse_lazy

from braces.views import LoginRequiredMixin

from trapper.apps.geomap.models import Location
from trapper.apps.geomap.forms import LocationUploadForm

class LocationDetailView(generic.DetailView):
	"""Displays given location on the map.
	"""
	model = Location
	context_object_name = 'location'
	template_name = 'geomap/location_detail.html'

class LocationListView(generic.ListView):
	"""Displays list of locations.
	"""
	model = Location
	context_object_name = 'locations'
	template_name = 'geomap/location_list.html'

class LocationUploadView(LoginRequiredMixin, generic.FormView):
	"""Uploads location data from the gpx file.
	"""

	template_name = 'geomap/location_upload.html'
	form_class = LocationUploadForm
	success_url = reverse_lazy('geomap:location_list')

	def form_valid(self, form):
		"""Attaches a message once the form was validated."""

		new_locs = form.add_locations(self.request.user)

		if new_locs == 0:
			messages.warning(self.request, "<strong>Upload Info:</strong> No new Locations found!")
		elif new_locs == 1:
			messages.success(self.request, "<strong>Upload Info:</strong> %d new Location was added!" % (new_locs,))
		elif new_locs > 1:
			messages.success(self.request, "<strong>Upload Info:</strong> %d new Locations were added!" % (new_locs,))

		return super(LocationUploadView, self).form_valid(form)
