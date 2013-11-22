from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase

class StorageViewsTests(TestCase):
	"""
	Tests validating the proper rendering of the standard storage pages.
	"""

	def test_storage_no_resources(self):
		response = self.client.get(reverse('storage:resource_list'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No resources available.")

	def test_storage_no_collections(self):
		response = self.client.get(reverse('storage:collection_list'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No collections available.")

