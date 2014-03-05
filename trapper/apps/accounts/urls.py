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

from trapper.apps.accounts import views

urlpatterns = patterns(
    '',
    url(r'profile/$', views.SessionUserProfileDetailView.as_view(), name='userprofile_detail'),
    url(r'profile/detail/(?P<pk>\d+)/$', views.UserProfileDetailView.as_view(), name='userprofile_detail'),
    url(r'profile/update/(?P<pk>\d+)/$', views.UserProfileUpdateView.as_view(), name='userprofile_update'),
    url(r'login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'register/$', views.UserRegistrationView.as_view(), name='register'),
    url(r'logout/$', views.logout_action, name='logout'),
)
