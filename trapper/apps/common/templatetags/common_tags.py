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

from django import template

register = template.Library()

class RenderPaginationMenuNode(template.Node):
	"""
	Renders the pagination menu

	USAGE:
		{% load common_tags %}
		{% pagination_menu page_obj 3 url_prefix_var %}

		only first argument is mandatory:
		{% pagination_menu page_obj %}
	
		where
		* page_obj - pagination object
		* 3 (optional) - number of extra items displayed before and after current page
		* url_prefix_var (optional) - variable holding extra GET parameters string for appending to each pagination link (e.g. list filtering params)
	"""

	def __init__(self, page_obj, num_extra="2", a_href_prefix=None, render_fastforward=True, render_prevnext=True):
		self.page_obj = template.Variable(page_obj)
		self.num_extra = int(num_extra)
		self.render_fastforward = render_fastforward
		self.render_prevnext = render_prevnext
		if a_href_prefix:
			self.a_href_prefix = template.Variable(a_href_prefix)
		else:
			self.a_href_prefix = None

	def get_items(self):
		current_page = self.page_obj_val.number
		num_pages = self.page_obj_val.paginator.num_pages
		
		dots_pre = (current_page - self.num_extra > 1)
		dots_post = (current_page + self.num_extra < num_pages)

		items_pre = range(max(current_page - self.num_extra, 1), current_page)
		items_post = range(current_page + 1, min(num_pages, current_page + self.num_extra) + 1)

		return dots_pre, items_pre, items_post, dots_post

	def render(self, context):
		self.page_obj_val = self.page_obj.resolve(context)
		if self.a_href_prefix:
			self.extra_get_url_val = self.a_href_prefix.resolve(context)
		else:
			self.extra_get_url_val = u""

		# Add ampersand if there are some preceeding filter arguments
		if len(self.extra_get_url_val) > 0:
			self.extra_get_url_val += "&"

		dots_pre, items_pre, items_post, dots_post = self.get_items()
		print self.get_items()

		context = template.Context({
			'page_obj': self.page_obj_val,
			'a_href_prefix': self.extra_get_url_val,
			'render_fastforward':self.render_fastforward,
			'render_prevnext':self.render_prevnext,
			'items_pre': items_pre,
			'items_post': items_post,
		})

		if dots_pre:
			context['dots_pre'] = True
		if dots_post:
			context['dots_post'] = True

		tmpl = template.loader.get_template('common/pagination.html')
		return tmpl.render(context)

def pagination_menu(parser, token):
	splitted_token = token.contents.split()[1:]
	if len(splitted_token) < 1:
		raise template.TemplateSyntaxError("%r tag requires at least one argument" % token.contents.split()[0])

	return RenderPaginationMenuNode(*splitted_token)

register.tag('pagination_menu', pagination_menu)
