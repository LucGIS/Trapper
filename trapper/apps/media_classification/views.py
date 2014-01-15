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

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.forms.models import inlineformset_factory
from django.views import generic
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404

from braces.views import LoginRequiredMixin
from extra_views import InlineFormSet, CreateWithInlinesView, UpdateWithInlinesView, NamedFormsetsMixin

from trapper.apps.media_classification.models import Feature, FeatureAnswer, FeatureScope, Project, Classification, ClassificationRow, ProjectRole, ProjectCollection, FeatureSet, Sequence
from trapper.apps.research.models import Project as RProject
from trapper.apps.storage.models import Resource
from trapper.apps.media_classification.forms import ProjectForm, ProjectCollectionFormset, ProjectRoleFormset, FeatureSetForm, SequenceForm
from trapper.apps.common.decorators import object_access_required, ObjectAccessRequiredMixin


# FeatureSet views

class FeatureSetDetailView(generic.DetailView):
	"""Detail view of a single FeatureSet model"""

	model = FeatureSet

class FeatureSetListView(generic.ListView):
	"""List view of a FeatureSet model"""

	model = FeatureSet
	context_object_name = 'featuresets'

class FeatureInline(InlineFormSet):
	"""Utility-class: Features displayed as a InlineFormset"""

	model = FeatureSet.features.through
	extra = 2

class FeatureSetUpdateView(UpdateWithInlinesView, NamedFormsetsMixin):
	"""Update view of the FeatureSet model"""

	model = FeatureSet
	form_class = FeatureSetForm
	inlines = [FeatureInline,]
	inlines_names = ['features_formset',]

class FeatureSetCreateView(CreateWithInlinesView, NamedFormsetsMixin):
	"""Create view of the FeatureSet model"""

	model = FeatureSet
	form_class = FeatureSetForm
	inlines = [FeatureInline,]
	inlines_names = ['features_formset',]

# Features views

class FeatureDetailView(generic.DetailView):
	"""Detail view of the Feature model"""

	model = Feature

class FeatureListView(generic.ListView):
	"""List view of the Feature model"""

	model = Feature
	context_object_name = 'features'

class FeatureUpdateView(generic.UpdateView):
	"""Update view of the Feature model"""

	model = Feature

class FeatureCreateView(generic.CreateView):
	"""Create view of the Feature model"""

	model = Feature

# Sequence views

class SequenceCreateView(generic.CreateView):
	"""Create view for the Sequence model"""

	model = Sequence
	form_class = SequenceForm

	def form_valid(self, form):
		self.object = form.save(commit=False)
		cproject = get_object_or_404(Project, pk=form.cleaned_data['cp_pk'])
		self.object.project = cproject
		self.object.user = self.request.user
		self.object.save()
		return HttpResponseRedirect(self.object.get_absolute_url())

	def get_initial(self, *args, **kwargs):
		initial = super(SequenceCreateView, self).get_initial(*args, **kwargs)
		initial['cp_pk'] = self.kwargs['cp_pk']
		return initial

class SequenceUpdateView(generic.UpdateView):
	"""Create view for the Sequence model"""

	model = Sequence
	form_class = SequenceForm

	def form_valid(self, form):
		self.object = form.save(commit=False)
		cproject = get_object_or_404(Project, pk=form.cleaned_data['cp_pk'])
		self.object.project = cproject
		self.object.user = self.request.user
		self.object.save()
		return HttpResponseRedirect(self.object.get_absolute_url())

class SequenceDetailView(generic.DetailView):
	"""Create view for the Sequence model"""

	model = Sequence

class SequenceListView(generic.ListView):
	"""Create view for the Sequence model"""

	# TODO:
	# SequenceListView is currently not used (and untested),
	# since raw list of sequences it not used in global scope,
	# e.g. without the project context on the classification project page)

	model = Sequence
	template_name = 'media_classification/sequence_list.html'

# Project views

class ProjectListView(generic.ListView):
	"""List view of the Project model"""

	model = Project
	context_object_name = 'items'
	template_name = 'media_classification/project_list.html'

	def get_queryset(self, *args, **kwargs):
		"""Besides getting the queryset, determines the permissions for request.user.

		:return: a list of tuples, each containing the following: (:class:`.Project`, user_can_view, user_can_edit)
		:rtype: list
		"""

		projects = super(ProjectListView, self).get_queryset(*args, **kwargs)
		user = self.request.user
		items = []
		for p in projects:
			roles = p.determine_roles(user) if user.is_authenticated() else []
			items.append((p, len(roles) > 0, ProjectRole.ROLE_PROJECT_ADMIN in roles))
		return items

class ProjectDetailView(LoginRequiredMixin, ObjectAccessRequiredMixin, generic.DetailView):
	"""Detail view for the Project model"""

	model = Project
        access_func = Project.can_detail

	#@method_decorator(object_access_required(Project, can_detail_project))
	def dispatch(self, *args, **kwargs):
		return super(ProjectDetailView, self).dispatch(*args, **kwargs)

class ProjectRoleInline(InlineFormSet):
	"""Utility-class: ProjectRoles displayed as a InlineFormset"""

	model = ProjectRole
	extra = 2

class CollectionInline(InlineFormSet):
	"""Utility-class: Collections displayed as a InlineFormset"""

	model = ProjectCollection
	extra = 2

