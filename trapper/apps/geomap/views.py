from django.contrib import messages
from django.views import generic
from django.core.urlresolvers import reverse_lazy

from braces.views import LoginRequiredMixin

from trapper.apps.geomap.models import Location
from trapper.apps.geomap.forms import LocationUploadForm

class LocationDetailView(generic.DetailView):
	"""
	Displays given location on the map.
	"""
	model = Location
	context_object_name = 'location'
	template_name = 'geomap/location_detail.html'

class LocationListView(generic.ListView):
	"""
	Displays given location on the map.
	"""
	model = Location
	context_object_name = 'locations'
	template_name = 'geomap/location_list.html'

class LocationUploadView(LoginRequiredMixin, generic.FormView):
	"""
	Uploads location data from the gpx file.
	"""

	template_name = 'geomap/location_upload.html'
	form_class = LocationUploadForm
	success_url = reverse_lazy('geomap:location_list')

	def form_valid(self, form):
		new_locs = form.add_locations(self.request.user)

		if new_locs == 0:
			messages.warning(self.request, "<strong>Upload Info:</strong> No new Locations found!")
		elif new_locs == 1:
			messages.success(self.request, "<strong>Upload Info:</strong> %d new Location was added!" % (new_locs,))
		elif new_locs > 1:
			messages.success(self.request, "<strong>Upload Info:</strong> %d new Locations were added!" % (new_locs,))

		return super(LocationUploadView, self).form_valid(form)
