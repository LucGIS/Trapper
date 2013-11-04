from django.contrib import admin
from trapper.apps.storage.models import ResourceType, Resource, ResourceCollection

admin.site.register(ResourceType)
admin.site.register(Resource)
admin.site.register(ResourceCollection)
