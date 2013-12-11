from django.db import models
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse


class UserProfile(models.Model):
	"""Extends the :py:class:`.User` class through a OneToOneField.
	Additionally, it provides some extra methods for other applications such as :ref:`trapper.apps.messaging`.
	"""

	user = models.OneToOneField(User)
	mobile = models.CharField(max_length=100, null=True, blank=True)

	def __unicode__(self):
		return unicode("%s" % (self.user.username,))

	def get_absolute_url(self):
		return reverse('accounts:userprofile_detail', kwargs={'pk':self.pk})

	def has_unread_messages(self):
		"""Checks whether user has any unread messages
		(see :class:`trapper.apps.messaging.models.Message`).
		"""

		return self.user.received_messages.filter(date_received=None).count() + self.user.system_notifications.filter(resolved=False).count() > 0

	def count_unread_messages(self):
		"""Returns the number of unread messages.
		(see :class:`trapper.apps.messaging.models.Message`).
		"""

		return self.user.received_messages.filter(date_received=None).count()

	def count_unresolved_system_notifications(self):
		"""Returns the number of unresolved system notifications.
		(see :class:`trapper.apps.messaging.models.SystemNotification`).
		"""

		return self.user.system_notifications.filter(resolved=False).count()

def create_user_profile(sender, instance, created, **kwargs):
	if created:
		profile, created = UserProfile.objects.get_or_create(user=instance)

def set_user_as_staff(sender, instance, action, **kwargs):
	"""Connects to the pre_save signal of the User model.
	Sets the is_staff flag on user by default for certain auth.models.Group instances.
	This functionality is redundant as model permissions are not relevant.
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
