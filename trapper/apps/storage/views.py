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

from django.shortcuts import get_object_or_404
from django.views import generic
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime
from braces.views import LoginRequiredMixin

from trapper.apps.storage.models import Resource, Collection, CollectionUploadJob
from trapper.apps.storage.tasks import process_collection_upload
from trapper.apps.storage.forms import ResourceForm, ResourceAjaxForm, CollectionForm, CollectionAjaxForm, ResourceRequestForm, CollectionRequestForm, CollectionUploadForm, CollectionUploadFormPart2
from trapper.apps.research.models import Project, ProjectRole
from trapper.apps.messaging.models import Message, CollectionRequest, ResourceRequest
from trapper.apps.common.decorators import ObjectAccessRequiredMixin
from trapper.apps.storage.filters import ResourceFilter
from trapper.apps.common.views import AngularNgGridMixin, AjaxFormMixin


class ResourceListView(AngularNgGridMixin):
    """Displays the list of :class:`.Resource` objects.
    This view employs the filtering features.
    The method filters the standard result according to the passed GET parameters.
    """

    list_model = Resource
    list_model_filter = ResourceFilter
    search_fields = ('name', 'owner__username')
    object_properties = ('pk', 'name', 'resource_type', 'owner__username', 'status', 'date_recorded')
    template_name = 'storage/resource_list.html'

    def get_queryset(self, *args, **kwargs):
        """
        """
        if not self.request.user.is_authenticated():
            self.queryset = Resource.objects.filter(status='Public').order_by('name')
        else:
            self.queryset = Resource.objects.exclude(Q(owner=self.request.user)|Q(managers=self.request.user)).exclude(status='Private').order_by('name')

    def get_extra_fields(self, qs_p):
        extra_fields = []
        for q in qs_p:
            try:
                extra_fields.append({'thumbnail_large': q.file['video'].url, 'thumbnail_default': q.file['default'].url, 'ajaxurl' : '\'/storage/resource/update/%s\'' % q.pk})
            except:
                extra_fields.append({'thumbnail_large': '/static/img/no_thumb_100x100.jpg', 'thumbnail_default': '/static/img/no_thumb_100x100.jpg'})
        return extra_fields


class UserResourceListView(LoginRequiredMixin, ResourceListView):
    """Displays the list of resources of given :py:class:`django.contrib.auth.models.User`
    It mirrors the functionality of :class:`.ResourceListView`,
    except it filters the queryset initally according to the resource ownership.
    """

    object_edit_tools = True
    template_name = 'storage/user_resource_list.html'

    def get_queryset(self, *args, **kwargs):
        """Return the queryset filtered by the resources which are owned by given user.
        """
        self.queryset = Resource.objects.filter(Q(owner=self.request.user)|Q(managers=self.request.user)).order_by('name')


class ResourceDetailView(ObjectAccessRequiredMixin, generic.DetailView):
    """ Resource can be public or not; if not it can be listed but only allowed users can view a content (details)
    Given resource can be viewed when user passes :func:`Resource.can_view` check.
    """

    model=Resource
    access_func = Resource.can_view

    def dispatch(self, *args, **kwargs):
        return super(ResourceDetailView, self).dispatch(*args, **kwargs)


class ResourceDeleteView(LoginRequiredMixin, ObjectAccessRequiredMixin, generic.DeleteView):
    """Delete view of the resource object.
    Given resource can be removed when user is the owner or the uploader of the resource.
    """

    model=Resource
    access_func = Resource.can_delete
    success_url='resource/list/'
    context_object_name='object'
    template_name='storage/object_confirm_delete.html'

    def dispatch(self, *args, **kwargs):
        return super(ResourceDeleteView, self).dispatch(*args, **kwargs)

        def get_context_data(self, *args, **kwargs):
            context = super(ResourceDeleteView, self).get_context_data(*args, **kwargs)
            resource = context['object']
            if  not resource.can_be_deleted(self.request.user):
                context['move_to_archive'] = True
            return context

        def delete(self, request, *args, **kwargs):
            self.object = self.get_object()
            if request.POST.get('submit') == 'Move to archive':
                self.object.move2archive()
            else:
                self.object.delete()
            return HttpResponseRedirect(self.get_success_url())


