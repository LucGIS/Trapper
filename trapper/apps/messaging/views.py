from django.db.models import Q
from django.views import generic

from datetime import datetime

from trapper.apps.messaging.models import Message


class MessageDetailView(generic.DetailView):
	model = Message

	def get_object(self, *args, **kwargs):
		message = super(MessageDetailView, self).get_object(*args, **kwargs)
		if self.request.user == message.user_to:
			message.date_received = datetime.now()
			message.save()
		return message

class MessageCreateView(generic.CreateView):
	model = Message
	template_name = 'messaging/message_create.html'
	fields = ['subject','text','user_to']

	def form_valid(self, form):
		form.instance.user_from = self.request.user
		return super(MessageCreateView, self).form_valid(form)

class MessageListView(generic.ListView):
	model = Message
	context_object_name = 'message_list'

	def get_queryset(self):
		user = self.request.user
		return Message.objects.filter(Q(user_from=user) | Q(user_to=user))

class MessageInboxView(MessageListView):
	def get_queryset(self):
		return self.request.user.received_messages.all().order_by('-date_sent')

class MessageOutboxView(MessageListView):
	def get_queryset(self):
		return self.request.user.sent_messages.all().order_by('-date_sent')
