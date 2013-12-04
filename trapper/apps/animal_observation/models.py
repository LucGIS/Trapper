from django.db import models
from trapper.apps.storage.models import Resource, ResourceType, Collection
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

class Feature(models.Model):
	"""
	Model describing given feature of an animal.
	Used for defining given "set" of features we are interested in identifying from given resource.
	"""

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

	def __unicode__(self):
		scope_str = ", ".join(sc.name for sc in self.featurescope_set.all())
		return unicode("Name: %s | Short: %s | Type: %s | Scope: [%s]" % (self.name, self.short_name, self.get_feature_type_display(), scope_str))


class FeatureScope(models.Model):
	"""
	Model describing the scope of given feature.
	Only relevant if the feature type is 'String'.
	"""
	name = models.CharField(max_length=255)
	feature = models.ForeignKey(Feature)

	def __unicode__(self):
		return unicode("Feature: %s | Name: %s" % (self.feature.name, self.name))


class FeatureSet(models.Model):
	"""
	Defined group of features describing given classification table.
	Such set is defined per-resource type, as given classification project.
	"""
	name = models.CharField(max_length=255)
	resource_type = models.ForeignKey(ResourceType)
	features = models.ManyToManyField(Feature)
	
	def __unicode__(self):
		return unicode("Name: %s | Type: %s" %(self.name, self.resource_type.name))

	def get_absolute_url(self):
		return reverse('animal_observation:featureset_detail', kwargs={'pk':self.pk})


class Classification(models.Model):
	"""
	Classification made by the Crowd-sourcing user.
	"""
	resource = models.ForeignKey(Resource)
	feature_set = models.ForeignKey(FeatureSet)
	user = models.ForeignKey(User)

	def __unicode__(self):
		return unicode("Id: %s | FeatureSet: %s | Resource: %s" % (self.id, self.feature_set, self.resource.name))


class ClassificationRow(models.Model):
	classification = models.ForeignKey(Classification)

	def __unicode__(self):
		return unicode("Row of Classification: %d" % (self.classification.id))


class FeatureAnswer(models.Model):
	value = models.CharField(max_length=255)
	feature = models.ForeignKey(Feature)
	classification_row = models.ForeignKey(ClassificationRow)

	def __unicode__(self):
		return "Feature: %s | Value: %s | ClassificationId: %s" % (self.feature.name, self.value, self.classification_row.classification.id);


class Project(models.Model):
	name = models.CharField(max_length=255)
	collections = models.ManyToManyField(Collection, through='ProjectCollection', blank=True, null=True)
	feature_sets = models.ManyToManyField(FeatureSet, blank=True, null=True)
	date_created = models.DateTimeField(auto_now_add=True)
	cs_enabled = models.BooleanField(default=True)

	def __unicode__(self):
		return unicode(self.name)

	def get_all_cs_resources(self):
		"""
		A list of crowd-sourcing enabled resources.
		"""

		resources = []
		#for c in self.collections.filter(projectcollection__active=True):
		#	print c.name
		#	new = [r.resource for r in ResourceExtra.objects.filter(cs_enabled=True, resource__in=c.resources.all())]
		#	resources.extend(new)
		return list(set(resources))

	def determine_roles(self, user):
		"""
		Returns a tuple of project roles for given user.
		"""
		return [r.name for r in self.projectrole_set.filter(user=user)]

	def get_absolute_url(self):
		return reverse('animal_observation:project_detail', kwargs={'pk':self.pk})


class Sequence(models.Model):
	"""
	Sequence of resources identified by an expert.
	"""

	name = models.CharField(max_length=255, null=True, blank=True)
	description = models.TextField(max_length=1000, null=True, blank=True)
	resources = models.ManyToManyField(Resource)
	project = models.ForeignKey(Project)
	date_created = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(User)

	def __unicode__(self):
		return unicode("Sequence from {date} defined by {user}".format(
			date=self.date_created, user=self.user))


class ProjectCollection(models.Model):
	"""
	ManyToMany model for Project-Collection relationship.

	* active - states whether given collection is "enabled" for the project.
	* cs_enabled - when True, given collection will take part in the crowd-sourcing classification
	"""

	project = models.ForeignKey(Project)
	collection = models.ForeignKey(Collection)
	active = models.BooleanField("Active", default=True)
	cs_enabled = models.BooleanField("Crowd-Sourcing", default=True)

	def __unicode__(self):
		return unicode("%s <-> %s (Active: %s, CS: %s)" % (self.project.name, self.collection.name, self.active, self.cs_enabled))


class ProjectRole(models.Model):
	ROLE_PROJECT_ADMIN = "A"
	ROLE_EXPERT = "E"
	ROLE_COLLABORATOR = "C"

	ROLE_ANY = (ROLE_PROJECT_ADMIN, ROLE_EXPERT, ROLE_COLLABORATOR, )

	ROLE_CHOICES = (
		(ROLE_PROJECT_ADMIN, "Admin"),
		(ROLE_EXPERT, "Expert"),
		(ROLE_COLLABORATOR, "Collaborator"),
	)
	user = models.ForeignKey(User)
	name = models.CharField(max_length=1, choices=ROLE_CHOICES)
	project = models.ForeignKey(Project)

	def __unicode__(self):
		return unicode("%s | Project: %s | Role: %s " % (self.user.username, self.project.name, self.get_name_display()))
