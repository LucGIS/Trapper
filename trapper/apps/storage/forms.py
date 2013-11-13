from django import forms
from django.contrib.auth.models import User
from ajax_select.fields import AutoCompleteSelectField
from ajax_select import make_ajax_field

from trapper.apps.animal_observation.models import ClassificationProject
from trapper.apps.storage.models import Resource, ResourceCollection

class ResourceCollectionRequestForm(forms.Form):
	text = forms.CharField(widget=forms.Textarea)
	project = forms.ModelChoiceField(queryset=ClassificationProject.objects.none())
	collection_pk = forms.IntegerField(widget=forms.HiddenInput())

class ResourceCollectionForm(forms.ModelForm):
	class Meta:
		model = ResourceCollection
	
	owner = make_ajax_field(ResourceCollection, 'owner', 'user', help_text=None, plugin_options={'autoFocus':True,})
	resources = make_ajax_field(ResourceCollection, 'resources', 'resource', help_text=None, show_help_text=False, plugin_options={'autoFocus':True,})
	managers = make_ajax_field(ResourceCollection, 'managers', 'user', help_text=None, show_help_text=False, plugin_options={'autoFocus':True,})

class ResourceForm(forms.ModelForm):
	class Meta:
		model = Resource
		# exclude the 'uploader' field as it is always the request.user
		exclude=['uploader',]
	
	owner = make_ajax_field(ResourceCollection, 'owner', 'user', help_text=None, plugin_options={'autoFocus':True,})
