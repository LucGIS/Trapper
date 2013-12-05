from datetime import datetime
from django.shortcuts import get_object_or_404
from django.views import generic
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from trapper.apps.storage.models import Resource, Collection
from trapper.apps.storage.forms import ResourceForm, CollectionForm, CollectionRequestForm
from trapper.apps.media_classification.models import Project, ProjectRole
from trapper.apps.messaging.models import Message, CollectionRequest
from trapper.commons.decorators import object_access_required

from trapper.apps.storage.filters import ResourceFilter


# Resource views

class ResourceListView(generic.ListView):
	"""
	Displays the list of resources
	"""
	model = Resource
	context_object_name = 'resources'
	paginate_by = 10
	template_name = "storage/resource_list.html"

	def get_context_data(self, *args, **kwargs):
		context = super(ResourceListView, self).get_context_data(*args, **kwargs)
		filtered_queryset = ResourceFilter(self.request.GET, queryset=self.get_queryset())
		context['resources'] = filtered_queryset
		return context

class UserResourceListView(ResourceListView):
	"""
	Displays the list of resources of given request.user
	"""

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(ResourceListView, self).dispatch(*args, **kwargs)

	def get_queryset(self):
		user = get_object_or_404(User, pk=self.kwargs['user_pk'])
		return Resource.objects.filter(owner=user)

def can_update_or_delete_resource(user, resource):
	return user in (resource.owner, resource.uploader) or user in resource.managers.all()

class ResourceDeleteView(generic.DeleteView):
	"""
	Given resource can be removed when user is the owner or the uploader of the resource.
	"""
	model=Resource
	success_url='resource/list/'
	context_object_name='object'
	template_name='storage/object_confirm_delete.html'

	@method_decorator(login_required)
	@method_decorator(object_access_required(Resource, can_update_or_delete_resource))
	def dispatch(self, *args, **kwargs):
		return super(ResourceDeleteView, self).dispatch(*args, **kwargs)

class ResourceUpdateView(generic.CreateView):
	model = Resource
	form_class= ResourceForm

	@method_decorator(login_required)
	@method_decorator(object_access_required(Resource, can_update_or_delete_resource))
	def dispatch(self, *args, **kwargs):
		return super(ResourceUpdateView, self).dispatch(*args, **kwargs)

class ResourceCreateView(generic.CreateView):
	model = Resource
	form_class= ResourceForm

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(ResourceCreateView, self).dispatch(*args, **kwargs)

	def form_valid(self, form):
		form.instance.uploader = self.request.user
		return super(ResourceCreateView, self).form_valid(form)


class UserCollectionListView(generic.ListView):
	model = Collection
	context_object_name = 'collections'

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(UserCollectionListView, self).dispatch(*args, **kwargs)

	def get_queryset(self):
		# check if user exists and return the filtered queryset
		user = get_object_or_404(User, pk=self.kwargs['user_pk'])
		return Collection.objects.filter(owner=user)

class CollectionCreateView(generic.CreateView):
	model = Collection
	form_class= CollectionForm

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(CollectionCreateView, self).dispatch(*args, **kwargs)

def can_update_or_delete_collection(user, collection):
	# Method used as a permission test for the decorator
	return user == collection.owner or user in collection.managers.all()

class CollectionUpdateView(generic.UpdateView):
	model = Collection
	form_class= CollectionForm

	@method_decorator(login_required)
	@method_decorator(object_access_required(Collection, can_update_or_delete_collection))
	def dispatch(self, *args, **kwargs):
		return super(CollectionUpdateView, self).dispatch(*args, **kwargs)

class CollectionDeleteView(generic.DeleteView):
	model = Collection
	success_url='collection/list/'
	context_object_name='object'
	template_name='storage/object_confirm_delete.html'

	@method_decorator(login_required)
	@method_decorator(object_access_required(Collection, can_update_or_delete_collection))
	def dispatch(self, *args, **kwargs):
		return super(CollectionDeleteView, self).dispatch(*args, **kwargs)

class CollectionRequestView(generic.FormView):
	"""
	This is the view generating the request page for a Collection.
	It will only display the Projects in which the user is the Project Admin
	"""

	template_name = "storage/collection_request.html"
	form_class = CollectionRequestForm
	success_url = reverse_lazy('storage:collection_list')

	# Template of the request message
	TEXT_TEMPLATE = "Dear %s,\nI would like to ask you for the permission to use the %s collection.\n\nBest regards,\n%s"

	# Only Project Admins and Experts can request for the resources
	REQUIRED_PROJECT_ROLES = [ProjectRole.ROLE_PROJECT_ADMIN, ProjectRole.ROLE_EXPERT]

	# TODO: Check for the permission only for the authentication
	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(CollectionRequestView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context = super(CollectionRequestView, self).get_context_data(*args, **kwargs)

		# self.collection was set previously in the "get_initial" method
		context['collection'] = self.collection
		return context

	def get_initial(self, *args, **kwargs):
		self.collection = get_object_or_404(Collection, pk=self.kwargs['pk'])
		projects = Project.objects.all()
		initial = {
			'collection_pk':self.collection.pk,
			'project': projects,
			'text': self.TEXT_TEMPLATE % (
				self.collection.owner.username,
				self.collection.name,
				self.request.user.username
			)
		}
		return initial

	def get_form(self, form_class, *args, **kwargs):
		form = super(CollectionRequestView, self).get_form(form_class, *args, **kwargs)

		##
		# FIXME:
		# Logic below should be in get_initial method.
		# For some reason, the initial for 'projects' does not work as expected
		# Specifically, ModelChoiceField is hard to initialize with a QuerySet through the constructor
		##

		project_pks = set(role.project.pk for role in self.request.user.projectrole_set.filter(name__in=self.REQUIRED_PROJECT_ROLES))
		projects = Project.objects.filter(pk__in=project_pks)
		form.fields['project'].queryset = projects
		return form

	def form_invalid(self, form):
		print "Invalid form"
		return super(CollectionRequestView, self).form_invalid(form)

	def form_valid(self, form):
		print "Send email, add message"
		collection = get_object_or_404(Collection, pk=form.cleaned_data['collection_pk'])
		project = form.cleaned_data['project']
		msg = Message.objects.create(subject="Request for resources", text=form.cleaned_data['text'], user_from=self.request.user,user_to=collection.owner, date_sent=datetime.now())
		CollectionRequest.objects.create(name="Request for resources", user=collection.owner, message=msg, project=project, collection=collection)
		return super(CollectionRequestView, self).form_valid(form)
