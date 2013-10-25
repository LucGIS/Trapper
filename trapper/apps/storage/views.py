from django.shortcuts import render, redirect
from django.views import generic

from trapper.apps.storage.models import Resource 


def index(request):
	resources = Resource.objects.all()
	context = {'resources': resources}
	return render(request, 'storage_index.html', context)

class ResourceView(generic.DetailView):
	model = Resource
	template_name = 'resource_view.html'

class ResourceUpdate(generic.UpdateView):
	model = Resource
	template_name = 'resource_view.html'
