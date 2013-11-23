from django.contrib.gis import admin
from trapper.apps.geomap.models import Location

admin.site.register(Location, admin.OSMGeoAdmin)
