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

from trapper.apps.research.models import Project, ProjectRole

class ProjectForm(forms.ModelForm):
	"""Project ModelForm for the Update/Create views"""

	class Meta:
		model = Project
		fields = ['name','description',]

	description = forms.CharField(widget=TinyMCE(attrs={'cols':60, 'rows':15}))

ProjectRoleFormset = inlineformset_factory(Project, ProjectRole, extra = 1)
"""Formset for the ProjectRole model"""
