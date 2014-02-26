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
from django.test import TestCase
from django.contrib.auth.models import User

from trapper.apps.media_classification.models import Project, ProjectRole
from trapper.apps.research.models import Project as RProject


class ProjectViewsTestDBTest(TestCase):

    def setUp(self):
        self.rp0 = RProject.objects.create(name="RProject_0")
        self.u0 = User.objects.create_user('user1', 'user@users.com', 'user1')
        self.p0 = Project.objects.create(name="Project_0", research_project=self.rp0)
        self.p1 = Project.objects.create(name="Project_1", research_project=self.rp0)
        self.pr0 = ProjectRole.objects.create(name=ProjectRole.ROLE_PROJECT_ADMIN, user=self.u0, project=self.p0)

    def test_project_list_anon(self):
        """List of projects is publicly available to anonymous users."""

        response = self.client.get(reverse('media_classification:project_list'))
        self.assertEqual(response.status_code, 200)

    def test_project_detail_anon(self):
        """Anonymous users cannot access the details of any project."""

        response = self.client.get(reverse('media_classification:project_detail', kwargs={'pk': self.p1.pk}))
        self.assertEqual(response.status_code, 302)

    def test_project_detail_forbidden(self):
        """Logged-in user accessing a project he does not participate in."""

        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('media_classification:project_detail', kwargs={'pk': self.p1.pk}))
        self.assertEqual(response.status_code, 403)

    def test_project_detail_allowed(self):
        """Logged-in user accessing a project he participates in."""

        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('media_classification:project_detail', kwargs={'pk': self.p0.pk}))
        self.assertEqual(response.status_code, 200)
