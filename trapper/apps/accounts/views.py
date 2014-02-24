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

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.views import generic
from django.core.urlresolvers import reverse_lazy


class UserRegistrationView(generic.FormView):
	"""Displays the user registration form and creates a new user."""

	form_class = UserCreationForm
	template_name = 'registration/register.html'
	success_url = reverse_lazy('accounts:login')

	def form_valid(self, form):
		form.save()
		messages.success(self.request, "<strong>Account Created!</strong>Please login using your username and password.")
		return super(UserRegistrationView, self).form_valid(form)

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

