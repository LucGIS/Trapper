from django.core.urlresolvers import reverse
from django.test import TestCase

class ViewTests(TestCase):
	"""
	Tests validating the proper rendering of the standard views.
	"""

	def test_storage_view(self):
		response = self.client.get(reverse('storage:index'))
		self.assertEqual(response.status_code, 200)

	def test_media_classification_view(self):
		response = self.client.get(reverse('media_classification:index'))
		self.assertEqual(response.status_code, 200)

	def test_messaging_view(self):
		response = self.client.get(reverse('messaging:index'))
		self.assertEqual(response.status_code, 200)
