from django.contrib import admin
from trapper.apps.animal_observation.models import AnimalFeatureScope, AnimalFeature, ResourceFeatureSet, ResourceClassification, ResourceClassificationItem, ClassificationProject, AnimalFeatureAnswer, ResourceExtra, ClassificationProjectRole, ClassificationProjectResourceCollection, ClassificationProjectResourceCollection

class AnimalFeatureScopeInline(admin.StackedInline):
	model = AnimalFeatureScope

class AnimalFeatureAdmin(admin.ModelAdmin):
	inlines = [AnimalFeatureScopeInline,]


class AnimalFeatureAnswerInline(admin.StackedInline):
	model = AnimalFeatureAnswer
	extra = 0

class ResourceClassificationItemAdmin(admin.ModelAdmin):
	inlines = [AnimalFeatureAnswerInline,]
	
class ResourceClassificationItemInline(admin.StackedInline):
	model = ResourceClassificationItem
	extra = 0

class ResourceClassificationAdmin(admin.ModelAdmin):
	inlines = [ResourceClassificationItemInline,]

class ClassificationProjectRoleInline(admin.StackedInline):
	model = ClassificationProjectRole
	extra = 0

class ClassificationProjectResourceCollectionInline(admin.StackedInline):
	model = ClassificationProjectResourceCollection
	extra = 0

class ClassificationProjectAdmin(admin.ModelAdmin):
	inlines = [ClassificationProjectRoleInline, ClassificationProjectResourceCollectionInline]
	filter_horizontal = ('resource_collections','resource_feature_sets',)

	def get_form(self, request, obj=None, **kwargs):
		form = super(ClassificationProjectAdmin, self).get_form(request, obj, **kwargs)
		# TODO: filter the resources by project availability
		#form.base_fields['resources'].queryset = form.base_fields['resources'].queryset.filter(name=u'VIDEO001.mp4')
		return form

admin.site.register(AnimalFeature, AnimalFeatureAdmin)
admin.site.register(AnimalFeatureAnswer)
admin.site.register(AnimalFeatureScope)
admin.site.register(ResourceFeatureSet)
admin.site.register(ResourceExtra)
admin.site.register(ClassificationProjectResourceCollection)
admin.site.register(ResourceClassification, ResourceClassificationAdmin)
admin.site.register(ResourceClassificationItem, ResourceClassificationItemAdmin)
admin.site.register(ClassificationProjectRole)
admin.site.register(ClassificationProject, ClassificationProjectAdmin)
