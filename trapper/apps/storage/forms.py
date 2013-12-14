from ajax_select import make_ajax_field
from tinymce.widgets import TinyMCE

from django import forms

from trapper.apps.media_classification.models import Project
from trapper.apps.storage.models import Resource, Collection
from trapper.apps.geomap.models import Location

from trapper.tools.batch_uploading import ConfigFileValidator

class CollectionRequestForm(forms.Form):
	"""Defines a form for creating a collection request for the :class:`Project` object."""

	text = forms.CharField(widget=TinyMCE(attrs={'cols':60, 'rows':15}))
	project = forms.ModelChoiceField(queryset=Project.objects.none())
	collection_pk = forms.IntegerField(widget=forms.HiddenInput())

class CollectionUploadForm(forms.Form):
	"""Defines a form for uploading a collection from the archive.
	This form handles the **first step** of the action - uploading and validating the definition file.
	The validation is done by the :class:`.ConfigFileValidator` object.
	"""

	definition_file = forms.FileField()

	def validate_config_file(self, user):
		"""Validates the config file using the :class:`.ConfigFileValidator` object.
		:class:`django.contrib.auth.models.User` object is provided as a parameter, because
		the definition may require to perform action which may not be permitted for the user.

		:param user: instance of the who requests the validation
		:type user: :class:`django.contrib.auth.models.User`
		"""

		errors = ConfigFileValidator(self.cleaned_data['definition_file'], user).check_errors()
		if errors:
			return errors
		return "OK"

class CollectionUploadFormPart2(forms.Form):
	"""Defines a form for uploading a collection from the archive.
	This form handles the **second step** of the action - uploading the archive file.
	There is no archive validation done in this form (as it was in the first step) because
	the final action is delegated to the task daemon.
	"""

	archive_file = forms.FileField()
	job_pk = forms.IntegerField(widget=forms.HiddenInput)

class CollectionForm(forms.ModelForm):
	"""Model form for creating and updating :class:`.Collection` objects
	"""

	class Meta:
		model = Collection
	
	owner = make_ajax_field(Collection, 'owner', 'user', help_text=None, plugin_options={'autoFocus':True,})
	resources = make_ajax_field(Collection, 'resources', 'resource', help_text=None, show_help_text=False, plugin_options={'autoFocus':True,})
	managers = make_ajax_field(Collection, 'managers', 'user', help_text=None, show_help_text=False, plugin_options={'autoFocus':True,})

class ResourceForm(forms.ModelForm):
	"""Model form for creating and updating :class:`.Resource` objects
	"""
	class Meta:
		model = Resource
		# exclude the 'uploader' field as it is always the request.user
		exclude=['uploader', 'thumbnail', 'mime_type', 'resource_type']

	def save(self, force_insert=False, force_update=False, commit=True):
		"""On resource save, the update of the metadata is performed
		(see :meth:`.Resource.update_metadata`)
		"""

		r = super(ResourceForm, self).save(commit=False)
		if commit:
			r.save()
			r.update_metadata(commit=True)
		return r
	
	owner = make_ajax_field(Collection, 'owner', 'user', help_text=None, plugin_options={'autoFocus':True,})
	managers = make_ajax_field(Collection, 'managers', 'user', help_text=None, show_help_text=False, plugin_options={'autoFocus':True,})
