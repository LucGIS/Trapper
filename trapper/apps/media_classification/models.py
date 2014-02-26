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

from django.db import models
from trapper.apps.storage.models import Resource
from trapper.apps.research.models import Project as RProject, ProjectCollection as RProjectCollection
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

class Feature(models.Model):
    """Model describing given feature of an animal.
    Used for defining given "set" of features we are interested in identifying from given resource.

    .. note::
        Feature can be of given type, which at the moment can be either:ode

        * String (enum)
        * Integer
        * Float
        * Boolean
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
    """Long name of feature"""

    short_name = models.CharField(max_length=255)
    """Short name of feature displayed on a form"""

    feature_type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    """Type of the feature"""

    def get_short_name(self):
        """Get short name of the feature.
        It is used for displaying a shorter name in the form.
        """

        return unicode(self.short_name)

    def __unicode__(self):
        scope_str = ", ".join(sc.name for sc in self.featurescope_set.all())
        return unicode("Name: %s | Short: %s | Type: %s | Scope: [%s]" % (self.name, self.short_name, self.get_feature_type_display(), scope_str))


class FeatureScope(models.Model):
    """Model describing the scope of given feature.
    Only relevant if the feature is of type 'String'.
    """

    name = models.CharField(max_length=255)
    """Name of the scope's item"""

    feature = models.ForeignKey(Feature)

    def __unicode__(self):
        return unicode("Feature: %s | Name: %s" % (self.feature.name, self.name))


class FeatureSet(models.Model):
    """Defined group of features describing given classification table.
    Such set is defined per-resource type, and is defined in given classification project.
    """

    name = models.CharField(max_length=255)
    resource_type = models.CharField(choices=Resource.TYPE_CHOICES, max_length=1)
    features = models.ManyToManyField(Feature)

    def __unicode__(self):
        return unicode("Name: %s | Type: %s" %(self.name, self.get_resource_type_display()))

    def get_absolute_url(self):
        return reverse('media_classification:featureset_detail', kwargs={'pk':self.pk})


class Project(models.Model):
    """Describes a single classification project existing withing the system
    """

    name = models.CharField(max_length=255)
    research_project = models.ForeignKey(RProject, related_name='classification_projects')
    collections = models.ManyToManyField(RProjectCollection, through='ProjectCollection', blank=True, null=True, related_name="classifications")
    """Collections assigned to the project"""

    feature_sets = models.ManyToManyField(FeatureSet, blank=True, null=True)
    """Feature sets definitions"""

    date_created = models.DateTimeField(auto_now_add=True)

    cs_enabled = models.BooleanField(default=True)
    """Is crowd-sourcing enabled for the project ?"""

    def __unicode__(self):
        return unicode(self.name)

    def get_all_cs_resources(self):
        """Returns a list of crowd-sourcing enabled resources for given project."""

        resources = []

        if not self.cs_enabled:
            return resources

        for c in self.projectcollection_set.filter(cs_enabled=True):
            new = [r for r in c.collection.resources.all()]
            resources.extend(new)
        return list(set(resources))

    def determine_roles(self, user):
        """Returns a tuple of project roles for given user.

        :param user: user for which the roles are determined
        :type user: :py:class:`django.contrib.auth.models.User`
        :return: list of role names of given user withing the project
        :rtype: str
        """

        return [r.name for r in self.projectrole_set.filter(user=user)]

    def can_update(self, user):
        """Determines whether given user can update the project.

        :param user: user for which the test is made
        :type user: :py:class:`django.contrib.auth.models.User`
        :return: True if user can edit the project, False otherwise
        :rtype: bool
        """

        return self.projectrole_set.filter(user=user, name__in=ProjectRole.ROLE_EDIT).count() > 0

    def can_detail(self, user):
        """Determines whether given user can see the details of a project.

        :param user: user for which the check is made
        :type user: :py:class:`django.contrib.auth.models.User`
        :return: True if user can see the details of the project, False otherwise
        :rtype: bool
        """

        return self.projectrole_set.filter(user=user).count() > 0

    def get_absolute_url(self):
        return reverse('media_classification:project_detail', kwargs={'pk':self.pk})


