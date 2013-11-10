from django.shortcuts import get_object_or_404
from django.views import generic
from django.contrib.auth.models import User

from trapper.apps.storage.models import Resource, ResourceCollection


class IndexView(generic.TemplateView):
	template_name='storage/index.html'

class ResourceListView(generic.ListView):
	model = Resource
	context_object_name = 'resources'
	# inferred storage/resource_list.html template

class UserResourceListView(ResourceListView):
	"""
	UserResourceList extends ResourceList and returns a queryset filtered by ownership.
	"""

	def get_queryset(self):
		# check if user exists and return the filtered queryset
		user = get_object_or_404(User, pk=self.kwargs['user_pk'])
		return Resource.objects.filter(owner=user)

class ResourceDetailView(generic.DetailView):
	model = Resource
	# inferred: template_name='storage/resource_detail.html'

class ResourceUpdateView(generic.UpdateView):
	model = Resource
	template_name='storage/resource_update.html'

class ResourceCreateView(generic.CreateView):
	model = Resource

	# exclude the 'uploader' so it can be added manually as the request.user
	fields=['name', 'resource_type', 'owner']
	template_name='storage/resource_create.html'

	def form_valid(self, form):
		form.instance.uploader = self.request.user
		return super(ResourceCreateView, self).form_valid(form)

# ResourceCollection Views
class ResourceCollectionListView(generic.ListView):
	model = ResourceCollection
	context_object_name = 'collections'
	# inferred storage/collection_list.html template

class UserResourceCollectionListView(ResourceCollectionListView):
	"""
	UserCollectionList extends CollectionList and returns a queryset filtered by ownership.
	"""

	def get_queryset(self):
		# check if user exists and return the filtered queryset
		user = get_object_or_404(User, pk=self.kwargs['user_pk'])
		return ResourceCollection.objects.filter(owner=user)

class ResourceCollectionDetailView(generic.DetailView):
	model = ResourceCollection
	# inferred: template_name='storage/collection_detail.html'

class ResourceCollectionUpdateView(generic.UpdateView):
	model = ResourceCollection
	template_name='storage/resourcecollection_update.html'

class ResourceCollectionCreateView(generic.CreateView):
	model = ResourceCollection

	# exclude the 'uploader' so it can be added manually as the request.user
	#fields=['name', 'collection_type', 'owner']
	template_name='storage/resourcecollection_create.html'

	#def form_valid(self, form):
	#	form.instance.uploader = self.request.user
	#	return super(ResourceCollectionCreateView, self).form_valid(form)
