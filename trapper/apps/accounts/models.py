from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
	user = models.OneToOneField(User)
	mobile = models.CharField(max_length=100)

	def __unicode__(self):
		return unicode("%s" % (self.user.username,))


def create_user_profile(sender, instance, created, **kwargs):
	if created:
		profile, created = UserProfile.objects.get_or_create(user=instance, mobile="555")
	pass

models.signals.post_save.connect(create_user_profile, sender=User)
