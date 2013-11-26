from trapper.apps.animal_observation.models import Project, ProjectRole
from django.shortcuts import redirect

from functools import wraps

def project_role_required(roles, access_denied_page):
	def decorator(func):
		def inner(request, project_id, *args, **kwargs):
			project = Project.objects.get(id=project_id)
			role = None
			if request.user:
				if request.user.is_authenticated():
					role = ProjectRole.objects.filter(user=request.user, project=project)
			if role:
				role = role[0]
				if role.name in roles:
					return func(request, project_id, *args, **kwargs)
			else:
				return redirect(access_denied_page)
		return wraps(func)(inner)
	return decorator
