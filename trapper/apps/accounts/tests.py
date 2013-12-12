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
