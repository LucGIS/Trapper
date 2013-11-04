from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from trapper.apps.animal_observation.models import AnimalFeature, AnimalFeatureAnswer, AnimalFeatureScope, ClassificationProject, ResourceClassification, ResourceClassificationItem, ResourceExtra, ClassificationProjectRole
from trapper.apps.storage.models import Resource
from trapper.apps.animal_observation.decorators import project_role_required


def index(request):
	projects = ClassificationProject.objects.all()
	context = {'projects': projects}
	return render(request, 'animal_observation/index.html', context)

@project_role_required([ClassificationProjectRole.ROLE_PROJECT_ADMIN,], redirect_page='trapper.apps.animal_observation.index')
def project_details(request, project_id):
	project = ClassificationProject.objects.get(id=project_id)
	role = None
	if request.user:
		role = ClassificationProjectRole.objects.filter(user=request.user, project=project)
		if role:
			role = role[0]
	context = {'project': project, 'role': role}
	return render(request, 'animal_observation/project_details.html', context)

def cs_resource_list(request):
	projects = ClassificationProject.objects.filter(cs_enabled=True)
	data = []
	for project in projects:
		resources = project.get_all_cs_resources()
		data.append((project, resources))
	context = {'data': data}
	return render(request, 'animal_observation/cs_resource_list.html', context)

@login_required
def classify_resource(request, resource_id, project_id):
	resource = Resource.objects.get(id=resource_id)
	project = ClassificationProject.objects.get(id=project_id)
	resource_feature_set = project.resource_feature_sets.filter(resource_type=resource.resource_type)[0]
	features = [[feature, AnimalFeatureScope.objects.filter(feature=feature.pk)] for feature in resource_feature_set.features.all()]
	context = {'resource': resource, 'project': project, 'features': features}
	return render(request, 'animal_observation/classify_resource.html', context)

@login_required
def process_classify(request):
	project_id = int(request.POST['project_id'])
	resource_id = int(request.POST['resource_id'])

	resource = Resource.objects.get(id=resource_id)
	project = ClassificationProject.objects.get(id=project_id)
	resource_feature_set = project.resource_feature_sets.filter(resource_type=resource.resource_type)[0]
	features = [[feature, AnimalFeatureScope.objects.filter(feature=feature.pk)] for feature in resource_feature_set.features.all()]

	answers = list(k.split('__') + [v,] for k,v in dict(request.POST).iteritems() if "__" in k)
	answer_rows = {}
	for n, k, v in answers:
		if n not in answer_rows:
			answer_rows[n] = {}
		answer_rows[n][k] = v
	answer_rows = [ v for k,v in sorted(answer_rows.items(), key=lambda i : i[0])]

	r = ResourceClassification(resource=resource, resource_feature_set=resource_feature_set, user=request.user)
	r.save()

	for answer_row in answer_rows:
		rci = ResourceClassificationItem(resource_classification=r)
		rci.save()
		for k, v in answer_row.iteritems():
			feature = AnimalFeature.objects.get(pk=k)
			afs = AnimalFeatureAnswer(value=v[0], feature=feature, resource_classification_item=rci)
			afs.save()

	return redirect('trapper.apps.animal_observation.classification_details', pk=r.pk)

def classification_details(request, pk):
	c = ResourceClassification.objects.get(pk=pk)

	context = {
		'c': c,
	}

	return render(request, 'animal_observation/classification_details.html', context)
