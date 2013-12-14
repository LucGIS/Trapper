############################################################################
#   Copyright (c) 2013  Trapper development team                           #
#                                                                          #
#   This file is a part of Trapper.                                        #
#                                                                          #
#   This program is free software; you can redistribute it and/or modify   #
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

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views import generic
from django.core.urlresolvers import reverse, reverse_lazy

class UserProfileDetailView(generic.DetailView):
	"""Displays the profile details about an arbitrary user."""

	model = User
	template_name = "accounts/user_detail.html"
	context_object_name = 'u'

class SessionUserProfileDetailView(UserProfileDetailView):
	"""Displays the profile details about user stored in session."""

	def get_object(self):
		return self.request.user

class UserProfileUpdateView(generic.UpdateView):
	"""Update view for the user profile."""

	model = User
	template_name = "accounts/user_update.html"
	context_object_name = 'u'
	fields = ['username','first_name','last_name','email']

	def get_success_url(self):
		return reverse_lazy('accounts:userprofile_detail', kwargs={'pk':self.request.user.pk,})

def logout_action(request):
	logout(request)
	return redirect('trapper.apps.accounts.login')

