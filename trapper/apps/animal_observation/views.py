from django.shortcuts import render, redirect
from django.views import generic

from trapper.apps.animal_observation.models import ClassificationProject, AnimalFeatureScope, ResourceClassification, AnimalFeature, ResourceClassificationItem, AnimalFeatureAnswer
from trapper.apps.storage.models import Resource


def index(request):
	projects = ClassificationProject.objects.all()
	context = {'projects': projects}
	return render(request, 'index.html', context)

def project_home(request, project_id):
	project = ClassificationProject.objects.get(id=project_id)
	context = {'project': project}
	return render(request, 'project_home.html', context)

def resource_details(request, resource_id):
	resource = Resource.objects.get(id=resource_id)
	context = {'resource': resource}
	return render(request, 'resource_view.html', context)

def classify_resource(request, resource_id, project_id):
	resource = Resource.objects.get(id=resource_id)
	project = ClassificationProject.objects.get(id=project_id)
	resource_feature_set = project.resource_feature_sets.filter(resource_type=resource.resource_type)[0]
	features = [[feature, AnimalFeatureScope.objects.filter(feature=feature.pk)] for feature in resource_feature_set.features.all()]
	context = {'resource': resource, 'project': project, 'features': features}
	return render(request, 'classify_resource.html', context)

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

	r = ResourceClassification(resource=resource, resource_feature_set=resource_feature_set)
	r.save()

	for answer_row in answer_rows:
		rci = ResourceClassificationItem(resource_classification=r)
		rci.save()
		for k, v in answer_row.iteritems():
			feature = AnimalFeature.objects.get(pk=k)
			afs = AnimalFeatureAnswer(value=v[0], feature=feature, resource_classification_item=rci)
			afs.save()

	return redirect('classification_view', pk=r.pk)

def classification_view(request, pk):

	c = ResourceClassification.objects.get(pk=pk)

	context = {
		'c': c,
	}

	return render(request, 'classification_view.html', context)
