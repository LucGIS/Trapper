from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views import generic
from django.core.urlresolvers import reverse, reverse_lazy

class UserProfileDetailView(generic.DetailView):
	model = User
	template_name = "accounts/user_detail.html"
	context_object_name = 'u'

class UserProfileUpdateView(generic.UpdateView):
	model = User
	template_name = "accounts/user_update.html"
	context_object_name = 'u'
	fields = ['username','first_name','last_name','email']
	#success_url = 
	#reverse_lazy('accounts:userprofile_detail')

	def get_success_url(self):
		return reverse_lazy('accounts:userprofile_detail', kwargs={'pk':self.request.user.pk,})

def logout_action(request):
	logout(request)
	return redirect('trapper.apps.accounts.login')

