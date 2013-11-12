from django.contrib import admin

from trapper.apps.messaging.models import Message, ResourceCollectionRequest

# Register your models here.
admin.site.register(Message)
admin.site.register(ResourceCollectionRequest)
