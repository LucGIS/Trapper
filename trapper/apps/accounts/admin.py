from django.contrib import admin
from django.contrib.auth.models import Permission, ContentType

from trapper.apps.accounts.models import UserProfile


admin.site.register(UserProfile)
admin.site.register(Permission)
admin.site.register(ContentType)
