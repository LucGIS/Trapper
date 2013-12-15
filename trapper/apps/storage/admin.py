############################################################################
#   Copyright (c) 2013  Trapper development team                           #
#                                                                          #
#   This file is a part of Trapper.                                        #
#                                                                          #
#   Trapper is free software; you can redistribute it and/or modify        #
#   it under the terms of the GNU General Public License as published by   #
#   the Free Software Foundation; either version 2 of the License, or      #
#   (at your option) any later version.                                    #
#                                                                          #
#   This program is distributed in the hope that it will be useful,        #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#   GNU General Public License for more details.                           #
#                                                                          #
#   You should have received a copy of the GNU General Public License      #
#   along with this program; if not, write to the                          #
#   Free Software Foundation, Inc.,                                        #
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.              #
############################################################################

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
		#process_collection_upload.delay(job.pk)
		process_collection_upload(job.pk)

run_collection_upload_task.short_description = "Retry the uploading task for selected jobs"

class CollectionUploadJobAdmin(admin.ModelAdmin):
	model = CollectionUploadJob
	actions=[run_collection_upload_task,]

admin.site.register(ResourceType)
admin.site.register(Resource)
admin.site.register(CollectionUploadJob, CollectionUploadJobAdmin)
admin.site.register(Collection, CollectionAdmin)
