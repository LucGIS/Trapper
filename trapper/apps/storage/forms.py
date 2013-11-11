from django import forms

from trapper.apps.animal_observation.models import ClassificationProject

class ResourceCollectionRequestForm(forms.Form):
	text = forms.CharField(widget=forms.Textarea)
	projects = forms.ModelChoiceField(queryset=ClassificationProject.objects.none())
