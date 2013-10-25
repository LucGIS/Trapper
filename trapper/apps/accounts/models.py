from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
	user = models.OneToOneField(User)

	def __unicode__(self):
		return u"Some user"


def create_user_profile(sender, instance, created, **kwargs):
	pass

models.signals.post_save.connect(create_user_profile, sender=User)
