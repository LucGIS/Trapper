from django import forms

from trapper.apps.animal_observation.models import ClassificationProject

class ResourceCollectionRequestForm(forms.Form):
	text = forms.CharField(widget=forms.Textarea)
	project = forms.ModelChoiceField(queryset=ClassificationProject.objects.none())
	collection_pk = forms.IntegerField(widget=forms.HiddenInput())
