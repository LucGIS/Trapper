from datetime import datetime
from django.shortcuts import get_object_or_404
from django.views import generic
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from trapper.apps.storage.models import Resource, ResourceCollection
from trapper.apps.storage.forms import ResourceForm, ResourceCollectionRequestForm
from trapper.apps.animal_observation.models import ClassificationProject, ClassificationProjectRole
from trapper.apps.messaging.models import Message, ResourceCollectionRequest
from trapper.commons.decorators import object_access_required


# Resource views
class UserResourceListView(generic.ListView):
	"""
	Displays the list of resources of given request.user
	"""
	model = Resource
	context_object_name = 'resources'

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(UserResourceListView, self).dispatch(*args, **kwargs)

	def get_queryset(self):
		user = get_object_or_404(User, pk=self.kwargs['user_pk'])
		return Resource.objects.filter(owner=user)

class ResourceDeleteView(generic.DeleteView):
	"""
	Given resource can be removed when user is the owner or the uploader of the resource.
	"""
	model=Resource,
	success_url='resource/list/',
	context_object_name='object',
	template_name='storage/object_confirm_delete.html'

	@method_decorator(login_required)
	@method_decorator(object_access_required(Resource, lambda u, o: u in (o.owner, o.uploader)))
	def dispatch(self, *args, **kwargs):
		return super(ResourceDeleteView, self).dispatch(*args, **kwargs)

class ResourceCreateView(generic.CreateView):
	model = Resource
	form_class= ResourceForm

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(ResourceCreateView, self).dispatch(*args, **kwargs)

	def form_valid(self, form):
		form.instance.uploader = self.request.user
		return super(ResourceCreateView, self).form_valid(form)


class UserResourceCollectionListView(generic.ListView):
	model = ResourceCollection
	context_object_name = 'collections'

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(UserResourceCollectionListView, self).dispatch(*args, **kwargs)

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

	# Template of the request message
	TEXT_TEMPLATE = "Dear %s,\nI would like to ask you for the permission to use the %s collection.\n\nBest regards,\n%s"

	# Only Project Admins and Experts can request for the resources
	REQUIRED_PROJECT_ROLES = [ClassificationProjectRole.ROLE_PROJECT_ADMIN, ClassificationProjectRole.ROLE_EXPERT]

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(UserResourceCollectionListView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context = super(ResourceCollectionRequestView, self).get_context_data(*args, **kwargs)

		# self.collection was set previously in the "get_initial" method
		context['collection'] = self.collection
		return context

	def get_initial(self, *args, **kwargs):
		self.collection = get_object_or_404(ResourceCollection, pk=self.kwargs['pk'])
		projects = ClassificationProject.objects.all()
		return {'collection_pk':self.collection.pk,'project': projects, 'text': self.TEXT_TEMPLATE % (self.collection.owner.username, self.collection.name, self.request.user.username)}

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
		form.fields['project'].queryset = projects
		return form

	def form_invalid(self, form):
		print "Invalid form"
		return super(ResourceCollectionRequestView, self).form_invalid(form)

	def form_valid(self, form):
		print "Send email, add message"
		collection = get_object_or_404(ResourceCollection, pk=form.cleaned_data['collection_pk'])
		project = form.cleaned_data['project']
		msg = Message.objects.create(subject="Request for resources", text=form.cleaned_data['text'], user_from=self.request.user,user_to=collection.owner, date_sent=datetime.now())
		ResourceCollectionRequest.objects.create(name="Request for resources", user=collection.owner, message=msg, project=project, collection=collection)
		return super(ResourceCollectionRequestView, self).form_valid(form)
