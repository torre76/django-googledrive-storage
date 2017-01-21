from __future__ import unicode_literals

import os
import os.path
import time
from pprint import pprint

from django.test import TestCase
from gdstorage.storage import GoogleDriveStorage, GoogleDrivePermissionType, GoogleDrivePermissionRole, \
    GoogleDriveFilePermission


class GoogleDriveStorageTest(TestCase):
    def test_check_root_file_exists(self):
        gds = GoogleDriveStorage()
        file_data = gds._check_file_exists("How to get started with Drive")
        pprint(file_data)
        self.assertIsNotNone(file_data, "Unable to find file 'How to get started with Drive'")
        time.sleep(10)

    def test_check_or_create_folder(self):
        gds = GoogleDriveStorage()
        folder_data = gds._get_or_create_folder("test4/folder")
        pprint(folder_data)
        self.assertIsNotNone(folder_data, "Unable to find or create folder 'test4/folder")
        time.sleep(10)

    def _test_upload_file(self):
        gds = GoogleDriveStorage()
        file_name = "{0}{1}{2}".format(os.path.dirname(os.path.abspath(__file__)), os.path.sep,
                                       "../test/gdrive_logo.png")
        result = gds.save("/test4/gdrive_logo.png", open(file_name, 'rb'))
        pprint(result)
        self.assertIsNotNone(result, u'Unable to upload file to Google Drive')

    def _test_list_folder(self):
        self._test_upload_file()
        gds = GoogleDriveStorage()
        (directories, files) = gds.listdir("/test4")
        pprint(directories)
        pprint(files)
        self.assertTrue(len(files) > 0, "Unable to read directory data")

    def _test_open_file(self):
        self._test_list_folder()
        gds = GoogleDriveStorage()
        f = gds.open(u'/test4/gdrive_logo.png', "rb")
        pprint(f)
        pprint(len(f))
        self.assertIsNotNone(f, "Unable to load data from Google Drive")

    def test_permission_full_write(self):
        full_write_permission = GoogleDriveFilePermission(GoogleDrivePermissionRole.WRITER,
                                                          GoogleDrivePermissionType.ANYONE)
        gds = GoogleDriveStorage(permissions=(full_write_permission,))
        file_name = "{0}{1}{2}".format(os.path.dirname(os.path.abspath(__file__)), os.path.sep,
                                       "../test/gdrive_logo.png")
        result = gds.save("/test4/gdrive_logo.png", open(file_name, 'rb'))
        pprint(result)
        self.assertIsNotNone(result, u'Unable to upload file to Google Drive')
        f = gds.open(result, "rb")
        pprint(f)
        pprint(len(f))
        self.assertIsNotNone(f, "Unable to load data from Google Drive")
        time.sleep(10)

    def test_multiple_permission(self):
        full_write_to_foo = GoogleDriveFilePermission(GoogleDrivePermissionRole.WRITER,
                                                      GoogleDrivePermissionType.USER,
                                                      "foo@mailinator.com")
        read_only_to_anyone = GoogleDriveFilePermission(GoogleDrivePermissionRole.READER,
                                                        GoogleDrivePermissionType.ANYONE)
        gds = GoogleDriveStorage(permissions=(full_write_to_foo, read_only_to_anyone,))
        file_name = "{0}{1}{2}".format(os.path.dirname(os.path.abspath(__file__)), os.path.sep,
                                       "../test/gdrive_logo.png")
        result = gds.save("/test4/gdrive_logo.png", open(file_name, 'rb'))
        pprint(result)
        self.assertIsNotNone(result, u'Unable to upload file to Google Drive')
        f = gds.open(result, "rb")
        pprint(f)
        pprint(len(f))
        self.assertIsNotNone(f, "Unable to load data from Google Drive")
        time.sleep(10)

    def test_upload_big_file(self):
        gds = GoogleDriveStorage()
        file_name = "{0}{1}{2}".format(os.path.dirname(os.path.abspath(__file__)), os.path.sep,
                                       "../test/huge_file")
        with open(file_name, "wb") as out:
            out.truncate(1024 * 1024 * 20)

        result = gds.save("/test5/huge_file", open(file_name, 'rb'))
        pprint(result)
        self.assertIsNotNone(result, u'Unable to upload file to Google Drive')

        os.remove(file_name)

        time.sleep(10)

    def test_open_big_file(self):
        self._test_list_folder()
        gds = GoogleDriveStorage()
        f = gds.open(u'/test5/huge_file', "rb")
        pprint(f)
        pprint(len(f))
        self.assertIsNotNone(f, "Unable to load data from Google Drive")
        time.sleep(10)

