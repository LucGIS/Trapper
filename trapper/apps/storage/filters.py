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

import django_filters
from trapper.apps.storage.models import Resource, Collection
from trapper.apps.storage.forms import ResourceFilterForm

resource_types = [(k) for k in Resource.TYPE_CHOICES]
resource_types.sort()
RESOURCE_TYPE_FILTER_CHOICES = tuple([('','-- All --')]+resource_types)
resource_status = [(k) for k in Resource.STATUS_CHOICES]
RESOURCE_STATUS_FILTER_CHOICES = tuple([('','-- All --')]+resource_status)
#collections = Collection.objects.all().order_by('name')
#COLLECTION_CHOICES = tuple([('','-- All --')]+[(x.id, x.name + " : " + x.owner.username) for x in collections])

class ResourceFilter(django_filters.FilterSet):
    date_uploaded = django_filters.DateRangeFilter(label='Date')
    resource_type= django_filters.ChoiceFilter(choices=RESOURCE_TYPE_FILTER_CHOICES, label='Type')
    status = django_filters.ChoiceFilter(choices=RESOURCE_STATUS_FILTER_CHOICES)
    #collection = django_filters.ChoiceFilter(choices=COLLECTION_CHOICES)

    class Meta:
        model = Resource
        form = ResourceFilterForm
        fields = ['resource_type', 'date_uploaded', 'status']




