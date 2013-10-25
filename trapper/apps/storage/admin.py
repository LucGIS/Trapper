from django.contrib import admin
from trapper.apps.storage.models import ResourceType, Resource

admin.site.register(ResourceType)
admin.site.register(Resource)
