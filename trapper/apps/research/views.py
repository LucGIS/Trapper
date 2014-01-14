from django.shortcuts import render
from braces.views import LoginRequiredMixin
from django.views import generic
from django.http import HttpResponseRedirect

from extra_views import InlineFormSet, CreateWithInlinesView, UpdateWithInlinesView, NamedFormsetsMixin

from trapper.apps.research.models import Project, ProjectRole
from trapper.apps.research.forms import ProjectForm, ProjectRoleFormset
from trapper.apps.common.decorators import object_access_required, ObjectAccessRequiredMixin

class ProjectListView(generic.ListView):
	"""List view of the Project model"""

	model = Project
	context_object_name = 'items'
	template_name = 'research/project_list.html'

	def get_queryset(self, *args, **kwargs):
		"""Besides getting the queryset, determines the permissions for request.user.

		:return: a list of tuples, each containing the following: (:class:`.Project`, user_can_view, user_can_edit)
		:rtype: list
		"""

		projects = super(ProjectListView, self).get_queryset(*args, **kwargs)
		user = self.request.user
		items = []
		for p in projects:
			roles = p.determine_roles(user) if user.is_authenticated() else []
			items.append((p, len(roles) > 0, ProjectRole.ROLE_PROJECT_ADMIN in roles))
		return items

class ProjectDetailView(LoginRequiredMixin, ObjectAccessRequiredMixin, generic.DetailView):
	"""Detail view for the Project model"""

	model = Project
        access_func = Project.can_detail

	def dispatch(self, *args, **kwargs):
		return super(ProjectDetailView, self).dispatch(*args, **kwargs)

# TODO: Class below belongs to forms.py
class ProjectRoleInline(InlineFormSet):
	"""Utility-class: ProjectRoles displayed as a InlineFormset"""

	model = ProjectRole
	extra = 2

class ProjectCreateView(CreateWithInlinesView, NamedFormsetsMixin):
	"""Create view for the Project model"""

	model = Project
	form_class = ProjectForm
	template_name = 'research/project_create.html'
	inlines = [ProjectRoleInline,]
	inlines_names = ['projectrole_formset', ]

	def forms_valid(self, form, inlines):
		"""Saves the formsets and redirects to Project's detail page."""

		self.object = form.save(commit=False)
		self.object.save()
		projectrole_formset = inlines[0]
		projectrole_formset.save()
		return HttpResponseRedirect(self.object.get_absolute_url())

class ProjectUpdateView(UpdateWithInlinesView, NamedFormsetsMixin):
	"""Create view for the Project model"""

	model = Project
	form_class = ProjectForm
	template_name = 'research/project_create.html'
	inlines = [ProjectRoleInline,]
	inlines_names = ['projectrole_formset', ]

	def forms_valid(self, form, inlines):
		"""Saves the formsets and redirects to Project's detail page."""

		self.object = form.save(commit=False)
		self.object.save()
		projectrole_formset = inlines[0]
		projectrole_formset.save()
		return HttpResponseRedirect(self.object.get_absolute_url())