class ProjectCreateView(CreateWithInlinesView, NamedFormsetsMixin):
	"""Create view for the Project model"""

	model = Project
	form_class = ProjectForm
	template_name = 'media_classification/project_create.html'
	inlines = [ProjectRoleInline, CollectionInline]
	inlines_names = ['projectrole_formset', 'collection_formset']

	def get_initial(self, *args, **kwargs):
		initial = super(ProjectCreateView, self).get_initial(*args, **kwargs)
		initial['rp_pk'] = self.kwargs['rp_pk']
		#initial['collections'] = self.kwargs['rp_pk']
		return initial

	def forms_valid(self, form, inlines):
		"""Saves the formsets and redirects to Project's detail page."""

		self.object = form.save(commit=False)
		rproject = get_object_or_404(RProject, pk=form.cleaned_data['rp_pk'])
		self.object.research_project=rproject
		self.object.save()
		projectrole_formset = inlines[0]
		projectrole_formset.save()
		return HttpResponseRedirect(self.object.get_absolute_url())

class ProjectUpdateView(UpdateWithInlinesView, NamedFormsetsMixin):
	"""Update view for the Project model"""

	model = Project
	form_class = ProjectForm
	template_name = 'media_classification/project_update.html'
	inlines = [ProjectRoleInline, CollectionInline]
	inlines_names = ['projectrole_formset', 'collection_formset']

	def forms_valid(self, form, inlines):
		"""Saves the formsets and redirects to Project's detail page."""

		self.object = form.save(commit=False)
		self.object.save()
		projectrole_formset, collection_formset = inlines
		projectrole_formset.save()
		# Save collection formset manually as it is defined using the intermediate model
		for pc in collection_formset:
			pc_obj = pc.save(commit=False)
			pc_obj.project_id = self.object.id
			pc_obj.collection_id = pc_obj.collection.id
			pc_obj.save()
		return HttpResponseRedirect(self.object.get_absolute_url())

def project_update(request, pk):
	"""Project update view function.

	.. warning::
		This view is marked for depreciation. It still handles the requests, but is to be replaced
		by its class-based equivalent :class:`.ProjectUpdateView`.
	"""

	project = Project.objects.get(pk=pk)

	form = ProjectForm(instance=project)

	if request.method == "POST":
		form = ProjectForm(request.POST, instance=project)
		collection_formset = ProjectCollectionFormset(request.POST, instance=project)
		projectrole_formset = ProjectRoleFormset(request.POST, instance=project)
		if form.is_valid() and collection_formset.is_valid() and projectrole_formset.is_valid():
			form.save()
			collection_formset.save()
			projectrole_formset.save()

	collection_formset = ProjectCollectionFormset(instance=project)
	projectrole_formset = ProjectRoleFormset(instance=project)

	context = {'project': project,
			'form': form,
			'collection_formset': collection_formset,
			'projectrole_formset': projectrole_formset,}

	return render(request, 'media_classification/project_update.html', context)


# Classify / CS views

def cs_resource_list(request):
	"""Displays the crowd-sourcing enabled resources list."""
	# TODO: This view should be converted to a class-based one

	projects = Project.objects.filter(cs_enabled=True)
	data = []
	for project in projects:
		resources = project.get_all_cs_resources()
		data.append((project, resources))
	context = {'data': data}
	return render(request, 'media_classification/cs_resource_list.html', context)

@login_required
def classify_resource(request, resource_id, project_id):
	"""Prepares the context for the classification table (i.e. feature sets), and renders it on a template."""

	resource = Resource.objects.get(id=resource_id)
	project = Project.objects.get(id=project_id)
	feature_set = project.feature_sets.filter(resource_type=resource.resource_type)[0]
	features = [[feature, FeatureScope.objects.filter(feature=feature.pk)] for feature in feature_set.features.all()]
	context = {'resource': resource, 'project': project, 'features': features}
	return render(request, 'media_classification/classify_resource.html', context)

@login_required
def process_classify(request):
	"""Processes the classification POST request.
	Breaks down the POST kwargs describing the classification table and adds saves the corresponding model instances:

	* :class:`.Classification`
	* :class:`.ClassificationRow`
	* :class:`.FeatureAnswer`
	"""
	project_id = int(request.POST['project_id'])
	resource_id = int(request.POST['resource_id'])

	resource = Resource.objects.get(id=resource_id)
	project = Project.objects.get(id=project_id)
	feature_set = project.feature_sets.filter(resource_type=resource.resource_type)[0]

	answers = list(k.split('__') + [v,] for k,v in dict(request.POST).iteritems() if "__" in k)
	answer_rows = {}
	for n, k, v in answers:
		if n not in answer_rows:
			answer_rows[n] = {}
		answer_rows[n][k] = v
	answer_rows = [ v for k,v in sorted(answer_rows.items(), key=lambda i : i[0])]

	c = Classification(resource=resource, feature_set=feature_set, user=request.user, project=project)
	c.save()

	for answer_row in answer_rows:
		row = ClassificationRow(classification=c)
		row.save()
		for k, v in answer_row.iteritems():
			feature = Feature.objects.get(pk=k)
			afs = FeatureAnswer(value=v[0], feature=feature, classification_row=row)
			afs.save()

	return HttpResponseRedirect(reverse('media_classification:classification_detail',kwargs={'pk':c.pk}))

class ClassificationDetailView(generic.DetailView):
	"""Detail view of the Classification object."""

	model = Classification
	template_name = 'media_classification/classification_detail.html'


class ClassificationListView(generic.ListView):
	"""List view of the Classification object."""

	paginate_by = 10
	model = Classification
	context_object_name = 'classifications'
	template_name = 'media_classification/classification_list.html'
