from django.contrib.auth.models import User
from guardian.shortcuts import assign_perm, remove_perm
from trapper.apps.storage.models import Resource
from trapper.apps.research.models import Project
import itertools


def collection_m2m_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    # TODO:asynchronous task needed?
    """ Assign/remove appropriate view permissions when collection is changed. """
    if action == 'pre_clear':
        instance._old_m2m = set(list(instance.resources.values_list('pk', flat=True)))
    if action == 'post_add' and hasattr(instance, '_old_m2m'):
        added = pk_set - instance._old_m2m
        removed = instance._old_m2m - pk_set
        if added or removed:
            projects = Project.objects.filter(
                pk__in=instance.projectcollection_set.values_list('project_id', flat=True)
            )
            if projects:
                users = User.objects.filter(pk__in=set(list(itertools.chain(*[project.projectrole_set.values_list('user_id', flat=True) for project in projects]))))
                for user in users:
                    if added:
                        added_qs = Resource.objects.filter(pk__in=added)
                        for resource in added_qs:
                            if not resource.can_view(user):
                                assign_perm("view_resource_PRO", user, resource)
                    if removed:
                        removed_qs = Resource.objects.filter(pk__in=removed)
                        for resource in removed_qs:
                            checkset = resource.has_access(user, return_checkset=True)
                            if not len(checkset) > 0:
                                remove_perm("view_resource_PRO", user, resource)
