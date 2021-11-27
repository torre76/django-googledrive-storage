import os
import os.path
import time

import pytest

from gdstorage.storage import (GoogleDriveFilePermission,
                               GoogleDrivePermissionRole,
                               GoogleDrivePermissionType, GoogleDriveStorage)

SLEEP_INTERVAL = 10


@pytest.fixture
def gds():
    return GoogleDriveStorage()


@pytest.fixture
def write_perm_gds():
    return GoogleDriveStorage(
        permissions=(GoogleDriveFilePermission(
            GoogleDrivePermissionRole.WRITER,
            GoogleDrivePermissionType.ANYONE,
        ),)
    )


@pytest.fixture
def read_write_perm_gds():
    return GoogleDriveStorage(
        permissions=(
            GoogleDriveFilePermission(
                GoogleDrivePermissionRole.WRITER,
                GoogleDrivePermissionType.USER,
                'foo@mailinator.com',
            ),
            GoogleDriveFilePermission(
                GoogleDrivePermissionRole.READER,
                GoogleDrivePermissionType.ANYONE,
            ),
        )
    )


class TestGoogleDriveStorage:
    def test_check_root_file_exists(self, gds):
        file_data = gds._check_file_exists('How to get started with Drive')
        assert file_data, "Unable to find file 'How to get started with Drive'"
        time.sleep(SLEEP_INTERVAL)

    def test_check_or_create_folder(self, gds):
        folder_data = gds._get_or_create_folder('test4/folder')
        assert folder_data, "Unable to find or create folder 'test4/folder'"
        time.sleep(SLEEP_INTERVAL)

    def _test_upload_file(self, gds):
        file_name = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../test/gdrive_logo.png',
        )
        with open(file_name, 'rb') as file:
            result = gds.save('/test4/gdrive_logo.png', file)
        assert result, 'Unable to upload file to Google Drive'

    def _test_list_folder(self, gds):
        self._test_upload_file(gds)
        directories, files = gds.listdir('/test4')
        assert len(files) > 0, 'Unable to read directory data'

    def _test_open_file(self):
        gds = GoogleDriveStorage()
        self._test_list_folder(gds)
        file = gds.open('/test4/gdrive_logo.png', 'rb')
        assert file, 'Unable to load data from Google Drive'

    def test_permission_full_write(self, write_perm_gds):
        file_name = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../test/gdrive_logo.png',
        )
        with open(file_name, 'rb') as file:
            result = write_perm_gds.save('/test4/gdrive_logo.png', file)
        assert result, 'Unable to upload file to Google Drive'
        file = write_perm_gds.open(result, 'rb')
        assert file, 'Unable to load data from Google Drive'
        time.sleep(SLEEP_INTERVAL)

    def test_multiple_permission(self, read_write_perm_gds):

        file_name = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../test/gdrive_logo.png',
        )
        result = read_write_perm_gds.save(
            '/test4/gdrive_logo.png', open(file_name, 'rb')
        )
        assert result, 'Unable to upload file to Google Drive'
        file = read_write_perm_gds.open(result, 'rb')
        assert file, 'Unable to load data from Google Drive'
        time.sleep(SLEEP_INTERVAL)

    def test_upload_big_file(self, gds):
        file_name = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '../test/huge_file',
        )
        with open(file_name, 'wb') as out:
            out.truncate(1024 * 1024 * 20)

        with open(file_name, 'rb') as file:
            result = gds.save('/test5/huge_file', file)
        assert result, 'Unable to upload file to Google Drive'

        os.remove(file_name)
        time.sleep(SLEEP_INTERVAL)

    def test_open_big_file(self, gds):
        self._test_list_folder(gds)
        file = gds.open('/test5/huge_file', 'rb')
        assert file, 'Unable to load data from Google Drive'
        time.sleep(SLEEP_INTERVAL)
