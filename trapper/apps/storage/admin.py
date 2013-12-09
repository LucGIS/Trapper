from ajax_select import make_ajax_form

from django.contrib import admin
from trapper.apps.storage.models import ResourceType, Resource, Collection, CollectionUploadJob

class ResourceInline(admin.StackedInline):
	model = Resource
	extra = 0

class CollectionAdmin(admin.ModelAdmin):
	model = Collection
	form = make_ajax_form(Collection, {'resources': 'resource', 'owner': 'user', 'managers': 'user'})

admin.site.register(ResourceType)
admin.site.register(Resource)
admin.site.register(CollectionUploadJob)
admin.site.register(Collection, CollectionAdmin)
