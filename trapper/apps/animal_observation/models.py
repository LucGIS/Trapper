from django.db import models
from trapper.apps.storage.models import Resource, ResourceType, Collection
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

class Feature(models.Model):

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
		scope_str = ", ".join([sc.name for sc in FeatureScope.objects.filter(feature=self.pk)])
		return unicode("Name: %s | Short: %s | Type: %s | Scope: [%s]" % (self.name, self.short_name, self.get_feature_type_display(), scope_str))

class FeatureScope(models.Model):
	name = models.CharField(max_length=255)
	feature = models.ForeignKey(Feature)

	def __unicode__(self):
		return unicode("Feature: %s | Name: %s" % (self.feature.name, self.name))

class FeatureSet(models.Model):
	name = models.CharField(max_length=255)
	resource_type = models.ForeignKey(ResourceType)
	features = models.ManyToManyField(Feature)
	
	def __unicode__(self):
		return unicode("Name: %s | Type: %s" %(self.name, self.resource_type.name))

	def get_absolute_url(self):
		return reverse('animal_observation:featureset_detail', kwargs={'pk':self.pk})

class ResourceExtra(models.Model):
	"""
	Extends the default storage.models.Resource model with the information relevant to the animal_observation app.
	"""
	resource = models.OneToOneField(Resource)
	public = models.BooleanField()
	cs_enabled = models.BooleanField()

	def __unicode__(self):
		return unicode("%s | public: %s | cs_enabled: %s" % (self.resource.name, self.public, self.cs_enabled))

class Classification(models.Model):
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
		for c in self.collections.filter(projectcollection__active=True):
			print c.name
			new = [r.resource for r in ResourceExtra.objects.filter(cs_enabled=True, resource__in=c.resources.all())]
			resources.extend(new)
		return list(set(resources))

	def determine_roles(self, user):
		"""
		Returns a tuple of project roles for given user.
		"""
		return [r.name for r in self.projectrole_set.filter(user=user)]

	def get_absolute_url(self):
		return reverse('animal_observation:project_detail', kwargs={'pk':self.pk})

class ProjectCollection(models.Model):
	"""
	ManyToMany model for Project-Collection relationship.

	* active - states whether given resource is "enabled" for the project. In that case it will be 
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

def create_resource_extra(sender, instance, created, **kwargs):
	if created:
		resource_extra, created = ResourceExtra.objects.get_or_create(resource=instance, public=False, cs_enabled=False)

models.signals.post_save.connect(create_resource_extra, sender=Resource)
