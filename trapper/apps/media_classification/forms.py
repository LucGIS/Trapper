############################################################################
#   Copyright (c) 2013  Trapper development team                           #
#                                                                          #
#   This file is a part of Trapper.                                        #
#                                                                          #
#   This program is free software; you can redistribute it and/or modify   #
#   it under the terms of the GNU General Public License as published by   #
#   the Free Software Foundation; either version 2 of the License, or      #
#   (at your option) any later version.                                    #
#                                                                          #
#   This program is distributed in the hope that it will be useful,        #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#   GNU General Public License for more details.                           #
#                                                                          #
#   You should have received a copy of the GNU General Public License      #
#   along with this program; if not, write to the                          #
#   Free Software Foundation, Inc.,                                        #
#   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.              #
############################################################################

from django import forms
from django.forms.models import inlineformset_factory

from trapper.apps.media_classification.models import Project, ProjectCollection, ProjectRole, FeatureSet

class ProjectForm(forms.ModelForm):
	"""Project ModelForm for the Update/Create views"""

	class Meta:
		model = Project
		exclude = ['collections']

class ProjectCollectionForm(forms.ModelForm):
	"""ProjectCollection ModelForm for the Update/Create views"""

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
"""Formset for the ProjectCollection model"""

ProjectRoleFormset = inlineformset_factory(Project, ProjectRole, extra = 1)
"""Formset for the ProjectRole model"""
