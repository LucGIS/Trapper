from django.contrib.gis.db import models

class Location(models.Model):
    coordinates = models.PointField(srid=4326, blank=True, null=True)
    objects = models.GeoManager()
    def __unicode__(self): 
		return unicode("Id: %s" % (self.pk, ))

