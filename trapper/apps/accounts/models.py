from django.db import models
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse


class UserProfile(models.Model):
	user = models.OneToOneField(User)
	mobile = models.CharField(max_length=100)

	def __unicode__(self):
		return unicode("%s" % (self.user.username,))

	def get_absolute_url(self):
		return reverse('accounts:userprofile_detail', kwargs={'pk':self.pk})

def create_user_profile(sender, instance, created, **kwargs):
	if created:
		profile, created = UserProfile.objects.get_or_create(user=instance, mobile="")

def set_user_as_staff(sender, instance, action, **kwargs):
	"""
	Connects to the pre_save signal of the User model.
	Sets the is_staff flag on user by default for certain auth.models.Group instances.
	"""

	# Check the type of the Many-To-Many signal
	if action in ("post_add", "post_remove", "post_clear",):
		# User is staff when he belongs to any of the groups
		if instance.groups.all().count() > 0:
			User.objects.filter(pk=instance.pk).update(is_staff=True)
		else:
			User.objects.filter(pk=instance.pk).update(is_staff=False)

models.signals.post_save.connect(create_user_profile, sender=User)
models.signals.m2m_changed.connect(set_user_as_staff, sender=User.groups.through)
