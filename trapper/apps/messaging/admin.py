from django.contrib import admin

from trapper.apps.messaging.models import Message

# Register your models here.
admin.site.register(Message)