class ResourceUpdateView(LoginRequiredMixin, ObjectAccessRequiredMixin, AjaxFormMixin, generic.UpdateView):
    """Update view of the resource object.
    Given resource can be updated when user passes :func:`Resource.can_update` check.
    """

    content_type = "text/html"
    model = Resource
    raise_exception = True
    ajax_form = ResourceAjaxForm
    access_func = Resource.can_update

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(ResourceUpdateView, self).dispatch(*args, **kwargs)

    def update_form_fields(self, obj, request, in_data, bound_form):
        obj.managers.clear()
        obj.managers.add(*list(bound_form.cleaned_data['managers']))
        return obj


class ResourceCreateView(LoginRequiredMixin, generic.CreateView):
    """Update view of the resource object.
    Given resource can be updated when user passes an access function.
    """

    model = Resource
    form_class= ResourceForm

    def form_valid(self, form):
        form.instance.uploader = self.request.user
        return super(ResourceCreateView, self).form_valid(form)


class UserCollectionListView(LoginRequiredMixin, generic.ListView):
    """Collection list, initially filtered by the collections owned by given user.
    """

    model = Collection
    context_object_name = 'collections'

    def get_queryset(self):
        """Filters the queryset according to the user's id. """

        user = get_object_or_404(User, pk=self.kwargs['user_pk'])
        return Collection.objects.filter(owner=user)


class CollectionDetailView(LoginRequiredMixin, ResourceListView):

    template_name = 'storage/collection_detail.html'

    def get_extra_json_content(self):
        obj = get_object_or_404(Collection, pk=self.kwargs['pk'])
        if self.request.user == obj.owner or self.request.user in obj.managers.all():
            return {'object_edit_tools' : True,}

    def get_queryset(self, *args, **kwargs):
        self.queryset = Resource.objects.filter(collection__pk=self.kwargs['pk'])

    def get_context_data(self, *args, **kwargs):
        context = super(CollectionDetailView, self).get_context_data(*args, **kwargs)
        context['collection'] = get_object_or_404(Collection, pk=self.kwargs['pk'])
        return context


class CollectionCreateView(LoginRequiredMixin, AjaxFormMixin):
    """Collection's create view.
    Handles the creation of the Collection object.
    """

    raise_exception = True
    ajax_form = CollectionForm

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(CollectionCreateView, self).dispatch(*args, **kwargs)

    def json_in_data_test(self, in_data, request):
        if not in_data['resources']:
            msg = 'You did not select any resources'
            return msg
        qs = Resource.objects.filter(Q(owner=request.user)|Q(managers=request.user))
        if set(in_data['resources']) - set(qs.values_list('pk', flat=True)):
            raise PermissionDenied()

    def update_form_fields(self, obj, request, in_data, bound_form):
        obj.owner = get_object_or_404(User, pk=request.user.pk)
        obj.uploader = get_object_or_404(User, pk=request.user.pk)
        obj.save()
        resources = Resource.objects.filter(pk__in=in_data['resources'])
        obj.resources.add(*list(resources))
        obj.managers.add(*list(bound_form.cleaned_data['managers']))
        return obj


