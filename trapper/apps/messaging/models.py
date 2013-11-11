from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class Message(models.Model):
	subject = models.CharField(max_length=50)
	text = models.CharField(max_length=1000)
	user_from = models.ForeignKey(User, related_name='sent_messages')
	user_to = models.ForeignKey(User, related_name='received_messages')
	date_sent = models.DateTimeField(auto_now_add=True)
	date_received = models.DateTimeField(blank=True, null=True)

	def __unicode__(self):
		return unicode("%s -> %s (sent: %s)" % (self.user_from, self.user_to, self.date_sent))

	def get_absolute_url(self):
		return reverse('messaging:message_detail', kwargs={'pk':self.pk})
