from django.views import generic

from trapper.apps.geomap.models import Location

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
