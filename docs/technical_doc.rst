###############################
Technical documentation
###############################

This section contains a more detailed documentation for the Trapper project.

********
Overview
********

Trapper was developed with a flexible architecture in mind.
For that reason it was separated into few django applications which establish some layers or encapsulation.
As of yet, there exist few core trapper applications, which often communicate between each other:

* Accounts (:ref:`trapper.apps.accounts`)
* Storage (:ref:`trapper.apps.storage`)
* Media classification (:ref:`trapper.apps.media_classification`)
* Messaging (:ref:`trapper.apps.messaging`)
* Geomap (:ref:`trapper.apps.geomap`)
* Common (:ref:`trapper.apps.common`)


*******************************
Django applications
*******************************

This section will cover each application in the project, describing the *Models* (database ORM definition) of each application,
its *Views* (*Controller* in the MVC) as well as the frontend, i.e. *Templates*.
In many cases we will also cover the *Forms* of the application.

.. _trapper.apps.accounts:

accounts
==============================

Accounts module is responsible for extending the :py:class:`django.contrib.auth.models.User` model.
It provides a :class:`trapper.apps.accounts.models.UserProfile` model which extends some basic user functionality.

models
-------------------------------------

.. automodule:: trapper.apps.accounts.models
    :members:

views
-------------------------------------

.. automodule:: trapper.apps.accounts.views
    :members:

forms
-------------------------------------

.. automodule:: trapper.apps.accounts.forms
    :members:


.. _trapper.apps.storage:

storage
==============================

Purpose of storage module is uploading and storing various media resources.
In most cases this will be video files, images or audio files, but any type of file can be uploaded and stored.
It is often used by other applications (e.g. :mod:`trapper.apps.media_classification`) to display media resources.

models
-------------------------------------

.. automodule:: trapper.apps.storage.models
    :members:

views
-------------------------------------

.. automodule:: trapper.apps.storage.views
    :members:

forms
-------------------------------------

.. automodule:: trapper.apps.storage.forms
    :members:


.. _trapper.apps.media_classification:

media_classification
========================================

Media classification module is at the moment one of the core features of Trapper.
This module allows for the classification of media resources (:ref:`trapper.apps.storage`) within the context defined in :class:`trapper.apps.media_classification.models.Project` objects.

.. note::

    It is worth noting how the classification is handled in the backend:
    Single ``Classification`` is split into
    rows, each containing an indentical set of features. Each ``ClassificationRow`` is again split into a set of *states* of the Feature model, namely an instance of model ``FeatureAnswer``

    See models for more details:

    * :class:`trapper.apps.media_classification.models.Classification`
    * :class:`trapper.apps.media_classification.models.ClassificationRow`
    * :class:`trapper.apps.media_classification.models.FeatureAnswer`

models
-----------------------------------------------

.. automodule:: trapper.apps.media_classification.models
    :members:

views
-----------------------------------------------

.. automodule:: trapper.apps.media_classification.views
    :members:

forms
-----------------------------------------------

.. automodule:: trapper.apps.media_classification.forms
    :members:

decorators
-----------------------------------------------

.. automodule:: trapper.apps.media_classification.decorators
    :members:


.. _trapper.apps.messaging:

messaging
========================================

Module :ref:`trapper.apps.messaging` serves as a simple notification system as well as an internal *e-mail* functionality between the users.

models
-----------------------------------------------

.. automodule:: trapper.apps.messaging.models
    :members:

views
-----------------------------------------------

.. automodule:: trapper.apps.messaging.views
    :members:

forms
-----------------------------------------------

.. automodule:: trapper.apps.messaging.forms
    :members:

.. _trapper.apps.geomap:

geomap
========================================

Module :ref:`trapper.apps.geomap` uses geospatial information about resources stored by :ref:`trapper.apps.storage` to present it on the map.

models
-----------------------------------------------

.. automodule:: trapper.apps.geomap.models
    :members:

views
-----------------------------------------------

.. automodule:: trapper.apps.geomap.views
    :members:

forms
-----------------------------------------------

.. automodule:: trapper.apps.geomap.forms
    :members:

.. _trapper.apps.common:

common
========================================

Module :ref:`trapper.apps.common` servers as a place for a general-purpose functions or decorators, not associated with
any of the applications above.

decorators
-----------------------------------------------

.. automodule:: trapper.apps.common.decorators
    :members:

