from django.contrib import admin
from trapper.apps.accounts.models import UserProfile

admin.site.register(UserProfile)
