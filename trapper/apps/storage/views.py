############################################################################
#   Copyright (c) 2013  IBS PAN Bialowieza                                 #
#   Copyright (c) 2013  Bialystok University of Technology                 #
#                                                                          #
#   This file is a part of Trapper.                                        #
#                                                                          #
#   Trapper is free software; you can redistribute it and/or modify        #
#   it under the terms of the GNU General Public License as published by   #
#   the Free Software Foundation; either version 2 of the License, or      #
#   (at your option) any later version.                                    #
#                                                                          #
#   This program is distributed in the hope that it will be useful,        #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#   GNU General Public License for more details.                           #
#                                                                          #
#   You should have received a copy of the GNU General Public License      #
#   along with this program; if not, write to the                          #
#   Free Software Foundation, Inc.,                                        #
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.              #
############################################################################

from datetime import datetime
from django.shortcuts import get_object_or_404
from django.views import generic
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect

from braces.views import LoginRequiredMixin

from trapper.apps.storage.models import Resource, Collection, CollectionUploadJob
from trapper.apps.storage.tasks import process_collection_upload
from trapper.apps.storage.forms import ResourceForm, CollectionForm, CollectionRequestForm, CollectionUploadForm, CollectionUploadFormPart2
from trapper.apps.research.models import Project, ProjectRole
from trapper.apps.messaging.models import Message, CollectionRequest
from trapper.apps.common.decorators import object_access_required, ObjectAccessRequiredMixin

from trapper.apps.storage.filters import ResourceFilter


# Resource views

class ResourceListView(generic.ListView):
	"""Displays the list of :class:`.Resource` objects.

	This view employs the filtering features.
	For that reason, the :py:meth:`django.views.generic.ListView.get_queryset` was overloaded.
	The method filters the standard result according to the passed GET parameters.
	"""

	model = Resource
	context_object_name = 'resources'
	paginate_by = 10
	template_name = "storage/resource_list.html"

	def get_queryset(self, *args, **kwargs):
		"""Get the queryset filtered by the GET parameters (see :class:`.ResourceFilter`)."""

		qs = super(ResourceListView, self).get_queryset(*args, **kwargs)
		filtered_queryset = ResourceFilter(self.request.GET, queryset=qs)
		return filtered_queryset

	def get_context_data(self, *args, **kwargs):
		"""Returns the context data supplemented by the filtering form as well as previous filtering parameters for the initial values."""

		context = super(ResourceListView, self).get_context_data(*args, **kwargs)
		context['filtering_form'] = ResourceFilter(self.request.GET).form
		request_params = self.request.GET.copy()
		if 'page' in request_params:
			del request_params['page']
		context['previous_filter_params'] = request_params.urlencode()
		return context

class UserResourceListView(LoginRequiredMixin, ResourceListView):
	"""Displays the list of resources of given :py:class:`django.contrib.auth.models.User`
	It mirrors the functionality of :class:`.ResourceListView`,
	except it filters the queryset initally according to the resource ownership.
	"""

	def get_queryset(self):
		"""Return the queryset filtered by the resources which are owned by given user.
		"""
		user = get_object_or_404(User, pk=self.kwargs['user_pk'])
		return Resource.objects.filter(owner=user)

class ResourceDeleteView(LoginRequiredMixin, ObjectAccessRequiredMixin, generic.DeleteView):
	"""Delete view of the resource object.
	Given resource can be removed when user is the owner or the uploader of the resource.
	"""

	model=Resource
        access_func = Resource.can_delete
	success_url='resource/list/'
	context_object_name='object'
	template_name='storage/object_confirm_delete.html'

	def dispatch(self, *args, **kwargs):
		return super(ResourceDeleteView, self).dispatch(*args, **kwargs)

class ResourceUpdateView(LoginRequiredMixin, ObjectAccessRequiredMixin, generic.CreateView):
	"""Update view of the resource object.
	Given resource can be updated when user passes :func:`Resource.can_update` check.
	"""

	model = Resource
        access_func = Resource.can_update
	form_class= ResourceForm

	def dispatch(self, *args, **kwargs):
		return super(ResourceUpdateView, self).dispatch(*args, **kwargs)

class ResourceCreateView(LoginRequiredMixin, generic.CreateView):
	"""Update view of the resource object.
	Given resource can be updated when user passes an access function.
	"""

	model = Resource
	form_class= ResourceForm

	def form_valid(self, form):
		form.instance.uploader = self.request.user
		return super(ResourceCreateView, self).form_valid(form)

class UserCollectionListView(LoginRequiredMixin, generic.ListView):
	"""Collection list, initially filtered by the collections owned by given user.
	"""

	model = Collection
	context_object_name = 'collections'

	def get_queryset(self):
		"""Filters the queryset according to the user's id. """

		user = get_object_or_404(User, pk=self.kwargs['user_pk'])
		return Collection.objects.filter(owner=user)

class CollectionCreateView(LoginRequiredMixin, generic.CreateView):
	"""Collection's create view.
	Handles the creation of the Collection object.
	"""

	model = Collection
	form_class= CollectionForm

class CollectionUpdateView(LoginRequiredMixin, ObjectAccessRequiredMixin, generic.UpdateView):
	"""Collection's update view.
	Handles the update of the Collection object.
	"""

	model = Collection
        access_func = Collection.can_update
	form_class= CollectionForm
        access_func = Collection.can_update

	def dispatch(self, *args, **kwargs):
		return super(CollectionUpdateView, self).dispatch(*args, **kwargs)

