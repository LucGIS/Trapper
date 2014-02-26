from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from trapper.apps.storage.models import Collection


class Project(models.Model):
    """Describes a research project existing withing the system """

    name = models.CharField(max_length=255)
    description = models.TextField(max_length=2000, null=True, blank=True)

    collections = models.ManyToManyField(Collection, through='ProjectCollection', blank=True, null=True,  related_name='research_projects')
    """Collections assigned to the project"""
    date_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return unicode(self.name)

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

    def can_delete(self, user):
        """Determines whether given user can delete the project.

        :param user: user for which the test is made
        :type user: :py:class:`django.contrib.auth.models.User`
        :return: True if user can delete the project, False otherwise
        :rtype: bool
        """

        return self.projectrole_set.filter(user=user, name__in=ProjectRole.ROLE_DELETE).count() > 0


    def can_detail(self, user):
        """Determines whether given user can see the details of a project.

        :param user: user for which the check is made
        :type user: :py:class:`django.contrib.auth.models.User`
        :return: True if user can see the details of the project, False otherwise
        :rtype: bool
        """

        return self.projectrole_set.filter(user=user).count() > 0

    def get_absolute_url(self):
        return reverse('research:project_detail', kwargs={'pk':self.pk})


class ProjectRole(models.Model):
    """Model describing the user's role withing given :class:`.Project`"""

    ROLE_PROJECT_ADMIN = "A"
    ROLE_EXPERT = "E"
    ROLE_COLLABORATOR = "C"

    ROLE_ANY = (ROLE_PROJECT_ADMIN, ROLE_EXPERT, ROLE_COLLABORATOR, )
    ROLE_EDIT = (ROLE_PROJECT_ADMIN, ROLE_EXPERT, )
    ROLE_DELETE = (ROLE_PROJECT_ADMIN,)

    ROLE_CHOICES = (
        (ROLE_PROJECT_ADMIN, "Admin"),
        (ROLE_EXPERT, "Expert"),
        (ROLE_COLLABORATOR, "Collaborator"),
    )

    user = models.ForeignKey(User, related_name='research_roles')
    """User for which the role is defined"""

    name = models.CharField(max_length=1, choices=ROLE_CHOICES)
    """Role name"""

    project = models.ForeignKey(Project)
    """Project for which the role is defined"""

    def __unicode__(self):
        return unicode("%s | Project: %s | Role: %s " % (self.user.username, self.project.name, self.get_name_display()))


class ProjectCollection(models.Model):
    """Many-To-Many model for Project-Collection relationship."""

    project = models.ForeignKey(Project)
    collection = models.ForeignKey(Collection)

    def __unicode__(self):
        return unicode("%s <-> %s" % (self.project.name, self.collection.name))

    def save(self, *args, **kwargs):
        super(ProjectCollection, self).save(*args, **kwargs)


# register signals
from django.db.models.signals import post_save, post_delete
from signals import assign_research_project_collection_permissions, remove_research_project_collection_permissions, assign_research_project_role_permissions, remove_research_project_role_permissions

post_save.connect(assign_research_project_collection_permissions, sender=ProjectCollection)
post_delete.connect(remove_research_project_collection_permissions, sender=ProjectCollection)

post_save.connect(assign_research_project_role_permissions, sender=ProjectRole)
post_delete.connect(remove_research_project_role_permissions, sender=ProjectRole)

