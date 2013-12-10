from ajax_select import make_ajax_form

from django.contrib import admin
from trapper.apps.storage.models import ResourceType, Resource, Collection, CollectionUploadJob
from trapper.apps.storage.tasks import process_collection_upload

class ResourceInline(admin.StackedInline):
	model = Resource
	extra = 0

class CollectionAdmin(admin.ModelAdmin):
	model = Collection
	form = make_ajax_form(Collection, {'resources': 'resource', 'owner': 'user', 'managers': 'user'})

def run_collection_upload_task(modeladmin, request, queryset):
	for job in queryset:
		process_collection_upload.delay(job.pk)

run_collection_upload_task.short_description = "Retry the uploading task for selected jobs"

class CollectionUploadJobAdmin(admin.ModelAdmin):
	model = CollectionUploadJob
	actions=[run_collection_upload_task,]

admin.site.register(ResourceType)
admin.site.register(Resource)
admin.site.register(CollectionUploadJob, CollectionUploadJobAdmin)
admin.site.register(Collection, CollectionAdmin)