# Uploading collections through YAML and archive files
class CollectionUploadViewPart2(LoginRequiredMixin, generic.FormView):
	"""Collection's upload view.
	This is the second part of the collection upload process.
	See :class:`.CollectionUploadView` for more details.
	This view handles the processing of the uploaded archive file, as well as its validation and the final
	uploading action.
	"""

	template_name = "storage/collection_upload.html"
	form_class = CollectionUploadFormPart2
	success_url = reverse_lazy('msg')

	def get_context_data(self, *args, **kwargs):
		context = super(CollectionUploadViewPart2, self).get_context_data(*args, **kwargs)
		return context

	def get_initial(self, *args, **kwargs):
		initial = {
			'job_pk':self.kwargs['pk'],
		}
		return initial

	def form_valid(self, form):
		"""Processes the uploaded archive file and delegates a
		:func:`.process_collection_upload` task.
		"""

		messages.success(self.request, "<strong>Resources uploaded!</strong> System will process your request soon.")
		job = CollectionUploadJob.objects.get(pk=form.cleaned_data['job_pk'])
		job.archive = form.cleaned_data['archive_file']
		job.save()
		process_collection_upload.delay(job.pk)
		return super(CollectionUploadViewPart2, self).form_valid(form)

class CollectionUploadView(LoginRequiredMixin, generic.FormView):
	"""This is the first controller of the two-step process of uploading a collection data (also called **batch_uploading**).
	This view displays a form with a single file upload input for the definition file.
	The file is validated and then the :class:`.CollectionUploadJob` object is created.
	"""

	template_name = "storage/collection_upload.html"
	form_class= CollectionUploadForm
	success_url = reverse_lazy('storage:collection_upload')

	def form_valid(self, form):
		"""Validates the configuration file using :meth:`.CollectionUploadForm.validate_config_file`,
		and creates the :class:`.CollectionUploadJob` object.
		"""

		err = form.validate_config_file(self.request.user)
		if err != "OK":
			messages.error(self.request, "<strong>Definition file error!</strong> %s" % (err,))
			return super(CollectionUploadView, self).form_valid(form)
		else:
			messages.success(self.request, "<strong>Success!</strong> Definition file is valid, please upload the archive file (.zip)")
			job = CollectionUploadJob.objects.create(definition=form.cleaned_data['definition_file'], owner=self.request.user)
			return HttpResponseRedirect(reverse('storage:collection_upload_2',kwargs={'pk':job.pk}))

# Deleting collections
class CollectionDeleteView(LoginRequiredMixin, ObjectAccessRequiredMixin, generic.DeleteView):
	"""This class handles the deletion of the :class:`.Collection` object.
	The collection object can be deleted by the managers and the owner of the collection.
	"""

	model = Collection
        access_func = Collection.can_update
	success_url='collection/list/'
	context_object_name='object'
	template_name='storage/object_confirm_delete.html'
        access_func = Collection.can_update

	def dispatch(self, *args, **kwargs):
		return super(CollectionDeleteView, self).dispatch(*args, **kwargs)

# Requesting collections for the research.Project model
class CollectionRequestView(LoginRequiredMixin, generic.FormView):
	"""This is the view generating the collection request page for the :class:`.Project`.
	It will only display the projects in which the user has the admin :class:`.ProjectRole`.

	"""

	template_name = "storage/collection_request.html"
	form_class = CollectionRequestForm
	success_url = reverse_lazy('storage:collection_list')

	# Template of the request message
	TEXT_TEMPLATE = "Dear %s,<br/>I would like to ask you for the permission to use the %s collection.<br/><br/>Best regards,<br/>%s"

	# Only Project Admins and Experts can request for the resources
	REQUIRED_PROJECT_ROLES = [ProjectRole.ROLE_PROJECT_ADMIN, ProjectRole.ROLE_EXPERT]

	def get_context_data(self, *args, **kwargs):
		context = super(CollectionRequestView, self).get_context_data(*args, **kwargs)

		# self.collection was set previously in the "get_initial" method
		context['collection'] = self.collection
		return context

	def get_initial(self, *args, **kwargs):
		"""Initialize the form with the projects query, as well as the collection in question.
		"""
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
		"""Gets the form the request view.

		FEATURE REQUEST:
		Logic below should be in :meth:`self.get_initial` method.
		For some reason, the initial data for 'project' does not work as expected.
		Specifically, ModelChoiceField does not initialize with a QuerySet through the constructor.
		"""
		form = super(CollectionRequestView, self).get_form(form_class, *args, **kwargs)


		project_pks = set(role.project.pk for role in self.request.user.research_roles.filter(name__in=self.REQUIRED_PROJECT_ROLES))
		projects = Project.objects.filter(pk__in=project_pks)
		form.fields['project'].queryset = projects
		return form

	def form_valid(self, form):
		"""Create a :class:`.Message` and :class:`.CollectionRequest` objects
		directed at the owner of the collection.
		"""
		print "Send email, add message"
		collection = get_object_or_404(Collection, pk=form.cleaned_data['collection_pk'])
		project = form.cleaned_data['project']
		msg = Message.objects.create(subject="Request for resources", text=form.cleaned_data['text'], user_from=self.request.user,user_to=collection.owner, date_sent=datetime.now())
		CollectionRequest.objects.create(name="Request for resources", user=collection.owner, message=msg, project=project, collection=collection)
		return super(CollectionRequestView, self).form_valid(form)
