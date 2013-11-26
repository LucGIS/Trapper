from django import forms
from ajax_select import make_ajax_field

from trapper.apps.animal_observation.models import Project
from trapper.apps.storage.models import Resource, Collection

class CollectionRequestForm(forms.Form):
	text = forms.CharField(widget=forms.Textarea)
	project = forms.ModelChoiceField(queryset=Project.objects.none())
	collection_pk = forms.IntegerField(widget=forms.HiddenInput())

class CollectionForm(forms.ModelForm):
	class Meta:
		model = Collection
	
	owner = make_ajax_field(Collection, 'owner', 'user', help_text=None, plugin_options={'autoFocus':True,})
	resources = make_ajax_field(Collection, 'resources', 'resource', help_text=None, show_help_text=False, plugin_options={'autoFocus':True,})
	managers = make_ajax_field(Collection, 'managers', 'user', help_text=None, show_help_text=False, plugin_options={'autoFocus':True,})

class ResourceForm(forms.ModelForm):
	class Meta:
		model = Resource
		# exclude the 'uploader' field as it is always the request.user
		exclude=['uploader',]
	
	owner = make_ajax_field(Collection, 'owner', 'user', help_text=None, plugin_options={'autoFocus':True,})
