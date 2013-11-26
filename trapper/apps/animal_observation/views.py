from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.forms.models import inlineformset_factory
from django.views import generic
from django.utils.decorators import method_decorator

from trapper.apps.animal_observation.models import Feature, FeatureAnswer, FeatureScope, Project, Classification, ClassificationRow, ProjectRole, ProjectCollection
from trapper.apps.storage.models import Resource
from trapper.apps.animal_observation.decorators import project_role_required
from trapper.apps.animal_observation.forms import ProjectForm, ProjectCollectionForm
from trapper.commons.decorators import object_access_required


class ProjectListView(generic.ListView):
	model = Project
	context_object_name = 'items'
	template_name = 'animal_observation/project_list.html'

	def get_queryset(self, *args, **kwargs):
		projects = super(ProjectListView, self).get_queryset(*args, **kwargs)
		user = self.request.user
		items = []
		for p in projects:
			roles = p.determine_roles(user) if user.is_authenticated() else []
			items.append((p, len(roles) > 0, ProjectRole.ROLE_PROJECT_ADMIN in roles))
		return items

def can_detail_project(user, project):
	return ProjectRole.objects.filter(user=user, project=project).count() > 0

class ProjectDetailView(generic.DetailView):
	model = Project

	@method_decorator(login_required)
	@method_decorator(object_access_required(Project, can_detail_project))
	def dispatch(self, *args, **kwargs):
		return super(ProjectDetailView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context = super(ProjectDetailView, self).get_context_data(*args, **kwargs)
		context['roles'] = ProjectRole.objects.filter(project=self.get_object())
		return context


def can_update_project(user, project):
	return ProjectRole.objects.filter(user=user, project=project, name=ProjectRole.ROLE_PROJECT_ADMIN).count() > 0

class ProjectUpdateView(generic.UpdateView):
	model = Project
	context_object_name = 'project'
	template_name = 'animal_observation/project_update.html'

	@method_decorator(login_required)
	@method_decorator(object_access_required(Project, can_update_project))
	def dispatch(self, *args, **kwargs):
		return super(ProjectUpdateView, self).dispatch(*args, **kwargs)


@project_role_required([ProjectRole.ROLE_PROJECT_ADMIN,], access_denied_page='/message/1/')
def project_update(request, project_id):
	project = Project.objects.get(id=project_id)

	form = ProjectForm(instance=project)
	CPRCFormset = inlineformset_factory(Project, ProjectCollection, extra=0, form=ProjectCollectionForm)
	CPCPRFormset = inlineformset_factory(Project, ProjectRole, extra=1)

	if request.method == "POST":
		form = ProjectForm(request.POST, instance=project)
		resources_formset = CPRCFormset(request.POST, instance=project)
		roles_formset = CPCPRFormset(request.POST, instance=project)
		if form.is_valid() and resources_formset.is_valid() and roles_formset.is_valid():
			form.save()
			resources_formset.save()
			roles_formset.save()

	resources_formset = CPRCFormset(instance=project)
	roles_formset = CPCPRFormset(instance=project)

	context = {'project': project,
			'form': form,
			'resources_formset': resources_formset,
			'roles_formset': roles_formset,
			}

	return render(request, 'animal_observation/project_update.html', context)

def cs_resource_list(request):
	projects = Project.objects.filter(cs_enabled=True)
	data = []
	for project in projects:
		resources = project.get_all_cs_resources()
		data.append((project, resources))
	context = {'data': data}
	return render(request, 'animal_observation/cs_resource_list.html', context)

@login_required
def classify_resource(request, resource_id, project_id):
	resource = Resource.objects.get(id=resource_id)
	project = Project.objects.get(id=project_id)
	feature_set = project.feature_sets.filter(resource_type=resource.resource_type)[0]
	features = [[feature, FeatureScope.objects.filter(feature=feature.pk)] for feature in feature_set.features.all()]
	context = {'resource': resource, 'project': project, 'features': features}
	return render(request, 'animal_observation/classify_resource.html', context)

@login_required
def process_classify(request):
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

	return redirect('trapper.apps.animal_observation.classification_details', pk=r.pk)

def classification_details(request, pk):
	c = Classification.objects.get(pk=pk)

	context = {
		'c': c,
	}

	return render(request, 'animal_observation/classification_details.html', context)
