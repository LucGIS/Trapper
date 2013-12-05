from django.core.urlresolvers import reverse
from django.test import TestCase

from trapper.scripts.db_basic import init as init_basic
from trapper.scripts.db_test import init as init_test


class StorageViewsTestDBTest(TestCase):

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
