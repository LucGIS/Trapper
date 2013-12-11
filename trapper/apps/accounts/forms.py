from django import forms

class CreateUserForm(forms.Form):
	"""User registration form."""

	username = forms.CharField(max_length=100)
