from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from trapper.apps.storage.models import Collection
from trapper.apps.media_classification.models import Project, ProjectCollection

class Message(models.Model):
	subject = models.CharField(max_length=50)
	text = models.TextField(max_length=1000)
	user_from = models.ForeignKey(User, related_name='sent_messages')
	user_to = models.ForeignKey(User, related_name='received_messages')
	date_sent = models.DateTimeField(auto_now_add=True)
	date_received = models.DateTimeField(blank=True, null=True)

	def __unicode__(self):
		return unicode("%s -> %s (sent: %s)" % (self.user_from, self.user_to, self.date_sent))

	def get_absolute_url(self):
		return reverse('messaging:message_detail', kwargs={'pk':self.pk})

class SystemNotification(models.Model):
	"""
	Abstract class for various types of system notifications directed towards a user.
	"""
	name = models.CharField(max_length=50)
	user = models.ForeignKey(User, related_name='system_notifications')
	resolved = models.BooleanField(default=False)

	def __unicode__(self):
		return unicode("%s (%s)" % (self.name, self.__class__.__name__))

	def resolve(self):
		self.resolved=True
		self.save()

	class Meta:
		abstract = True

class CollectionRequest(SystemNotification):
	message = models.ForeignKey(Message)
	project = models.ForeignKey(Project)
	collection = models.ForeignKey(Collection)

	def resolve_yes(self):
		self.resolve()
		ProjectCollection.objects.create(project=self.project, collection=self.collection, active=True)

	def resolve_no(self):
		self.resolve()
