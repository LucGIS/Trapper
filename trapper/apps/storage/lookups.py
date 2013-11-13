from ajax_select import LookupChannel
from django.utils.html import escape
from django.db.models import Q
from trapper.apps.storage.models import Resource

class ResourceLookup(LookupChannel):
	model = Resource

	def check_auth(self, request):
		if request.user.is_authenticated():
			return True

	def get_query(self,q,request):
		return Resource.objects.filter(Q(name__icontains=q) | Q(resource_type__name__icontains=q)).order_by('name')

	def get_result(self, obj):
		u""" result is the simple text that is the completion of what the person typed """
		return obj.name

	def format_match(self, obj):
		""" (HTML) formatted item for display in the dropdown """
		return self.format_item_display(obj)

	def format_item_display(self, obj):
		""" (HTML) formatted item for displaying item in the selected deck area """
		return u"%s|%s" % (escape(obj.name), escape(obj.resource_type.name))

#Note that raw strings should always be escaped with the escape() function
