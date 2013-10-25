from django.db import models
from trapper.apps.storage.models import Resource, ResourceType

class AnimalFeature(models.Model):

	TYPE_STR = 'S'
	TYPE_INT = 'I'
	TYPE_FLT = 'F'
	TYPE_BOL = 'B'

	CHOICES = {
		TYPE_STR: ('String', str),
		TYPE_INT: ('Integer', int),
		TYPE_FLT: ('Float', float),
		TYPE_BOL: ('Boolean', bool),
	}

	name = models.CharField(max_length=255)
	short_name = models.CharField(max_length=255)
	feature_type = models.CharField(max_length=1, choices=tuple((k, v[0]) for k, v  in CHOICES.iteritems()))

	def get_short_name(self):
		return unicode(self.short_name)

	def cast_to_type(self, value):
		return self.CHOICES[self.feature_type][1](value)

	def __unicode__(self):
		scope_str = ", ".join([sc.name for sc in AnimalFeatureScope.objects.filter(feature=self.pk)])
		return unicode("Name: %s | Short: %s | Type: %s | Scope: [%s]" % (self.name, self.short_name, self.get_feature_type_display(), scope_str))

class AnimalFeatureScope(models.Model):
	name = models.CharField(max_length=255)
	feature = models.ForeignKey(AnimalFeature)

	def __unicode__(self):
		return unicode("Feature: %s | Name: %s" % (self.feature.name, self.name))

class ResourceFeatureSet(models.Model):
	name = models.CharField(max_length=255)
	resource_type = models.ForeignKey(ResourceType)
	features = models.ManyToManyField(AnimalFeature)
	
	def __unicode__(self):
		return unicode("Name: %s | Type: %s" %(self.name, self.resource_type.name))

class ResourceClassification(models.Model):
	resource = models.ForeignKey(Resource)
	resource_feature_set = models.ForeignKey(ResourceFeatureSet)
	#user = 

	def __unicode__(self):
		return unicode("Id: %s | FeatureSet: %s | Resource: %s" % (self.id, self.resource_feature_set, self.resource.name))

class ResourceClassificationItem(models.Model):
	resource_classification = models.ForeignKey(ResourceClassification)

	def __unicode__(self):
		return unicode("Row of Classification: %d" % (self.resource_classification.id))

class AnimalFeatureAnswer(models.Model):
	value = models.CharField(max_length=255)
	feature = models.ForeignKey(AnimalFeature)
	resource_classification_item = models.ForeignKey(ResourceClassificationItem)

	def __unicode__(self):
		return "Feature: %s | Value: %s | ClassificationId: %s" % (self.feature.name, self.value, self.resource_classification_item.resource_classification.id);


class ClassificationProject(models.Model):
	name = models.CharField(max_length=255)
	resources = models.ManyToManyField(Resource)
	resource_feature_sets = models.ManyToManyField(ResourceFeatureSet)

	def __unicode__(self):
		return unicode(self.name)

#class ResourceGroup(models.Model):
#	name = models.CharField(max_length=40)
#	project = models.ForeignKey(ClassificationProject)
#	resources = models.ManyToManyField(Resource)
