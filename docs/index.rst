Django Google Drive Storage
===========================

`Django Google Drive Storage <https://github.com/torre76/django-googledrive-storage/>`_
is a `Django Storage <https://docs.djangoproject.com/en/1.7/ref/files/storage/>`_
implementation that uses `Google Drive <https://drive.google.com>`_ as a backend for storing data.

Please take note that with **this implementation you could not save or load data from a user's Drive**.
You can use only a Drive **dedicated to a Google Project**. This means that:

* this storage interacts with Google Drive as a Google Project, not a Google User.
* your project can use Google Drive only through `Google Drive SDK <https://developers.google.com/drive/>`_. Because no user is associated with this Drive, **you cannot use Google Drive User Interface**.
* this storage authenticates with Google using public private keys. See prerequisites_ for how to obtain it.

Having stated that, with this storage you gain a 15GB space hosted on Google Server where you are able to store data
using Django models.

.. _prerequisites:

Prerequisites
*************

To use this storage, you have to:

* `set up a project and application in the Google Developers Console <https://console.developers.google.com/flows/enableapi?apiid=drive>`_
* `obtain the json private key file (OAuth 2.0 for Server to Server Applications) for your Google Project associated with Google Drive service <https://developers.google.com/identity/protocols/OAuth2ServiceAccount>`_

Installation
************

This storage is hosted on `PyPI <https://pypi.python.org/pypi/django-googledrive-storage>`_. It can be easily installed
through *pip*:

.. code-block:: bash

   pip install django-googledrive-storage

Setup
*****

Once installed, there are a few steps to configure the storage:

* add the module *gdstorage* to your installed apps in your `settings.py` file:

.. code-block:: python

   INSTALLED_APPS = (
       ...,
       'django.contrib.staticfiles',
       'gdstorage'
   )

* create a section in your `setting.py` that contains the configuration for this storage:

.. code-block:: python

   #
   # Google Drive Storage Settings
   #

   GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE = '<path to your json private key file>'
   GOOGLE_DRIVE_STORAGE_SERVICE_EMAIL = '<your service mail>'

The `GOOGLE_DRIVE_STORAGE_SERVICE_EMAIL` should be the email Google assigned to your project,
while the `GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE` must be the path to *private json key file* obtained by Google.

.. note::

   **Django Google Drive Storage** is using `Django Appconf <http://django-appconf.readthedocs.org/>`_ to handle
   settings, so you can setup `GOOGLE_DRIVE_STORAGE_KEY` as an environment variable outside the Django app.

   This will increase security to your environment.

   Thanks to `Johannes Hoppe <https://github.com/codingjoe>`_ for his contribution

* instantiate the storage on you `models.py` file before using into the models:

.. code-block:: python

   from gdstorage.storage import GoogleDriveStorage

   # Define Google Drive Storage
   gd_storage = GoogleDriveStorage()

Use
***

Once configured, it can be used as storage space associated with Django:

.. code-block:: python

   class Map(models.Model):
       id = models.AutoField( primary_key=True)
       map_name = models.CharField(max_length=200)
       map_data = models.FileField(upload_to='/maps', storage=gd_storage)

Source and License
******************

Source can be found on `GitHub <https://github.com/torre76/django-googledrive-storage>`_ with its included
`license <https://github.com/torre76/django-googledrive-storage/blob/master/LICENSE.txt>`_.