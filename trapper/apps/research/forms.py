############################################################################
#   Copyright (c) 2013  IBS PAN Bialowieza                                 #
#   Copyright (c) 2013  Bialystok University of Technology                 #
#                                                                          #
#   This file is a part of Trapper.                                        #
#                                                                          #
#   Trapper is free software; you can redistribute it and/or modify        #
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

from tinymce.widgets import TinyMCE
from djangular.forms import NgModelFormMixin
from crispy_forms.helper import FormHelper

from trapper.apps.research.models import Project, ProjectRole, ProjectCollection


class ProjectForm(forms.ModelForm):
    """Project ModelForm for the Update/Create views"""

    class Meta:
        model = Project
        fields = ['name','description',]

    description = forms.CharField(widget=TinyMCE(attrs={'cols':60, 'rows':15}))

ProjectRoleFormset = inlineformset_factory(Project, ProjectRole, extra = 1)
"""Formset for the ProjectRole model"""


class ProjectCollectionForm(NgModelFormMixin, forms.ModelForm):

    REQUIRED_PROJECT_ROLES = [ProjectRole.ROLE_PROJECT_ADMIN, ProjectRole.ROLE_EXPERT]

    class Meta:
        model = ProjectCollection

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.error_text_inline = True
        self.helper.form_show_errors = True
        self.helper.help_text_inline = False
        super(ProjectCollectionForm, self).__init__(*args, **kwargs)
        self.fields['collection'].widget = forms.HiddenInput()
        if user:
            project_pks = set(role.project.pk for role in user.research_roles.filter(name__in = self.REQUIRED_PROJECT_ROLES))
            projects = Project.objects.filter(pk__in=project_pks)
            self.fields['project'].queryset = projects

    def clean(self):
        project = self.cleaned_data.get("project")
        collection = self.cleaned_data.get("collection")
        if ProjectCollection.objects.filter(project=project, collection=collection):
            raise forms.ValidationError("Project Collection already exists.")
        return self.cleaned_data
