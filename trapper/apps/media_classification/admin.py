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

from django.contrib import admin
from trapper.apps.media_classification.models import FeatureScope, Feature, FeatureSet, Classification, ClassificationRow, Project, FeatureAnswer, ProjectRole, ProjectCollection, Sequence


class FeatureScopeInline(admin.StackedInline):
	model = FeatureScope

class FeatureAdmin(admin.ModelAdmin):
	inlines = [FeatureScopeInline,]

class FeatureAnswerInline(admin.StackedInline):
	model = FeatureAnswer
	extra = 0

class ClassificationRowAdmin(admin.ModelAdmin):
	inlines = [FeatureAnswerInline,]
	
class ClassificationRowInline(admin.StackedInline):
	model = ClassificationRow
	extra = 0

class ClassificationAdmin(admin.ModelAdmin):
	inlines = [ClassificationRowInline,]

class ProjectRoleInline(admin.TabularInline):
	model = ProjectRole
	extra = 0

class ProjectCollectionInline(admin.TabularInline):
	model = ProjectCollection
	extra = 0

class ProjectAdmin(admin.ModelAdmin):
	inlines = [ProjectRoleInline, ProjectCollectionInline]
	filter_horizontal = ('collections','feature_sets',)

	def get_form(self, request, obj=None, **kwargs):
		form = super(ProjectAdmin, self).get_form(request, obj, **kwargs)
		return form

admin.site.register(Feature, FeatureAdmin)
admin.site.register(FeatureAnswer)
admin.site.register(FeatureScope)
admin.site.register(FeatureSet)
admin.site.register(ProjectCollection)
admin.site.register(Classification, ClassificationAdmin)
admin.site.register(ClassificationRow, ClassificationRowAdmin)
admin.site.register(ProjectRole)
admin.site.register(Sequence)
admin.site.register(Project, ProjectAdmin)
