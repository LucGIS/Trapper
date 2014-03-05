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

from django import forms

from trapper.apps.media_classification.models import Project
from trapper.apps.storage.models import Resource, Collection
from trapper.tools.batch_uploading import ConfigFileValidator

from djangular.forms import NgModelFormMixin
from tinymce.widgets import TinyMCE
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Div

############################################################################
# RESOURCE FORMS
############################################################################


class ResourceForm(forms.ModelForm):
    """Model form for creating and updating :class:`.Resource` objects
    """

    class Meta:
        model = Resource
        exclude = ['uploader', ]

    def __init__(self, *args, **kwargs):
        kwargs.pop('user', None)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.error_text_inline = True
        self.helper.form_show_errors = True
        self.helper.help_text_inline = False
        super(ResourceForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['managers'] = [str(t.pk) for t in self.instance.managers.all()]
            self.fields['managers'].help_text = 'Select your managers'  # Django bug
            self.fields['date_recorded'].widget.attrs['datetimepicker'] = ''

    def save(self, force_insert=False, force_update=False, commit=True):
        """On resource save, the update of the metadata is performed
        (see :meth:`.Resource.update_metadata`)
        """
        r = super(ResourceForm, self).save(commit=False)
        if commit:
            r.save()
            r.update_metadata(commit=True)
        return r


class ResourceAjaxForm(NgModelFormMixin, ResourceForm):
    class Meta:
        model = Resource
        exclude = ['file', 'extra_file', 'uploader', 'mime_type', 'extra_mime_type', 'resource_type']


class ResourceRequestForm(forms.Form):
    text = forms.CharField(widget=TinyMCE(attrs={'cols': 60, 'rows': 15}))
    object_pk = forms.IntegerField(widget=forms.HiddenInput())


############################################################################
# COLLECTION FORMS
############################################################################

class CollectionForm(NgModelFormMixin, forms.ModelForm):
    """Model form for creating and updating :class:`.Collection` objects
    """

    class Meta:
        model = Collection
        exclude = ['uploader', 'owner', 'resources']

    def __init__(self, *args, **kwargs):
        kwargs.pop('user', None)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.error_text_inline = True
        self.helper.form_show_errors = True
        self.helper.form_action = '#'
        self.helper.help_text_inline = False
        self.helper.layout = Layout(
            'name',
            'description',
            'managers',
            'status'
        )
        super(CollectionForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['managers'] = [str(t.pk) for t in self.instance.managers.all()]
        self.fields['managers'].help_text = 'Select your managers'  # Django bug


class CollectionAjaxForm(CollectionForm):

    def __init__(self, *args, **kwargs):
        super(CollectionAjaxForm, self).__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                Div(
                    'name',
                    'managers',
                    'status',
                    css_class="col-md-4"
                ),
                Div(
                    'description',
                    HTML('<button type="button" class="btn btn-primary btn-lg" ng-click="collection_update_submit()">Update collection</button>'),
                    css_class="col-md-8"
                ),
                css_class="row"
            )
        )


class CollectionRequestForm(forms.Form):
    """Defines a form for creating a collection request for the :class:`Project` object."""

    text = forms.CharField(widget=TinyMCE(attrs={'cols': 60, 'rows': 15}))
    project = forms.ModelChoiceField(queryset=Project.objects.none())
    object_pk = forms.IntegerField(widget=forms.HiddenInput())


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


############################################################################
# DJANGO-FILTER FORMS
############################################################################


class ResourceFilterForm(NgModelFormMixin, forms.Form):

    class Meta:
        model = Resource

    def __init__(self, *args, **kwargs):
        kwargs.update(scope_prefix='filter_data')
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.error_text_inline = True
        self.helper.form_show_errors = False
        self.helper.form_action = '#'
        self.helper.help_text_inline = False
        # bootstrap3 inline form
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'crispy_forms/bootstrap3/layout/crispy_filter_field.html'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            'resource_type',
            'status',
            'date_uploaded',
        )
        super(ResourceFilterForm, self).__init__(*args, **kwargs)
