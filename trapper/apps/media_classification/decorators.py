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

from trapper.apps.media_classification.models import Project, ProjectRole
from django.shortcuts import redirect

from functools import wraps

def project_role_required(roles, access_denied_page):
	"""Determines whether request.user contains the necessary project roles.

	:param roles: iterable of role names required (any)
	:type roles: list
	"""

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
