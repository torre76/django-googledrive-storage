from appconf import AppConf

__version__ = '1.0.0'


class GoogleDriveStorageConf(AppConf):
    MEDIA_ROOT = ''

    class Meta:
        prefix = 'GOOGLE_DRIVE_STORAGE'
        required = ['JSON_KEY_FILE']

    USER_EMAIL = None
