##############################################
Tutorials
##############################################


These tutorial will cover some of the actions you can perform in Trapper. Trapper allows different features depending on your role and participation in media classification projects. This tutorial page will be roughly divided according to these differences

**********************************************
System roles
**********************************************

Roles in Trapper are hierarchically ordered.
The following roles exist within the Trapper:

* :ref:`role.anonymous`
* :ref:`role.crowdsourcing`
* :ref:`role.expert`
* :ref:`role.staff`

The least privileged type of user is the ``Anonymous`` one.
Each successive role introduces more permissions:

.. note::

    The hierarchy of *privileges* is as follows:

    ``Staff`` > ``Expert`` > ``Crowd-Sourcing`` > ``Anonymous``

    Each role on the **right** of any other role has **less** privileges and features. At the same time, each role on the **left** has all the features and privileges as your role.

    E.g.: if your role in the Trapper is ``Expert``, tutorials for roles ``Crowd-Sourcing`` and ``Anonymous`` will also be relevant you.

.. _role.anonymous:

**********************************************
Anonymous user
**********************************************

Anonymous users of Trapper have a limited functionality.
Namely, they cannot alter Trapper's data in any way nor contribute to any of the ongoing media classification projects.

.. note::

    As an anonymous user you have access to the following modules of Trapper:
    
    * Home page
    * List of publicly available resources, collections and locations
    * List of projects by their name

Possible actions
==============================================

    * List of publicly available resources ``Storage > Resources``
    * List of publicly available collections ``Storage > Collections``
    * List of publicly available locations (displayed on the map) ``Geomap > Show map``
    * You can see a list of project by their names but you can't see the details on any of it ``Media classification > Projects``


.. _role.crowdsourcing:

**********************************************
Crowd-Sourcing user
**********************************************

.. note::

    Once you log-in to Trapper, are recognized as a ``Crowd-Sourcing`` user, navigation bar will display more navigation options, namely:
    
    * Profile view
    * Messaging features
    * Crowd-Sourcing menu under ``Media Classification`` drop-down

Edit Profile
==============================================

Since you are a registered user now, you can edit your user profile, to do so navigate to your profile view (your user name next to a ``Logout`` button on the right).

When you click it, you can see the details about your profile.
Below the table, you should see a button called ``Edit Profile``.
Clicking it will take you to the profile editing view in which you can alter the information about yourself.

Classifying material
==============================================

In order to classify media resource go to navigation bar and select ``Media classification > Classify material``.

At the moment, Trapper lets you pick the crowd-sourcing enabled resources for the classification.
On the newly opened page you will see a list of ongoing media classification projects, and the resources available for the classification.
Once you select given resource, you will see the media file associated with it (usually an image or a video).
Your task is to describe the situation visible on the media according to some ``Features``, e.g. How many animals are visible, and of what kind.

Once you make your decision, you can submit your classification data to the system.

Send and receive messages with other users
==============================================

Registered users have the ability to use Trappers messaging module.

.. note::
    The module itself tries to mimic a standard (but very limited) **e-mail** functionality:
    
    * Each message can be directed towards a single users
    * Each message is composed of a *subject* and a *body*

In order to send a message to another user, navigate to ``Messaging > New Message`` at the main navigation bar.
You will be presented with a simple message form, in which you are to enter the message subject, the message itself, and a recipient.

Additionally to writing new messages, you can browse and read the incoming and outgoing correspondence by navigating to ``Messaging > Inbox`` and ``Messaging > Outbox`` correspondingly.

.. note::

    Unread incoming messages and system notifications are also indicated by the altered icon of the ``Messaging`` menu at the main navigation bar.

.. _role.expert:

**********************************************
Expert user
**********************************************

Expert users are usually researchers operating on the whole collections of resources along with the context and the classification results.
In future iterations of Trapper, this role will have access to many analytical modules, such as generating statistics and modeling patterns of behaviour of animals within the geo-spatial context.

.. note::

    ``Expert`` users can benefit from many more of Trapper's features:
    
    * Create new ``Media Classification`` projects
    * Upload resources, define collections, upload and define locations and request

.. _role.staff:

**********************************************
Trapper staff
**********************************************

Trapper's staff members are usually the system administrators and the core maintainers of the Trapper instance.
They have all the privileges by default, and have an access to *Django*'s admin panel.

.. note::

    Staff users will have an additional ``Admin Site`` button at the main navigation bar which takes them to the Django's admin panel.
