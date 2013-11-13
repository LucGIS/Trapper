from ajax_select import make_ajax_form

from django.contrib import admin
from trapper.apps.storage.models import ResourceType, Resource, ResourceCollection

class ResourceInline(admin.StackedInline):
	model = Resource
	extra = 0

class ResourceCollectionAdmin(admin.ModelAdmin):
	model = ResourceCollection
	form = make_ajax_form(ResourceCollection, {'resources': 'resource', 'owner': 'user', 'managers': 'user'})

admin.site.register(ResourceType)
admin.site.register(Resource)
admin.site.register(ResourceCollection, ResourceCollectionAdmin)
