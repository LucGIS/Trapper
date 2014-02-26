from django.core.exceptions import ImproperlyConfigured
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.views.generic import View,TemplateView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from braces.views import AjaxResponseMixin, JSONResponseMixin
from crispy_forms.utils import render_crispy_form
import json
import datetime
import decimal
from django.utils import timezone


class TrapperDjangoJSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types.
    """
    def default(self, o):
        if isinstance(o, datetime.datetime):
            if timezone.is_aware(o):
                r = timezone.localtime(o)
            else:
                r = o
            return r.strftime("%Y-%m-%d %H:%M")
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if timezone.is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(TrapperDjangoJSONEncoder, self).default(o)


# some angularjs ng-grid related mixins
class AngularNgGridMixin(JSONResponseMixin, AjaxResponseMixin, TemplateView):
    '''
    '''
    # OPTIONS:JSONResponseMixin
    #--------------------------------------#
    content_type ="text/html"
    #json_dumps_kwargs = None

    # OPTIONS:TemplateView
    #--------------------------------------#
    template_name = None

    # OPTIONS:AngularNgGridMixin
    #--------------------------------------#
    list_model = None # django model that will be used to feed nggrid
    list_model_filter = None # 'django-filter' filter class
    pageSize_request_str = 'pageSize'
    pageNumber_request_str = 'pageNumber'
    search_request_str = 'search'
    search_fields = None
    object_properties = ('pk',)
    object_edit_tools = False
    #--------------------------------------#

    def render_json_response(self, context_dict, status=200):
        json_context = json.dumps(context_dict, cls=TrapperDjangoJSONEncoder,
                                  **self.get_json_dumps_kwargs())
        return HttpResponse(json_context,
                            content_type=self.get_content_type(),
                            status=status)

    def get_context_data(self, *args, **kwargs):
        context = super(AngularNgGridMixin, self).get_context_data(*args, **kwargs)
        context['filtering_form'] = self.list_model_filter(self.request.GET).form
        context['model_name'] = self.list_model._meta.model_name.capitalize()
        return context

    def get_queryset(self, *args, **kwargs):
        if self.list_model is None:
            raise ImproperlyConfigured(
                "%(cls)s is missing the model. "
                "Define %(cls)s.model or override "
                "%(cls)s.__get_queryset()." % {"cls": self.__class__.__name__})
        qs = self.list_model.objects.all()
        self.queryset = qs

    def filter_data(self, request, *args, **kwargs):
        if self.list_model_filter is None:
            return None
        filtered_queryset = self.list_model_filter(self.request.GET, queryset=self.queryset)
        self.queryset = filtered_queryset.qs

    def search_data(self, request, *args, **kwargs):
        if self.search_fields is None:
            raise ImproperlyConfigured(
                "%(cls)s is missing the search_fields. "
                "Define %(cls)s.search_fields or override "
                "%(cls)s.filter_data()." % {"cls": self.__class__.__name__})
        search = self.request.GET.get(self.search_request_str)
        if search:
            search_words = search.split()
            filters = None
            for f in self.search_fields:
                for word in search_words:
                    q = Q(**{f + '__icontains': word})
                    filters = filters | q if filters else q
            if filters:
                filtered_qs = self.queryset.filter(filters)
            self.queryset = filtered_qs

    def get_paginated_data(self, request, *args, **kwargs):
        pageSize = self.request.GET.get(self.pageSize_request_str)
        if pageSize:
            paginator = Paginator(self.queryset, pageSize)
            pageNumber = self.request.GET.get(self.pageNumber_request_str)
            try:
                qs_p = paginator.page(int(pageNumber))
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                qs_p = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                qs_p = paginator.page(paginator.num_pages)
            return qs_p

    def filter_queryset(self, request, *args, **kwargs):
        self.get_queryset(request)
        if self.request.GET.get('items'):
            self.queryset = self.queryset.filter(pk__in=self.request.GET.get('items').split(','))
        else:
            self.filter_data(request)
            self.search_data(request)

    # override this method to include extra non-model objects properties
    def get_extra_fields(qs_p):
        return None

    def get_extra_json_content(self):
        return None

    def get_ajax(self, request, extra_fields = None, *args, **kwargs):
        self.filter_queryset(request)
        qs_p = self.get_paginated_data(request)
        objects =  list(qs_p.object_list.values(*list(self.object_properties)))
        # use extra_fields to include non-model object properties
        extra_fields = self.get_extra_fields(qs_p)
        if extra_fields:
            for d1,d2 in zip(objects, extra_fields):
                d1.update(d2)
        json_content = {'count' : len(self.queryset), 'objects' : objects, 'object_edit_tools' : self.object_edit_tools,}
        extra_json_content = self.get_extra_json_content()
        if extra_json_content:
            json_content.update(extra_json_content)
        return self.render_json_response(json_content)

    # a place to resolve actions on items e.g batch delete
    def post_ajax(self, request, *args, **kwargs):
        pass
        #return self.render_json_response(data)


# GET form and POST data to create/update an item (with ajax-based form validation)
class AjaxFormMixin(JSONResponseMixin, AjaxResponseMixin, View):
    '''
    '''
    # OPTIONS:JSONResponseMixin
    #--------------------------------------#
    content_type ="application/json"
    # OPTIONS:AjaxFormMixin
    #--------------------------------------#
    ajax_form = None
    #--------------------------------------#

    def get_ajax(self, request, obj=None, *args, **kwargs):
        if self.kwargs.has_key('pk'):
            obj = get_object_or_404(self.ajax_form._meta.model, pk=self.kwargs['pk'])
        model = self.ajax_form._meta.model._meta.model_name
        scope_prefix = '_'.join([model, 'data'])
        form = self.ajax_form(instance=obj, scope_prefix=scope_prefix, user=request.user)
        # prepare inital data dict to feed ng-model
        form_html = render_crispy_form(form)
        out_data = {'form_html':form_html, 'model':model,}
        if obj:
            initial = json.dumps(form.initial, cls=TrapperDjangoJSONEncoder) #default=lambda x: ''
            out_data.update({'initial':initial,})
        return self.render_json_response(out_data)

    # override this method to include some tests of incoming json data
    def json_in_data_test(self, in_data, request):
        msg = ''
        return msg

    def update_form_fields(self, obj, request, in_data, bound_form):
        return obj

    def post_ajax(self, request, obj=None, *args, **kwargs):
        if self.ajax_form is None:
            raise ImproperlyConfigured(
                "%(cls)s is missing the form. "
                "Define %(cls)s.form." % {"cls": self.__class__.__name__})
        in_data = json.loads(request.body)
        test_msg = self.json_in_data_test(in_data, request)
        if test_msg:
            return HttpResponseBadRequest(json.dumps({'msg': test_msg}), mimetype="application/json")
        model = self.ajax_form._meta.model._meta.model_name
        scope_prefix = '_'.join([model, 'data'])
        if self.kwargs.has_key('pk'):
            obj = get_object_or_404(self.ajax_form._meta.model, pk=self.kwargs['pk'])
        bound_form = self.ajax_form(data=in_data, instance=obj, scope_prefix=scope_prefix, user=request.user)
        bound_form.full_clean()
        if bound_form.is_valid():
            instance = bound_form.save(commit=False)
            instance = self.update_form_fields(instance, request, in_data, bound_form)
            instance.save()
            form_html = render_crispy_form(bound_form)
            if obj:
                msg = '%s successfully updated!' % model.capitalize()
            else:
                msg = '%s successfully created!' % model.capitalize()
            return HttpResponse(json.dumps({'msg': msg, 'form_html': form_html,}), mimetype="application/json")
        else:
            form_html = render_crispy_form(bound_form)
            msg = 'Invalid form: please correct the errors below:'
            return HttpResponseBadRequest(json.dumps({'msg': msg, 'form_html': form_html}), mimetype="application/json")

