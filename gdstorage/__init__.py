from appconf import AppConf

__version__ = '1.0.0'


class GoogleDriveStorageConf(AppConf):

    class Meta:
        prefix = 'GOOGLE_DRIVE_STORAGE'
        required = ['KEY_PATH']

    USER_EMAIL = None
