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
