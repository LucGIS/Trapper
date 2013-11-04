from django.shortcuts import render, redirect
from django.views import generic

from trapper.apps.storage.models import Resource 


def index(request):
	resources = Resource.objects.all()
	context = {'resources': resources}
	return render(request, 'storage/index.html', context)

def resource_list(request):
	resources = Resource.objects.all()
	context = {'resources': resources}
	return render(request, 'storage/resource_list.html', context)

class ResourceDetails(generic.DetailView):
	model = Resource
	template_name = 'storage/resource_details.html'

class ResourceUpdate(generic.UpdateView):
	model = Resource
	template_name = 'storage/resource_details.html'
