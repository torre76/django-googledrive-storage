from appconf import AppConf

__version__ = '1.0.0'


class GoogleDriveStorageConf(AppConf):
    KEY_FILE_PASSWORD = 'notasecret'

    class Meta:
        prefix = 'GOOGLE_DRIVE_STORAGE'
        required = ['KEY_FILE', 'SERVICE_EMAIL']