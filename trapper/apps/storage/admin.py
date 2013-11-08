from django.contrib import admin
from trapper.apps.storage.models import ResourceType, Resource, ResourceCollection

class ResourceInline(admin.StackedInline):
	model = Resource
	extra = 0

class ResourceCollectionAdmin(admin.ModelAdmin):
	filter_horizontal = ('resources', )

admin.site.register(ResourceType)
admin.site.register(Resource)
admin.site.register(ResourceCollection, ResourceCollectionAdmin)
