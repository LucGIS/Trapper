from django import forms

from trapper.apps.animal_observation.models import ClassificationProject

class ClassificationProjectForm(forms.ModelForm):
	class Meta:
		model = ClassificationProject
