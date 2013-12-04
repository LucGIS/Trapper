from django.contrib import admin
from trapper.apps.animal_observation.models import FeatureScope, Feature, FeatureSet, Classification, ClassificationRow, Project, FeatureAnswer, ProjectRole, ProjectCollection


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
admin.site.register(Project, ProjectAdmin)
