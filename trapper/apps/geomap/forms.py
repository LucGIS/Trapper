from django import forms

from trapper.apps.geomap.models import Location
import trapper.tools.gpxpy as gpxpy
import trapper.tools.gpxpy.gpx
from django.contrib.gis.geos import Point

class LocationUploadForm(forms.Form):
	gpx_file=forms.FileField()
	is_public = forms.BooleanField(initial=False, required=False)

	def add_locations(self, user):
		print self.cleaned_data
		gpx_file = self.cleaned_data['gpx_file']
		gpx = gpxpy.parse(gpx_file)
		no_created = 0
		for waypoint in gpx.waypoints:
			if Location.objects.filter(location_id=waypoint.name).count() == 0:
				no_created += 1
				Location.objects.create(location_id=waypoint.name,
					coordinates=Point(waypoint.longitude, waypoint.latitude), owner=user, is_public=self.cleaned_data['is_public'])
		return no_created