class CollectionUpdateView(ObjectAccessRequiredMixin, UserResourceListView):
    """Collection's update view.
    Handles the update of the Collection object.
    """

    model = Collection
    access_func = Collection.can_update
    object_edit_tools = True
    template_name = 'storage/collection_update.html'

    def dispatch(self, *args, **kwargs):
        return super(CollectionUpdateView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        return get_object_or_404(Collection, pk=self.kwargs['pk'])

    def get_extra_json_content(self):
        obj = self.get_object()
        resources = obj.resources.values_list('pk', flat=True)
        return {'preselection':str(resources),}


class CollectionUpdateView2(LoginRequiredMixin, ObjectAccessRequiredMixin, AjaxFormMixin, generic.UpdateView):

    content_type = "text/html"
    model = Collection
    raise_exception = True
    ajax_form = CollectionAjaxForm
    access_func = Collection.can_update

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(CollectionUpdateView2, self).dispatch(*args, **kwargs)

    def json_in_data_test(self, in_data, request):
        if not in_data['resources']:
            msg = 'You did not select any resources'
            return msg

    def update_form_fields(self, obj, request, in_data, bound_form):
        obj.managers.clear()
        obj.managers.add(*list(bound_form.cleaned_data['managers']))
        resources = Resource.objects.filter(pk__in=in_data['resources'])
        obj.resources.clear()
        obj.resources.add(*list(resources))
        return obj


# Uploading collections through YAML and archive files
class CollectionUploadViewPart2(LoginRequiredMixin, generic.FormView):
    """Collection's upload view.
    This is the second part of the collection upload process.
    See :class:`.CollectionUploadView` for more details.
    This view handles the processing of the uploaded archive file, as well as its validation and the final
    uploading action.
    """

    template_name = "storage/collection_upload.html"
    form_class = CollectionUploadFormPart2
    success_url = reverse_lazy('msg')

    def get_context_data(self, *args, **kwargs):
        context = super(CollectionUploadViewPart2, self).get_context_data(*args, **kwargs)
        return context

    def get_initial(self, *args, **kwargs):
        initial = {
            'job_pk':self.kwargs['pk'],
        }
        return initial

    def form_valid(self, form):
        """Processes the uploaded archive file and delegates a
        :func:`.process_collection_upload` task.
        """

        messages.success(self.request, "<strong>Resources uploaded!</strong> System will process your request soon.")
        job = CollectionUploadJob.objects.get(pk=form.cleaned_data['job_pk'])
        job.archive = form.cleaned_data['archive_file']
        job.save()
        process_collection_upload.delay(job.pk)
        return super(CollectionUploadViewPart2, self).form_valid(form)


class CollectionUploadView(LoginRequiredMixin, generic.FormView):
    """This is the first controller of the two-step process of uploading a collection data (also called **batch_uploading**).
    This view displays a form with a single file upload input for the definition file.
    The file is validated and then the :class:`.CollectionUploadJob` object is created.
    """

    template_name = "storage/collection_upload.html"
    form_class= CollectionUploadForm
    success_url = reverse_lazy('storage:collection_upload')

    def form_valid(self, form):
        """Validates the configuration file using :meth:`.CollectionUploadForm.validate_config_file`,
        and creates the :class:`.CollectionUploadJob` object.
        """

        err = form.validate_config_file(self.request.user)
        if err != "OK":
            messages.error(self.request, "<strong>Definition file error!</strong> %s" % (err,))
            return super(CollectionUploadView, self).form_valid(form)
        else:
            messages.success(self.request, "<strong>Success!</strong> Definition file is valid, please upload the archive file (.zip)")
            job = CollectionUploadJob.objects.create(definition=form.cleaned_data['definition_file'], owner=self.request.user)
            return HttpResponseRedirect(reverse('storage:collection_upload_2',kwargs={'pk':job.pk}))


# Deleting collections
class CollectionDeleteView(LoginRequiredMixin, ObjectAccessRequiredMixin, generic.DeleteView):
    """This class handles the deletion of the :class:`.Collection` object.
    The collection object can be deleted by the managers and the owner of the collection.
    """

    model = Collection
    access_func = Collection.can_update
    success_url='collection/list/'
    context_object_name='object'
    template_name='storage/object_confirm_delete.html'
    access_func = Collection.can_update

    def dispatch(self, *args, **kwargs):
        return super(CollectionDeleteView, self).dispatch(*args, **kwargs)


# Requesting collections for the research.Project model
class CollectionRequestView(LoginRequiredMixin, generic.FormView):
    """This is the view generating the collection request page for the :class:`.Project`.
    It will only display the projects in which the user has the admin :class:`.ProjectRole`.
    """

    success_url = reverse_lazy('storage:collection_list')
    template_name = "storage/collection_request.html"
    form_class = CollectionRequestForm

    # Template of the request message
    TEXT_TEMPLATE = "Dear %s,<br/>I would like to ask you for the permission to use the %s.<br/><br/>Best regards,<br/>%s"

    # Only Project Admins and Experts can request for the resources
    REQUIRED_PROJECT_ROLES = [ProjectRole.ROLE_PROJECT_ADMIN, ProjectRole.ROLE_EXPERT]

    def get_form(self, form_class, *args, **kwargs):
        """Gets the form the request view.

        FEATURE REQUEST:
        Logic below should be in :meth:`self.get_initial` method.
        For some reason, the initial data for 'project' does not work as expected.
        Specifically, ModelChoiceField does not initialize with a QuerySet through the constructor.
        """
        form = super(CollectionRequestView, self).get_form(form_class, *args, **kwargs)

        project_pks = set(role.project.pk for role in self.request.user.research_roles.filter(name__in=self.REQUIRED_PROJECT_ROLES))
        projects = Project.objects.filter(pk__in=project_pks)
        form.fields['project'].queryset = projects
        return form


    def get_context_data(self, *args, **kwargs):
        context = super(CollectionRequestView, self).get_context_data(*args, **kwargs)

        # self.collection was set previously in the "get_initial" method
        context['collection'] = self.collection
        return context

    def get_initial(self, *args, **kwargs):
        """Initialize the form with the projects query, as well as the collection in question.
        """
        self.collection = get_object_or_404(Collection, pk=self.kwargs['pk'])
        projects = Project.objects.all()
        initial = {
            'object_pk':self.collection.pk,
            'project': projects,
            'text': self.TEXT_TEMPLATE % (
                self.collection.owner.username,
                self.collection.name,
                self.request.user.username
            )
        }
        return initial

    def form_valid(self, form):
        """Create a :class:`.Message` and :class:`.CollectionRequest` objects
        directed at the owner of the collection.
        """
        print "Send email, add message"
        collection = get_object_or_404(Collection, pk=form.cleaned_data['object_pk'])
        project = form.cleaned_data['project']
        msg = Message.objects.create(subject="Request for collections", text=form.cleaned_data['text'], user_from=self.request.user,user_to=collection.owner, date_sent=datetime.now())
        coll_req = CollectionRequest(name="Request for collections", user=collection.owner, message=msg, project=project)
        coll_req.save()
        coll_req.collections.add(collection)
        return super(CollectionRequestView, self).form_valid(form)

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(self.get_context_data(form=form))


class ResourceRequestView(LoginRequiredMixin, generic.FormView):

    success_url = reverse_lazy('storage:resource_list')
    template_name = "storage/resource_request.html"
    form_class = ResourceRequestForm

    # Template of the request message
    TEXT_TEMPLATE = "Dear %s,<br/>I would like to ask you for the permission to use the %s.<br/><br/>Best regards,<br/>%s"

    def get_context_data(self, *args, **kwargs):
        context = super(ResourceRequestView, self).get_context_data(*args, **kwargs)

        # self.resource was set previously in the "get_initial" method
        context['resource'] = self.resource
        return context

    def get_initial(self, *args, **kwargs):
        """Initialize the form with the projects query, as well as the collection in question.
        """
        self.resource = get_object_or_404(Resource, pk=self.kwargs['pk'])
        initial = {
            'object_pk':self.resource.pk,
            'text': self.TEXT_TEMPLATE % (
                self.resource.owner.username,
                self.resource.name,
                self.request.user.username
            )
        }
        return initial

    def form_valid(self, form):
        """Create a :class:`.Message` and :class:`.ResourceRequest` objects
        directed at the owner of the resource.
        """
        print "Send email, add message"

        resource = get_object_or_404(Resource, pk=form.cleaned_data['object_pk'])
        msg = Message.objects.create(subject="Request for resources: %s" % resource.name, text=form.cleaned_data['text'], user_from=self.request.user,user_to=resource.owner, date_sent=datetime.now())
        res_req = ResourceRequest(name="Request for resources %s" % resource.name, user=resource.owner, message=msg, user_from=self.request.user)
        res_req.save()
        res_req.resources.add(resource)
        return super(ResourceRequestView, self).form_valid(form)

