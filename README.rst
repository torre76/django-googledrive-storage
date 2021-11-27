===========================
Django Google Drive Storage
===========================

|build-status| |lint| |pypi| |docs|

This is a `Django Storage <https://docs.djangoproject.com/en/dev/ref/files/storage/>`_ implementation that uses `Google Drive <https://drive.google.com>`_ as backend for storing data.

Quick start
-----------

Installation
************

.. code-block:: bash

   pip install django-googledrive-storage


Setup
*****

.. code-block:: python

   INSTALLED_APPS = (
        ...,
        'django.contrib.staticfiles',
        'gdstorage'
    )

Set the environment variable `GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE_CONTENTS` or path file in the `settings.py`: `GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE`. 

Optional set `GOOGLE_DRIVE_STORAGE_MEDIA_ROOT` in the `settings.py`

Usage example
*************

.. code-block:: python

    from gdstorage.storage import GoogleDriveStorage

    # Define Google Drive Storage
    gd_storage = GoogleDriveStorage()

    ...

    class Map(models.Model):
        id = models.AutoField( primary_key=True)
        map_name = models.CharField(max_length=200)
        map_data = models.FileField(upload_to='maps', storage=gd_storage)


Documentation and Installation instructions
-------------------------------------------

Documentation and installation instructions can be found at `Read The Docs <http://django-googledrive-storage.readthedocs.org/>`_.

.. |build-status| image:: https://github.com/conformist-mw/django-googledrive-storage/workflows/tests/badge.svg
    :target: https://github.com/conformist-mw/django-googledrive-storage/actions/workflows/tests.yml
    :alt: Tests status

.. |lint| image:: https://github.com/conformist-mw/django-googledrive-storage/workflows/lint/badge.svg
    :target: https://github.com/conformist-mw/django-googledrive-storage/actions/workflows/lint.yml
    :alt: Linter status

.. |pypi| image:: https://img.shields.io/pypi/v/django-googledrive-storage.svg
    :target: https://pypi.python.org/pypi/django-googledrive-storage/
    :alt: django-googledrive-storage on Pypi

.. |docs| image:: https://readthedocs.org/projects/django-googledrive-storage/badge/?version=latest
    :target: http://django-googledrive-storage.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status
