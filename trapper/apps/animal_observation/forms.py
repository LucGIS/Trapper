from django import forms

from trapper.apps.animal_observation.models import ClassificationProject, ClassificationProjectResourceCollection, ResourceFeatureSet

class ClassificationProjectForm(forms.ModelForm):
	class Meta:
		model = ClassificationProject
		exclude = ['resource_collections']

	def __init__(self, *args, **kwargs):
		super(ClassificationProjectForm, self).__init__(*args,**kwargs)
		self.fields['cs_enabled'].label='Enabled for Crowd-Sourcing ?'
	
class ClassificationProjectResourceCollectionForm(forms.ModelForm):
	class Meta:
		model = ClassificationProjectResourceCollection
		#hidden = ['collection']

	def __init__(self, *args, **kwargs):
		super(ClassificationProjectResourceCollectionForm, self).__init__(*args,**kwargs)
		if self.instance.id:
			self.col_name = self.instance.collection.name
			del self.fields['collection']

class ResourceFeatureSetForm(forms.ModelForm):
	class Meta:
		model = ResourceFeatureSet
