############################################################################
#   Copyright (c) 2013  Trapper development team                           #
#                                                                          #
#   This file is a part of Trapper.                                        #
#                                                                          #
#   This program is free software; you can redistribute it and/or modify   #
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

from django.core.urlresolvers import reverse
from django.test import TestCase

from trapper.scripts.db_basic import init as init_basic
from trapper.scripts.db_test import init as init_test


class ProjectViewsTestDBTest(TestCase):

	def setUp(self):
		init_basic()
		init_test()

	def test_project_list_anon(self):
		response = self.client.get(reverse('media_classification:project_list'))
		self.assertEqual(response.status_code, 200)

	def test_project_detail_anon(self):
		response = self.client.get(reverse('media_classification:project_detail', kwargs={'pk': 1}))
		self.assertEqual(response.status_code, 302)

	def test_project_detail_forbidden(self):
		self.client.login(username='user1', password='user1')
		response = self.client.get(reverse('media_classification:project_detail', kwargs={'pk': 1}))
		self.assertEqual(response.status_code, 403)
