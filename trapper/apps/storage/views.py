from datetime import datetime
from django.shortcuts import get_object_or_404
from django.views import generic
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy

from trapper.apps.storage.models import Resource, ResourceCollection
from trapper.apps.storage.forms import ResourceCollectionRequestForm
from trapper.apps.animal_observation.models import ClassificationProject, ClassificationProjectRole
from trapper.apps.messaging.models import Message


class UserResourceListView(generic.ListView):
	model = Resource
	context_object_name = 'resources'

	def get_queryset(self):
		user = get_object_or_404(User, pk=self.kwargs['user_pk'])
		return Resource.objects.filter(owner=user)

class ResourceCreateView(generic.CreateView):
	model = Resource

	# exclude the 'uploader' so it can be added manually as the request.user
	fields=['name', 'resource_type', 'owner']
	#template_name='storage/resource_create.html'

	def form_valid(self, form):
		form.instance.uploader = self.request.user
		return super(ResourceCreateView, self).form_valid(form)


class UserResourceCollectionListView(generic.ListView):
	model = ResourceCollection
	context_object_name = 'collections'

	def get_queryset(self):
		# check if user exists and return the filtered queryset
		user = get_object_or_404(User, pk=self.kwargs['user_pk'])
		return ResourceCollection.objects.filter(owner=user)

class ResourceCollectionRequestView(generic.FormView):
	"""
	This is the view generating the request page for a ResourceCollection.
	It will only display the Projects in which the user is the Project Admin
	"""

	template_name = "storage/resourcecollection_request.html"
	form_class = ResourceCollectionRequestForm
	success_url = reverse_lazy('storage:collection_list')

	# Template of the default request message
	TEXT_TEMPLATE = "Dear %s,\nI would like to ask you for the permission to use the %s collection.\n\nBest regards,\n%s"

	# Only Project Admins and Experts can request for the resources
	REQUIRED_PROJECT_ROLES = [ClassificationProjectRole.ROLE_PROJECT_ADMIN, ClassificationProjectRole.ROLE_EXPERT]

	def get_context_data(self, *args, **kwargs):
		context = super(ResourceCollectionRequestView, self).get_context_data(*args, **kwargs)

		# self.collection was set previously in the "get_initial" method
		context['collection'] = self.collection
		return context

	def get_initial(self, *args, **kwargs):
		self.collection = get_object_or_404(ResourceCollection, pk=self.kwargs['pk'])
		projects = ClassificationProject.objects.all()
		return {'collection_pk':self.collection.pk,'projects': projects, 'text': self.TEXT_TEMPLATE % (self.collection.owner.username, self.collection.name, self.request.user.username)}

	def get_form(self, form_class, *args, **kwargs):
		form = super(ResourceCollectionRequestView, self).get_form(form_class, *args, **kwargs)

		##
		# FIXME:
		# Logic below should be in get_initial method.
		# For some reason, the initial for 'projects' does not work as expected
		# Specifically, ModelChoiceField is hard to initialize with a queryset through the contstructor
		##

		project_pks = set(role.project.pk for role in self.request.user.classificationprojectrole_set.filter(name__in=self.REQUIRED_PROJECT_ROLES))
		projects = ClassificationProject.objects.filter(pk__in=project_pks)
		form.fields['projects'].queryset = projects
		return form

	def form_invalid(self, form):
		print "Invalid form"
		return super(ResourceCollectionRequestView, self).form_invalid(form)

	def form_valid(self, form):
		print "Send email, add message"
		collection = get_object_or_404(ResourceCollection, pk=form.cleaned_data['collection_pk'])
		Message.objects.create(subject="Request for resources", text=form.cleaned_data['text'], user_from=self.request.user,user_to=collection.owner, date_sent=datetime.now())
		return super(ResourceCollectionRequestView, self).form_valid(form)
