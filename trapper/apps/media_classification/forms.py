from django import forms
from django.forms.models import inlineformset_factory

from trapper.apps.media_classification.models import Project, ProjectCollection, ProjectRole, FeatureSet

class ProjectForm(forms.ModelForm):
	class Meta:
		model = Project
		exclude = ['collections']

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
		exclude = ['features',]

ProjectCollectionFormset = inlineformset_factory(Project, ProjectCollection, extra=0, form=ProjectCollectionForm)
ProjectRoleFormset = inlineformset_factory(Project, ProjectRole, extra = 1)
