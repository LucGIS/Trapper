from datetime import datetime

from django import forms
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect

from trapper.apps.messaging.models import Message, CollectionRequest
from trapper.apps.messaging.forms import MessageForm
from trapper.apps.common.decorators import object_access_required


class MessageDetailView(generic.DetailView):
	model = Message

	@method_decorator(login_required)
	@method_decorator(object_access_required(Message, lambda u, o: u in (o.user_from, o.user_to)))
	def dispatch(self, *args, **kwargs):
		return super(MessageDetailView, self).dispatch(*args, **kwargs)

	def get_object(self, *args, **kwargs):
		message = super(MessageDetailView, self).get_object(*args, **kwargs)
		if self.request.user == message.user_to:
			message.date_received = datetime.now()
			message.save()
		return message

class MessageCreateView(generic.CreateView):
	form_class = MessageForm
	template_name = 'messaging/message_create.html'
	fields = ['subject','text','user_to']

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(MessageCreateView, self).dispatch(*args, **kwargs)

	def form_valid(self, form):
		form.instance.user_from = self.request.user
		return super(MessageCreateView, self).form_valid(form)

class MessageListView(generic.ListView):
	model = Message
	context_object_name = 'message_list'

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(MessageListView, self).dispatch(*args, **kwargs)

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
	model=CollectionRequest
	context_object_name='notifications'
	template_name='messaging/notification_list.html'

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(SystemNotificationListView, self).dispatch(*args, **kwargs)

	def get_queryset(self):
		return self.request.user.system_notifications.filter(resolved=False)

class ResolveClassificaionResourceRequestView(generic.DetailView):
	template_name="messaging/resource_request_resolve.html"
	context_object_name = "notification"
	model = CollectionRequest

	@method_decorator(login_required)
	@method_decorator(object_access_required(CollectionRequest, lambda u, o: u==o.user))
	def dispatch(self, *args, **kwargs):
		return super(ResolveClassificaionResourceRequestView, self).dispatch(*args, **kwargs)

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if 'resolve_yes' in self.request.POST:
			self.object.resolve_yes()
		elif 'resolve_n' in self.request.POST:
			self.object.resolve_no()
		return redirect(reverse('messaging:notification_list'))
