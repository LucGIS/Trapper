from ajax_select import LookupChannel
from django.utils.html import escape
from django.contrib.auth.models import User

class UserLookup(LookupChannel):
	model = User

	def check_auth(self, request):
		if request.user.is_authenticated():
			return True

	def get_query(self, q, request):
		return User.objects.filter(username__icontains=q).order_by('username')

	def get_result(self, obj):
		u""" result is the simple text that is the completion of what the person typed """
		return obj.username

	def format_match(self, obj):
		""" (HTML) formatted item for display in the dropdown """
		return self.format_item_display(obj)

	def format_item_display(self, obj):
		""" (HTML) formatted item for displaying item in the selected deck area """
		return u"%s" % (escape(obj.username))

#Note that raw strings should always be escaped with the escape() function
