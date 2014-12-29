from appconf import AppConf

__version__ = '1.0.0'


class GoogleDriveStorageConf(AppConf):

    class Meta:
        prefix = 'GOOGLE_DRIVE_STORAGE'
        required = ['KEY', 'SERVICE_EMAIL']

    USER_EMAIL = None