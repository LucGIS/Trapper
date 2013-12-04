import django_filters

from trapper.apps.storage.models import Resource

class ResourceFilter(django_filters.FilterSet):
	class Meta:
		model = Resource
		fields = ['name', 'resource_type', 'is_public']
