from guardian.shortcuts import assign_perm, remove_perm
from django.contrib.auth.models import User


# PROJECT COLLECTIONS
def assign_research_project_collection_permissions(sender, *args, **kwargs):
    """post_save signal to assign view permission
       to all resources in a new research_project_collection
       for all users that belong to research_project
    """

    if kwargs['created']:
        instance = kwargs['instance']
        users = User.objects.filter(pk__in=instance.project.projectrole_set.values_list('user_id', flat=True))
        for user in users:
            for resource in instance.collection.resources.all():
                if not resource.can_view(user):
                    assign_perm("view_resource_PRO", user, resource)


def remove_research_project_collection_permissions(sender, *args, **kwargs):
    instance = kwargs['instance']
    users = User.objects.filter(pk__in=instance.project.projectrole_set.values_list('user_id', flat=True))
    for user in users:
        for resource in instance.collection.resources.all():
            checkset = resource.has_access(user, return_checkset=True)
            if not len(checkset) > 0:
                remove_perm("view_resource_PRO", user, resource)


# PROJECT ROLES
def assign_research_project_role_permissions(sender, *args, **kwargs):
    if kwargs['created']:
        instance = kwargs['instance']
        project_collections = instance.project.projectcollection_set.all()
        for project_collection in project_collections:
            for resource in project_collection.collection.resources.all():
                if not resource.can_view(instance.user):
                    assign_perm("view_resource_PRO", instance.user, resource)


def remove_research_project_role_permissions(sender, *args, **kwargs):
    instance = kwargs['instance']
    project_collections = instance.project.projectcollection_set.all()
    for project_collection in project_collections:
        for resource in project_collection.collection.resources.all():
            checkset = resource.has_access(instance.user, return_checkset=True)
            if not len(checkset) > 0:
                remove_perm("view_resource_PRO", instance.user, resource)
