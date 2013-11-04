from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

@login_required
def profile_details(request):
	user = request.user
	context = {'user': user}
	return render(request, 'accounts/profile_details.html', context)

def logout_action(request):
	logout(request)
	return redirect('trapper.apps.accounts.login')

