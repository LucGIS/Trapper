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

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from trapper.apps.research import views


urlpatterns = patterns('',
	# Home page of research project module
	url(r'^$', TemplateView.as_view(template_name='research/index.html'), name='index'),

	# Display project list and the details about given project
	url(r'project/list/$', views.ProjectListView.as_view(), name='project_list'),
	url(r'project/detail/(?P<pk>\d+)/$', views.ProjectDetailView.as_view(), name='project_detail'),
	url(r'project/create/$', views.ProjectCreateView.as_view(), name='project_create'),
	url(r'project/update/(?P<pk>\d+)/$', views.ProjectUpdateView.as_view(), name='project_update'),
)
