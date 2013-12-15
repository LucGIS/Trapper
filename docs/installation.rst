##############################################
Installation guide
##############################################

The project is developed using:

* Python 2.7.x
* Django 1.6

System requirements:

* `virtualenv <http://www.virtualenv.org>`_
* `RabbitMQ server <http://www.rabbitmq.com/>`_
* PostgreSQL 9.1 (tested on version 9.1.9)
* Geospatial libraries: GEOS and PROJ.4
* PostGIS (preferably 2.0.x)

******************************
System requirements
******************************

Let us start with the installation of the system dependencies.
Django and other python requirements will be installed locally inside the project using virtualenv.

.. warning::
    This guide will cover the installation on the Ubuntu/Debian systems.
    For other systems, please use the recommended methods of package installation.

Command below will install virtualenv, postgresql, geospatial libraries, PostGIS and rabbitmq-server:

.. code-block:: none

    user@home:~$ sudo apt-get install python-virtualenv postgresql-9.1 binutils
    libproj-dev gdal-bin postgresql-server-dev-9.1
    rabbitmq-server libavcodec-dev libavformat-dev libswscale-dev libjpeg-dev python-dev

Before installing postgis, check which version is available at your system:

.. code-block:: none

    user@home:~$ sudo apt-get install -s postgresql-9.1-postgis | grep postgis

It may be the case that your version is 1.5.x or lower.

You can either install the available version same as before:

.. code-block:: none

    user@home:~$ sudo apt-get install postgresql-9.1-postgis

Or you could try to find the way to obtain PostGIS 2.x for your system:

.. seealso::

    * `Adding UbuntuGIS (contains PostGIS 2.0) <http://trac.osgeo.org/ubuntugis/wiki/UbuntuGISRepository>`_
    * `PostGIS 2.1 on Debian Wheezy <http://blog.light42.com/wordpress/?p=1540>`_

.. note:

    It is recommended to use PostGIS 2.x as it simplifies the setup process.

.. seealso::

    * `Installing geospatial libraries <https://docs.djangoproject.com/en/1.6/ref/contrib/gis/install/geolibs/>`_
    * `Installing PostGIS <https://docs.djangoproject.com/en/1.6/ref/contrib/gis/install/postgis/>`_

*******************************
Preparing PostgreSQL database
*******************************

In this section we will prepare the database for handling the geospatial data, as well as setup some basic user privileges.
Before we downloading Trapper perform the following actions in a console:

Now we will create a new postgresql user named *trapper*.

.. code-block:: none

    user@home:~$ adduser trapper
    (use unix defaults here)
    user@home:~$ su - postgres
    postgres@home:~$ psql
    postgres=# CREATE USER trapper WITH PASSWORD 'trapper';
    CREATE ROLE
    postgres=# \q

Snipplet above does the following:

1. Creates a new unix user called *trapper*
2. Switches to *postgres* user
3. Runs *psql* command-line interface and connects to a *template1* database
4. Creates the postgresql user *trapper*
5. ``\q`` exists the psql

.. seealso::

    * `Adding postgresql user accounts <http://www.cyberciti.biz/faq/howto-add-postgresql-user-account/>`_

.. note::

    In production code you will most likely want to create a user with a more sophisticated password (don't forget to update the ``trapper/settings.py`` accordingly).

.. note::

    In order to run trapper's automated unit tests user might need some additional privileges for creating databases. In order to resolve that without assigning him superuser provileges, see `Obtaining sufficient privileges <https://docs.djangoproject.com/en/dev/ref/contrib/gis/testing/#obtaining-sufficient-privileges>`_ section of the Django documentation.

Now we will create a database and set up the postgis extension on it:

.. code-block:: none

    user@home:~$ su - postgres
    postgres@home:~$ psql
    postgres=# CREATE DATABASE trapper_db OWNER trapper;
    CREATE DATABASE
    postgres=# GRANT ALL PRIVILEGES ON DATABASE trapper_db TO trapper;
    GRANT
    postgres=# \c trapper_db
    You are now connected to database "trapper_db" as user "postgres"
    trapper_db=# CREATE EXTENSION postgis;
    CREATE EXTENSION
    trapper_db=# \q

Snipplet above does the following:

1. Switches to a *postgres* user
2. Runs *psql* command-line interface and connects to a *template1* database
3. Creates the database named *trapper_db* and makes *trapper* its owner
4. Connects to the newly created database
5. installs the postgis extension (required for the geospatial features of Trapper)
6. ``\q`` exists the psql


.. warning::
    Creating the postgis extension (last step of the snipplet above) is a little bit more involved with PostGIS 1.x.
    For more details on how to set up a PostGIS 1.x database please refer to:

    * `Setting up PostGIS 1.x (Django documentation) <https://docs.djangoproject.com/en/1.6/ref/contrib/gis/install/postgis/#creating-a-spatial-database-template-for-earlier-versions>`_


************************************
Preparing the project
************************************

Next step is cloning the repository and installing python the requirements.

.. code-block:: none

    user@home:~$ git clone https://github.com/TrapperTeam/Trapper
    user@home:~$ cd Trapper/
    user@home:~$ virtualenv env
    user@home:~$ ./env/bin/pip install -r requirements.txt

************************************
Running Trapper
************************************

The project is now set up and ready to use.
Initialize the database along with the test data and run the server:

.. code-block:: none

    user@home:~$ ./setup_database.sh
    user@home:~$ ./run_server.sh

Additionally, execute a celery worker in a separate shell:

.. code-block:: none

    user@home:~$ ./run_celery.sh

************************************
Extra: Generating this documentation
************************************

Since Trapper is developed using virtualenv, it may be difficult to generate this documentation
using sphinx-build that's installed system-wide. In order to resolve that simply perform the following steps:

.. note::
    ``$TRAPPER_ROOT`` is the path the Trapper on your system, e.g. ``/home/user/MyProjects/Trapper/``

.. code-block:: none

    user@home:~$ cd $TRAPPER_ROOT
    user@home:~$ which sphinx-build
    /usr/bin/sphinx-build (or other system path)
    user@home:~$ source ./env/bin/activate
    user@home:~$ which sphinx-build
    $TRAPPER_ROOT/env/bin/sphinx-build

After that you should be able to generate this document without problems:

.. code-block:: none

    user@home:~$ cd $TRAPPER_ROOT/docs/
    user@home:~$ make html

After that, this website will reside in ``$TRAPPER_ROOT/docs/_build`` directory.
