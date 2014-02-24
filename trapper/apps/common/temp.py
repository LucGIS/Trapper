class ResourceListView2( JSONResponseMixin, generic.ListView):
	"""Displays the list of :class:`.Resource` objects.

	This view employs the filtering features.
	For that reason, the :py:meth:`django.views.generic.ListView.get_queryset` was overloaded.
	The method filters the standard result according to the passed GET parameters.
	"""

	model = Resource
	#context_object_name = 'resources'
	#paginate_by = 3
	template_name = "storage/resource_list.html"


        def get_queryset(self, *args, **kwargs):
                pass

        def __get_queryset(self, *args, **kwargs):
                """Get the queryset filtered by the GET parameters (see :class:`.ResourceFilter`)."""
                if not self.request.user.is_authenticated():
                        qs = Resource.objects.filter(is_public=True)
                elif self.kwargs.has_key('user_pk'):
                        #if not self.request.user.is_authenticated():
                         #       raise PermissionDenied
                        user = User.objects.get(pk=self.kwargs['user_pk'])
                        # get all user's 'viewable' items
                        qs_view = get_objects_for_user(user, ["view_resource_SNG", "view_resource_PRO"], klass=Resource, any_perm=True)
                        # get all user's 'editable' items
                        qs_edit = Resource.objects.filter(Q(owner=user) | Q(uploader=user) | Q(managers=user))
                        # combine both querysets
                        qs = qs_view | qs_edit
                else:
                        qs = Resource.objects.all()

                filtered_queryset = ResourceFilter(self.request.GET, queryset=qs)
                return filtered_queryset.qs         

        # feed angularjs ng-grid with json response 
        def get_data(self):
                #print self.request.GET, self.args, self.kwargs
                qs = self.__get_queryset()
                search = self.request.GET.get('search')
                if search:
                        qs = qs.filter(name__icontains=search)
                pageSize = self.request.GET.get('pageSize')
                if pageSize:
                        paginator = Paginator(qs, pageSize)
                        pageNumber = self.request.GET.get('pageNumber')
                        try:
                                qs_p = paginator.page(int(pageNumber))
                        except PageNotAnInteger:
                                # If page is not an integer, deliver first page.
                                qs_p = paginator.page(1)
                        except EmptyPage:
                                # If page is out of range (e.g. 9999), deliver last page of results.
                                qs_p = paginator.page(paginator.num_pages)
                        data =  list(qs_p.object_list.values('pk', 'name', 'resource_type', 'owner__username', 'is_public',))
                        thumbs = []
                        for q in qs_p:
                                try:
                                        thumbs.append({'thumbnail_large': q.file['video'].url, 'thumbnail_default': q.file['default'].url})
                                except:
                                        thumbs.append({'thumbnail_large': '/static/img/no_thumb_100x100.jpg', 'thumbnail_default': '/static/img/no_thumb_100x100.jpg'})
                        for d1,d2 in zip(data, thumbs):
                                d1.update(d2)
                        data.append(len(qs))
                else:
                        data = list(qs.values('pk', 'name', 'resource_type', 'owner__username', 'is_public',))
                return data
        
        def get_context_data(self, *args, **kwargs):
		context = super(ResourceListView, self).get_context_data(*args, **kwargs)
                context['filtering_form'] = ResourceFilter(self.request.GET).form
                request_params = self.request.GET.copy()
                if 'page' in request_params:
                        del request_params['page']
                context['previous_filter_params'] = request_params.urlencode()
                collection_form = CollectionCreateForm(scope_prefix = 'collection_data')
                context.update({'collection_form': collection_form})
                return context
