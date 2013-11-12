from datetime import datetime

from django import forms
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.views import generic
from django.shortcuts import redirect, get_object_or_404, render

from trapper.apps.messaging.models import Message, ResourceCollectionRequest


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

	def get_form(self, *args, **kwargs):
		form = super(MessageCreateView, self).get_form(*args, **kwargs)
		form.fields['text'].widget=forms.Textarea()
		form.fields['text'].label = 'Body'
		form.fields['user_to'].label = 'Recepient'
		return form

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

class SystemNotificationListView(generic.ListView):
	model=ResourceCollectionRequest
	context_object_name='notifications'
	template_name='messaging/notification_list.html'

	def get_queryset(self):
		return self.request.user.system_notifications.filter(resolved=False)

class ResolveClassificaionResourceRequestView(generic.DetailView):
	template_name="messaging/resource_request_resolve.html"
	context_object_name = "notification"
	model = ResourceCollectionRequest

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if 'resolve_yes' in self.request.POST:
			self.object.resolve_yes()
		elif 'resolve_n' in self.request.POST:
			self.object.resolve_no()
		return redirect(reverse('messaging:notification_list'))
