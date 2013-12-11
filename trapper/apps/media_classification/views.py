from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.forms.models import inlineformset_factory
from django.views import generic
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator

from braces.views import LoginRequiredMixin
from extra_views import InlineFormSet, CreateWithInlinesView, UpdateWithInlinesView, NamedFormsetsMixin

from trapper.apps.media_classification.models import Feature, FeatureAnswer, FeatureScope, Project, Classification, ClassificationRow, ProjectRole, ProjectCollection, FeatureSet
from trapper.apps.storage.models import Resource
from trapper.apps.media_classification.forms import ProjectForm, ProjectCollectionFormset, ProjectRoleFormset, FeatureSetForm
from trapper.apps.common.decorators import object_access_required



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

def can_detail_project(user, project):
	return ProjectRole.objects.filter(user=user, project=project).count() > 0


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
	"""Detail view for the Project model"""

	model = Project

	@method_decorator(object_access_required(Project, can_detail_project))
	def dispatch(self, *args, **kwargs):
		return super(ProjectDetailView, self).dispatch(*args, **kwargs)


def can_update_project(user, project):
	return ProjectRole.objects.filter(user=user, project=project, name=ProjectRole.ROLE_PROJECT_ADMIN).count() > 0

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

	def forms_valid(self, form, inlines):
		"""Saves the formsets and redirects to Project's detail page."""

		self.object = form.save(commit=False)
		self.object.save()
		projectrole_formset, collection_formset = inlines
		projectrole_formset.save()
		# Save collection formset manually as it is defined using intermediate model
		for pc in collection_formset:
			pc_obj = pc.save(commit=False)
			pc_obj.project_id = self.object.id
			pc_obj.save()
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
	resource_feature_set = project.resource_feature_sets.filter(resource_type=resource.resource_type)[0]

	answers = list(k.split('__') + [v,] for k,v in dict(request.POST).iteritems() if "__" in k)
	answer_rows = {}
	for n, k, v in answers:
		if n not in answer_rows:
			answer_rows[n] = {}
		answer_rows[n][k] = v
	answer_rows = [ v for k,v in sorted(answer_rows.items(), key=lambda i : i[0])]

	r = Classification(resource=resource, resource_feature_set=resource_feature_set, user=request.user)
	r.save()

	for answer_row in answer_rows:
		rci = ClassificationRow(resource_classification=r)
		rci.save()
		for k, v in answer_row.iteritems():
			feature = Feature.objects.get(pk=k)
			afs = FeatureAnswer(value=v[0], feature=feature, resource_classification_item=rci)
			afs.save()

	return redirect('trapper.apps.media_classification.classification_details', pk=r.pk)

def classification_details(request, pk):
	c = Classification.objects.get(pk=pk)

	context = {
		'c': c,
	}

	return render(request, 'media_classification/classification_details.html', context)
