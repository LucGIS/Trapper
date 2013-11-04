from django import forms

class CreateUserForm(forms.Form):
	username = forms.CharField(max_length=100)
	password
