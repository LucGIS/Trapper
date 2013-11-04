from django.db import models
from trapper.apps.storage.models import Resource, ResourceType, ResourceCollection
from django.contrib.auth.models import User

class AnimalFeature(models.Model):

	TYPE_STR = 'S'
	TYPE_INT = 'I'
	TYPE_FLT = 'F'
	TYPE_BOL = 'B'

	TYPE_CHOICES = {
		(TYPE_STR, 'String'),
		(TYPE_INT, 'Integer'),
		(TYPE_FLT, 'Float'),
		(TYPE_BOL, 'Boolean'),
	}

	name = models.CharField(max_length=255)
	short_name = models.CharField(max_length=255)
	feature_type = models.CharField(max_length=1, choices=TYPE_CHOICES)

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

class ResourceExtra(models.Model):
	"""
	Extends the default storage.models.Resource model with the information relevant to the animal_observation app.
	"""
	resource = models.OneToOneField(Resource)
	public = models.BooleanField()
	cs_enabled = models.BooleanField()

	def __unicode__(self):
		return unicode("%s | public: %s | cs_enabled: %s" % (self.resource.name, self.public, self.cs_enabled))

class ResourceClassification(models.Model):
	resource = models.ForeignKey(Resource)
	resource_feature_set = models.ForeignKey(ResourceFeatureSet)
	user = models.ForeignKey(User)

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
	resources = models.ManyToManyField(Resource, blank=True, null=True)
	collections = models.ManyToManyField(ResourceCollection, blank=True, null=True)
	resource_feature_sets = models.ManyToManyField(ResourceFeatureSet, blank=True, null=True)
	users = models.ManyToManyField(User)
	date_created = models.DateTimeField(auto_now_add=True)
	cs_enabled = models.BooleanField(default=True)

	def __unicode__(self):
		return unicode(self.name)

	def get_all_cs_resources(self):
		"""
		A list of crowd-sourcing enabled resources.
		"""
		resources = [r.resource for r in ResourceExtra.objects.filter(cs_enabled=True, pk__in=self.resources.all())]
		for c in self.collections.all():
			new = [r.resource for r in ResourceExtra.objects.filter(cs_enabled=True, resource__in=c.resources.all())]
			resources.extend(new)
		return list(set(resources))

class ClassificationProjectRole(models.Model):
	ROLE_PROJECT_ADMIN = "A"
	ROLE_EXPERT = "E"
	ROLE_COLLABORATOR = "C"
	ROLE_CHOICES = (
		(ROLE_PROJECT_ADMIN, "Admin"),
		(ROLE_EXPERT, "Expert"),
		(ROLE_COLLABORATOR, "Collaborator"),
	)
	name = models.CharField(max_length=1, choices=ROLE_CHOICES)
	user = models.ForeignKey(User)
	project = models.ForeignKey(ClassificationProject)

	def __unicode__(self):
		return unicode("%s | Project: %s | Role: %s " % (self.user.username, self.project.name, self.get_name_display()))
