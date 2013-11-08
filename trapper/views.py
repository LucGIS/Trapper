from django.shortcuts import render

def index(request):
	return render(request, 'index.html', { })

def message(request, msg_id):
	"""
	Temporary page for testing permissions and errors.
	"""
	ERRORS = {
		1 : "You do not have sufficient privileges to access this project",
		2 : "You do not have sufficient privileges to access this resource",
	}
	context = {'message': ERRORS[int(msg_id)]}
	return render(request, 'message.html', context)
