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

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase

class UserTestsViews(TestCase):

	def anonymous_menu(self, response):
		self.assertNotContains(response, "My resources")
		self.assertNotContains(response, "Add resource")
		self.assertNotContains(response, "My collections")
		self.assertNotContains(response, "Add collection")
		self.assertNotContains(response, "Messaging")

	def logged_in_menu(self, response):
		self.assertContains(response, "My resources")
		self.assertContains(response, "Add resource")
		self.assertContains(response, "My collections")
		self.assertContains(response, "Add collection")
		self.assertContains(response, "Messaging")

	def staff_menu(self, response):
		self.assertContains(response, "Admin Site")

	def setUp(self):
		User.objects.create_user('user1', 'user1@trapper.com', 'user1')
		staff = User.objects.create_user('staff1', 'staff1@trapper.com', 'staff1')
		staff.is_staff=True;
		staff.save()

	def test_index_anonymous(self):
		response = self.client.get(reverse('index'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Welcome to Trapper!")
		self.anonymous_menu(response)

	def test_index_logged_in(self):
		self.client.login(username='user1', password='user1')
		response = self.client.get(reverse('index'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Welcome to Trapper!")
		self.logged_in_menu(response)

	def test_index_staff(self):
		self.client.login(username='staff1', password='staff1')
		response = self.client.get(reverse('index'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Welcome to Trapper!")
		self.logged_in_menu(response)
		self.staff_menu(response)
