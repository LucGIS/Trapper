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