class Classification(models.Model):
    """Classification made by the Crowd-sourcing user.

    .. note::

        This model is a top-most object in a single classification.
        It's tightly connected with :class:`.ClassificationRow` and :class:`.FeatureAnswer` models.

        Since classification table is composed of rows (which are defined dynamically),
        the rows themselves are stored in database as entries of ClassificationRow model.
        Each row on the other hand can contain a set of *states* for each feature, be it a numerical value,
        or a certain state of the FeatureScope model.
    """

    resource = models.ForeignKey(Resource)
    feature_set = models.ForeignKey(FeatureSet)
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)

    def __unicode__(self):
        return unicode("Id: %s | FeatureSet: %s | Resource: %s" % (self.id, self.feature_set, self.resource.name))


class ClassificationRow(models.Model):
    """Describes a single "row" in a classification table.
    The instances of this model is aggregated by an instance Classification model.

    .. seealso::

        * :class:`Classification`
    """

    classification = models.ForeignKey(Classification)

    def __unicode__(self):
        return unicode("Row of Classification: %d" % (self.classification.id))


class FeatureAnswer(models.Model):
    """A single state of the :class:`.Feature` model.
    The instances of this model are aggregated by an instance ClassificationRow model.

    .. seealso::

        * :class:`ClassificationRow`
    """

    value = models.CharField(max_length=255)
    feature = models.ForeignKey(Feature)
    classification_row = models.ForeignKey(ClassificationRow)

    def __unicode__(self):
        return "Feature: %s | Value: %s | ClassificationId: %s" % (self.feature.name, self.value, self.classification_row.classification.id)

    def get_display_name(self):
        """Returns the name that is to be displayed on a website."""

        # If it's a numerical, return it
        if self.feature.feature_type != Feature.TYPE_STR:
            return unicode(self.value)
        else:
            return unicode(self.feature.featurescope_set.get(pk=int(self.value)).name)


class Sequence(models.Model):
    """Sequence of resources identified by an expert.  """

    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    resources = models.ManyToManyField(Resource, null=True, blank=True)
    project = models.ForeignKey(Project)
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return unicode("Sequence from {date} defined by {user}".format(
            date=self.date_created, user=self.user))

    def get_absolute_url(self):
        return reverse('media_classification:sequence_detail', kwargs={'pk':self.pk})


class ProjectCollection(models.Model):
    """Many-To-Many model for Project-Collection relationship."""

    project = models.ForeignKey(Project)
    collection = models.ForeignKey(RProjectCollection)
    active = models.BooleanField("Active", default=True)
    """Is collection "active" within the project at given moment ?"""

    cs_enabled = models.BooleanField("Crowd-Sourcing", default=True)
    """Is collection available for the crowd-sourcing ?"""

    def __unicode__(self):
        return unicode("%s <-> %s (Active: %s, CS: %s)" % (self.project.name, self.collection, self.active, self.cs_enabled))


class ProjectRole(models.Model):
    """Model describing the user's role withing given :class:`.Project`"""

    ROLE_PROJECT_ADMIN = "A"
    ROLE_EXPERT = "E"
    ROLE_COLLABORATOR = "C"

    ROLE_ANY = (ROLE_PROJECT_ADMIN, ROLE_EXPERT, ROLE_COLLABORATOR, )
    ROLE_EDIT = (ROLE_PROJECT_ADMIN, ROLE_EXPERT, )

    ROLE_CHOICES = (
        (ROLE_PROJECT_ADMIN, "Admin"),
        (ROLE_EXPERT, "Expert"),
        (ROLE_COLLABORATOR, "Collaborator"),
    )

    user = models.ForeignKey(User)
    """User for which the role is defined"""

    name = models.CharField(max_length=1, choices=ROLE_CHOICES)
    """Role name"""

    project = models.ForeignKey(Project)
    """Project for which the role is defined"""

    def __unicode__(self):
        return unicode("%s | Project: %s | Role: %s " % (self.user.username, self.project.name, self.get_name_display()))
