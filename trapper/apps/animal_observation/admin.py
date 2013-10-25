from django.contrib import admin
from trapper.apps.animal_observation.models import AnimalFeatureScope, AnimalFeature, ResourceFeatureSet, ResourceClassification, ResourceClassificationItem, ClassificationProject, AnimalFeatureAnswer

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

admin.site.register(AnimalFeature, AnimalFeatureAdmin)
admin.site.register(AnimalFeatureAnswer)
admin.site.register(AnimalFeatureScope)
admin.site.register(ResourceFeatureSet)
admin.site.register(ResourceClassification, ResourceClassificationAdmin)
admin.site.register(ResourceClassificationItem, ResourceClassificationItemAdmin)
admin.site.register(ClassificationProject)
