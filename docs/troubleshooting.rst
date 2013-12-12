############################################
Troubleshooting
############################################

This section will cover some of the problems that you might encounter when trying to setup Trapper for the first time.
We rely on many external libraries, and there's no way we could cover the step-by-step installation on every possible system and configuration.

Below you will find a list of problems:

**************************************
Cannot determine PostGIS version
**************************************

.. warning::

    django.core.exceptions.ImproperlyConfigured: Cannot determine PostGIS version for database "trapper_db". GeoDjango requires at least PostGIS version 1.3. Was the database created from a spatial database template?

There may be two problems here:

1. You did not install the PostGIS extension on the database
2. Your PostGIS version is neither 1.3, 1.4, 1.5 or 2.0

Let us check whether you have PostGIS installed. Execute these commands:

.. code-block:: none

    su - postgres
    psql trapper_db
    trapper_db=# select postgis_lib_version();

1. If the output is an error, you have not installed the PostGIS extension on your database.
2. If the output is silent (e.g. no output), you might have a PostGIS 2.1 or newer which is not recognized properly by GeoDjango.

In order to resolve that, you can edit the Trapper's ``settings.py`` file and add the following:

``POSTGIS_VERSION = (2, 1, 0)``, where the tuple ``(2, 1, 0)`` will be your version of PostGIS.

******************************************************
OperationalError: FATAL: Peer authentication failed
******************************************************

.. warning::

    OperationalError: FATAL:  Peer authentication failed for user "trapper"

This error means that user ``trapper`` cannot access the database.

Find the following line in the file ``/etc/postgresql/9.1/main/pg_hba.conf``:

.. code-block:: none

    # "local" is for Unix domain socket connections only
    local        all         all             peer

and change the last item, ``peer``, to ``md5``.

.. code-block:: none

    # "local" is for Unix domain socket connections only
    local        all         all             md5

Restart the postgresql server as root:

.. code-block:: none

    sudo /etc/init.d/postgresql restart
