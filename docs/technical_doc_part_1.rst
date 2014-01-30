#########################################
Technical documentation: Overview
#########################################

This document will cover a technical documentation for the Trapper project.

*******************************
Introduction
*******************************

Trapper was developed with a flexible architecture in mind.
For that reason it was separated into few django applications which establish some layers of abstraction over common usages.
As of yet, there exist few core trapper applications, which often communicate between each other.

*******************************
Django applications
*******************************

Trapper is composed of several Django applications.
In next section we will cover each application in the project, describing the *Models* (database ORM definition) of each application,
its *Views* (*Controller* in the MVC) as well as the frontend, i.e. *Templates*.
In many cases we will also cover the *Forms* or the *Decorators* of the application.

Core applications of Trapper are following:

* Accounts (:ref:`trapper.apps.accounts`)
* Storage (:ref:`trapper.apps.storage`)
* Media classification (:ref:`trapper.apps.media_classification`)
* Messaging (:ref:`trapper.apps.messaging`)
* Geomap (:ref:`trapper.apps.geomap`)
* Common (:ref:`trapper.apps.common`)

*******************************
Coding style
*******************************

General rules
===============================

* We aim to follow `PEP-8 <http://www.python.org/dev/peps/pep-0008/>`_ coding style guide, although at this stage of development it wasn't as carefully abiden.
* Exception to the rule above is using **tabs** instead of spaces for indentation, and allowing for a line longer than 79 characters.

Strings: single vs double quotes
================================

Use double quotes:

* When the string is a sentence, message or a word: ``"Four Yorkshiremen."``, ``"Shoebox"``

Use single quotes:

* When the string is a regexp: ``r'spam/detail/(?P<pk>\d+)/$'``
* When the string is an identifier, kwarg which is not a sentence or a dict key:

.. code-block:: python

    FRUIT_CHOICES = {
        'A': "Apples",
        'B': "Banana",
    }

    def set_color(color='red'):
        """Sets the color."""

Indentation in templates
===========================

* Python code in templates should be indented up to the current indentation level of the preceeding HTML tag
* Each variable should be separated by one space from the parenthesis, e.g. ``{{ value }}`` and **not** ``{{value}}``

.. code-block:: html

    <table>
    {% for row in table_rows %}
        <tr>
        {% for cell in row.cells %}
            <td>{{ cell }}</td>
        {% endfor %}
        </tr>
    {% endfor %}
    </table>
