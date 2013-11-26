from django.core.exceptions import PermissionDenied

from functools import wraps

def object_access_required(modelname, access_func):
	"""
	At the moment this decorator checks whether request.user passes certain access_func.

	TODO: It should also check whether the user is authenticated:
	2. Verifies the access for request.user to an instance of 'modelname' class object using the access_func.
	Object is identified by the 'pk' item from the request.GET
	"""
	def decorator(func):
		def inner(request, pk, *args, **kwargs):
			some_object = modelname.objects.get(id=pk)
			if access_func(request.user, some_object):
				return func(request, pk, *args, **kwargs)
			else:
				raise PermissionDenied
		return wraps(func)(inner)
	return decorator
