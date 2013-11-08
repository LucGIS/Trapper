from django import forms

from trapper.apps.animal_observation.models import ClassificationProject, ClassificationProjectResourceCollection

class ClassificationProjectForm(forms.ModelForm):
	class Meta:
		model = ClassificationProject
	
class ClassificationProjectResourceCollectionForm(forms.ModelForm):
	class Meta:
		model = ClassificationProjectResourceCollection
