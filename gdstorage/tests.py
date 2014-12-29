from django.test import TestCase
from gdstorage.storage import GoogleDriveStorage
import os.path
from pprint import pprint


class GoogleDriveStorageTest(TestCase):

    def test_check_root_file_exists(self):
        gds = GoogleDriveStorage()
        file_data = gds._check_file_exists("How to get started with Drive")
        pprint(file_data)
        print "\n\n"
        self.assertIsNotNone(file_data, u"Unable to find file 'How to get started with Drive'")

    def test_check_or_create_folder(self):
        gds = GoogleDriveStorage()
        folder_data = gds._get_or_create_folder("test4/folder")
        pprint(folder_data)
        print "\n\n"
        self.assertIsNotNone(folder_data, u"Unable to find or create folder 'test4/folder")

    def _test_upload_file(self):
        gds = GoogleDriveStorage()
        file_name = u"{0}{1}{2}".format(os.path.dirname(os.path.abspath(__file__)), os.path.sep,
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
        self.assertTrue(len(files) > 0, u"Unable to read directory data")

    def test_open_file(self):
        self._test_list_folder()
        gds = GoogleDriveStorage()
        f = gds.open(u'/test4/gdrive_logo.png', "rb")
        pprint(f)
        pprint(len(f))
        self.assertIsNotNone(f, "Unable to load data from Google Drive")