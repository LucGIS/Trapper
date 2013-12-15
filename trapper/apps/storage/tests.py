############################################################################
#   Copyright (c) 2013  Trapper development team                           #
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
from django.test import TestCase

from trapper.scripts.db_basic import init as init_basic
from trapper.scripts.db_test import init as init_test


class StorageViewsEmptyDBTest(TestCase):

	def test_resource_list(self):
		response = self.client.get(reverse('storage:resource_list'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No resources available")

	def test_collection_list(self):
		response = self.client.get(reverse('storage:collection_list'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No collections available")


class StorageViewsTestDBTest(TestCase):

	def setUp(self):
		init_basic()
		init_test()

	# Resource tests
	def test_resource_list_anon(self):
		# Anonymous user can see the resource list
		response = self.client.get(reverse('storage:resource_list'))
		self.assertEqual(response.status_code, 200)

	def test_resource_list_user(self):
		# Logged-in user can see the resource list
		self.client.login(username='user1', password='user1')
		response = self.client.get(reverse('storage:resource_list'))
		self.assertEqual(response.status_code, 200)

	def test_resource_create_anon(self):
		# Anonymous user is redirected to login
		response = self.client.get(reverse('storage:resource_create'))
		self.assertEqual(response.status_code, 302)

	def test_resource_create_user(self):
		# Logged-in user can see the resource create
		self.client.login(username='user1', password='user1')
		response = self.client.get(reverse('storage:resource_create'))
		self.assertEqual(response.status_code, 200)

	def test_resource_detail_anon(self):
		# Anonymous user can see the details
		response = self.client.get(reverse('storage:resource_detail', kwargs={'pk': 1}))
		self.assertEqual(response.status_code, 200)

	def test_resource_update_anon(self):
		# Anonymous user cannot see the update view
		response = self.client.get(reverse('storage:resource_update', kwargs={'pk': 1}))
		self.assertEqual(response.status_code, 302)

	def test_resource_update_forbidden(self):
		# Logged-in user cannot update an arbitrary resource
		self.client.login(username='user1', password='user1')
		response = self.client.get(reverse('storage:resource_update', kwargs={'pk': 1}))
		self.assertEqual(response.status_code, 403)

	def test_resource_update_owned(self):
		# Logged-in user can update the resource he owns
		self.client.login(username='user1', password='user1')
		response = self.client.get(reverse('storage:resource_update', kwargs={'pk': 3}))
		self.assertEqual(response.status_code, 200)

	def test_resource_delete_anon(self):
		# Anonymous user cannot delete the resource
		response = self.client.get(reverse('storage:resource_delete', kwargs={'pk': 1}))
		self.assertEqual(response.status_code, 302)

	def test_resource_delete_forbidden(self):
		# Logged-in user cannot update an arbitrary resource
		self.client.login(username='user1', password='user1')
		response = self.client.get(reverse('storage:resource_delete', kwargs={'pk': 1}))
		self.assertEqual(response.status_code, 403)

	def test_resource_delete_owned(self):
		# Logged-in user can update the resource he owns
		self.client.login(username='user1', password='user1')
		response = self.client.get(reverse('storage:resource_delete', kwargs={'pk': 3}))
		self.assertEqual(response.status_code, 200)

	# Collection tests
	def test_collection_list_anon(self):
		# Anonymous user can see the collection list
		response = self.client.get(reverse('storage:collection_list'))
		self.assertEqual(response.status_code, 200)

	def test_collection_list_user(self):
		# Logged-in user can see the collection list
		self.client.login(username='user1', password='user1')
		response = self.client.get(reverse('storage:collection_list'))
		self.assertEqual(response.status_code, 200)

	def test_collection_create_anon(self):
		# Anonymous user can see the collection list
		response = self.client.get(reverse('storage:collection_create'))
		self.assertEqual(response.status_code, 302)

	def test_collection_create_user(self):
		# Logged-in user can see the collection list
		self.client.login(username='user1', password='user1')
		response = self.client.get(reverse('storage:collection_create'))
		self.assertEqual(response.status_code, 200)

	def test_collection_detail_anon(self):
		# Anonymous user can see the details
		response = self.client.get(reverse('storage:collection_detail', kwargs={'pk': 1}))
		self.assertEqual(response.status_code, 200)

	def test_collection_update_anon(self):
		# Anonymous user cannot see the update view
		response = self.client.get(reverse('storage:collection_update', kwargs={'pk': 1}))
		self.assertEqual(response.status_code, 302)

	def test_collection_update_forbidden(self):
		# Logged-in user cannot update an arbitrary collection
		self.client.login(username='user1', password='user1')
		response = self.client.get(reverse('storage:collection_update', kwargs={'pk': 2}))
		self.assertEqual(response.status_code, 403)

	def test_collection_update_owned(self):
		# Logged-in user can update the collection he owns
		self.client.login(username='user1', password='user1')
		response = self.client.get(reverse('storage:collection_update', kwargs={'pk': 1}))
		self.assertEqual(response.status_code, 200)

	def test_collection_delete_anon(self):
		# Anonymous user cannot delete the collection
		response = self.client.get(reverse('storage:collection_delete', kwargs={'pk': 1}))
		self.assertEqual(response.status_code, 302)

	def test_collection_delete_forbidden(self):
		# Logged-in user cannot update an arbitrary collection
		self.client.login(username='user1', password='user1')
		response = self.client.get(reverse('storage:collection_delete', kwargs={'pk': 2}))
		self.assertEqual(response.status_code, 403)

	def test_collection_delete_owned(self):
		# Logged-in user can update the collection he owns
		self.client.login(username='user1', password='user1')
		response = self.client.get(reverse('storage:collection_delete', kwargs={'pk': 1}))
		self.assertEqual(response.status_code, 200)

	def test_collection_request_anon(self):
		# Anonymous user cannot delete the collection
		response = self.client.get(reverse('storage:collection_request', kwargs={'pk': 1}))
		self.assertEqual(response.status_code, 302)

	def test_collection_request_logged_in(self):
		# Logged-in user cannot update an arbitrary collection
		self.client.login(username='user1', password='user1')
		response = self.client.get(reverse('storage:collection_request', kwargs={'pk': 1}))
		self.assertEqual(response.status_code, 200)
