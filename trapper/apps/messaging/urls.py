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

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from trapper.apps.messaging import views

urlpatterns = patterns('',
	url(r'^$', TemplateView.as_view(template_name="messaging/index.html"), name='index'),
	url(r'message/detail/(?P<pk>\d+)/$', views.MessageDetailView.as_view(), name='message_detail'),
	url(r'message/inbox/$', views.MessageInboxView.as_view(), name='message_inbox'),
	url(r'message/outbox/$', views.MessageOutboxView.as_view(), name='message_outbox'),
	url(r'message/create/$', views.MessageCreateView.as_view(), name='message_create'),
	url(r'notification/list/$', views.SystemNotificationListView.as_view(), name='notification_list'),
	url(r'notification/resolve/(?P<pk>\d+)/$', views.ResolveClassificaionResourceRequestView.as_view(), name='notification_resolve'),
)
