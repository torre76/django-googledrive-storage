import os

from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class GoogleDriveStorageConfig(AppConfig):
    name = 'gdstorage'
    verbose_name = 'Google Drive Storage'
    _prefix = 'GOOGLE_DRIVE_STORAGE'

    def ready(self):
        if not hasattr(settings, self._get_attr('JSON_KEY_FILE')):
            if not os.getenv(self._get_attr('JSON_KEY_FILE_CONTENTS')):
                raise ImproperlyConfigured(
                    'Either GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE in settings '
                    'or GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE_CONTENTS '
                    'environment variable should be defined.'
                )
        if not hasattr(settings, self._get_attr('MEDIA_ROOT')):
            setattr(settings, self._get_attr('MEDIA_ROOT'), '')

    def _get_attr(self, suffix):
        return '_'.join([self._prefix, suffix])
