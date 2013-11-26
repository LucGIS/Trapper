from django import forms

from trapper.apps.animal_observation.models import Project, ProjectCollection, FeatureSet

class ProjectForm(forms.ModelForm):
	class Meta:
		model = Project
		exclude = ['resource_collections']

	def __init__(self, *args, **kwargs):
		super(ProjectForm, self).__init__(*args,**kwargs)
		self.fields['cs_enabled'].label='Enabled for Crowd-Sourcing ?'
	
class ProjectCollectionForm(forms.ModelForm):
	class Meta:
		model = ProjectCollection

	def __init__(self, *args, **kwargs):
		super(ProjectCollectionForm, self).__init__(*args,**kwargs)
		if self.instance.id:
			# Adds collection as a simple label, so the user can't alter it.
			self.col_name = self.instance.collection.name
			del self.fields['collection']

class FeatureSetForm(forms.ModelForm):
	class Meta:
		model = FeatureSet
