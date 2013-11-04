from trapper.apps.animal_observation.models import AnimalFeature, AnimalFeatureAnswer, AnimalFeatureScope, ClassificationProject, ResourceClassification, ResourceClassificationItem, ResourceExtra, ClassificationProjectRole
from django.shortcuts import redirect

from functools import wraps

def project_role_required(roles, redirect_page):
	def decorator(func):
		def inner(request, project_id, *args, **kwargs):
			project = ClassificationProject.objects.get(id=project_id)
			role = None
			if request.user:
				if request.user.is_authenticated():
					role = ClassificationProjectRole.objects.filter(user=request.user, project=project)
			if role:
				role = role[0]
				if role.name in roles:
					return func(request, project_id, *args, **kwargs)
			else:
				return redirect(redirect_page)
		return wraps(func)(inner)
	return decorator
