from io import BytesIO
import mimetypes

from apiclient.discovery import build
from apiclient.http import MediaIoBaseUpload
from dateutil.parser import parse
import django
from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage
import httplib2
from oauth2client.client import SignedJwtAssertionCredentials
import os.path
import requests


DJANGO_VERSION = django.VERSION[:2]

class GoogleDriveStorage(Storage):
    """
    Storage class for Django that interacts with Google Drive as persistent storage.
    This class uses a system account for Google API that create an application drive 
    (the drive is not owned by any Google User, but it is owned by the application declared on 
    Google API console).
    """

    _UNKNOWN_MIMETYPE_ = "application/octet-stream"
    _GOOGLE_DRIVE_FOLDER_MIMETYPE_ = "application/vnd.google-apps.folder"

    def __init__(self, service_email=None, private_key=None, user_email=None):
        """
        Handles credentials and builds the google service.

        :param service_email: String
        :param private_key: Path
        :param user_email: String
        :raise ValueError:
        """
        self._service_email = service_email or settings.GOOGLE_DRIVE_STORAGE_SERVICE_EMAIL
        self._key = private_key or settings.GOOGLE_DRIVE_STORAGE_KEY

        kwargs = {}
        if user_email or settings.GOOGLE_DRIVE_STORAGE_USER_EMAIL:
            self._user_email = kwargs['sub'] = user_email or settings.GOOGLE_DRIVE_STORAGE_USER_EMAIL
        credentials = SignedJwtAssertionCredentials(
            self._service_email,
            self._key,
            scope="https://www.googleapis.com/auth/drive",
            **kwargs
        )
        http = httplib2.Http()
        http = credentials.authorize(http)

        self._drive_service = build('drive', 'v2', http=http)

    if DJANGO_VERSION >= (1, 7):
        def deconstruct(self):
            """
                Handle field serialization to support migration

            """
            name, path, args, kwargs = super(GoogleDriveStorage, self).deconstruct()
            if self._service_email is not None:
                kwargs["service_email"] = self._service_email
            if self._key is not None:
                kwargs["private_key"] = self._key
            if self._user_email is not None:
                kwargs["user_email"] = self._user_email

    def _split_path(self, p):
        """
        Split a complete path in a list of strings

        :param p: Path to be splitted
        :type p: string
        :returns: list - List of strings that composes the path
        """
        p = p[1:] if p[0] == '/' else p
        a, b = os.path.split(p)
        return (self._split_path(a) if len(a) and len(b) else []) + [b]

    def _get_or_create_folder(self, path, parent_id=None):
        """
        Create a folder on Google Drive.
        It creates folders recursively.
        If the folder already exists, it retrieves only the unique identifier.

        :param path: Path that had to be created
        :type path: string
        :param parent_id: Unique identifier for its parent (folder)
        :type parent_id: string
        :returns: dict
        """
        folder_data = self._check_file_exists(path, parent_id)
        if folder_data is None:
            # Folder does not exists, have to create
            split_path = self._split_path(path)
            current_folder_data = None
            for p in split_path:
                meta_data = {
                    'title': p,
                    'mimeType': self._GOOGLE_DRIVE_FOLDER_MIMETYPE_
                }
                if current_folder_data is not None:
                    meta_data['parents'] = [{'id': current_folder_data['id']}]
                else:
                    # This is the first iteration loop so we have to set the parent_id
                    # obtained by the user, if available
                    if parent_id is not None:
                        meta_data['parents'] = [{'id': parent_id}]
                current_folder_data = self._drive_service.files().insert(body=meta_data).execute()
            return current_folder_data
        else:
            return folder_data

    def _check_file_exists(self, filename, parent_id=None):
        """
        Check if a file with specific parameters exists in Google Drive.

        :param filename: File or folder to search
        :type filename: string
        :param parent_id: Unique identifier for its parent (folder)
        :type parent_id: string
        :param mime_type: Mime Type for the file to search
        :type mime_type: string
        :returns: dict containing file / folder data if exists or None if does not exists
        """
        split_filename = self._split_path(filename)
        if len(split_filename) > 1:
            # This is an absolute path with folder inside
            # First check if the first element exists as a folder
            # If so call the method recursively with next portion of path
            # Otherwise the path does not exists hence the file does not exists
            q = u"mimeType = '{0}' and title = '{1}'".format(self._GOOGLE_DRIVE_FOLDER_MIMETYPE_,
                                                             unicode(split_filename[0]))
            if parent_id is not None:
                q = u"{0} and '{1}' in parents".format(q, parent_id)
            max_results = 1000  # Max value admitted from google drive
            folders = self._drive_service.files().list(q=q, maxResults=max_results).execute()
            for folder in folders["items"]:
                if folder["title"] == unicode(split_filename[0]):
                    # Assuming every folder has a single parent
                    return self._check_file_exists(os.path.sep.join(split_filename[1:]), folder["id"])
            return None
        else:
            # This is a file, checking if exists
            q = u"title = '{0}'".format(split_filename[0])
            if parent_id is not None:
                q = u"{0} and '{1}' in parents".format(q, parent_id)
            max_results = 1000  # Max value admitted from google drive
            file_list = self._drive_service.files().list(q=q, maxResults=max_results).execute()
            if len(file_list["items"]) == 0:
                q = u"" if parent_id is None else u"'{0}' in parents".format(parent_id)
                file_list = self._drive_service.files().list(q=q, maxResults=max_results).execute()
                for element in file_list["items"]:
                    if unicode(split_filename[0]) in element["title"]:
                        return element
                return None
            else:
                return file_list["items"][0]

    # Methods that had to be implemented
    # to create a valid storage for Django

    def _open(self, name, mode='rb'):
        file_data = self._check_file_exists(name)
        r = requests.get(file_data['alternateLink'])
        return File(BytesIO(r.content), name)

    def _save(self, name, content):
        folder_path = os.path.sep.join(self._split_path(name)[:-1])
        folder_data = self._get_or_create_folder(folder_path)
        parent_id = None if folder_data is None else folder_data['id']
        # Now we had created (or obtained) folder on GDrive
        # Upload the file
        fd = BytesIO(content.file.read())
        mime_type = mimetypes.guess_type(name)
        if mime_type[0] is None:
            mime_type = self._UNKNOWN_MIMETYPE_
        media_body = MediaIoBaseUpload(fd, mime_type, resumable=True)
        body = {
            'title': name,
            'mimeType': mime_type
        }
        # Set the parent folder.
        if parent_id:
            body['parents'] = [{'id': parent_id}]
        file_data = self._drive_service.files().insert(
            body=body,
            media_body=media_body).execute()

        # Setting up public permission
        public_permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        self._drive_service.permissions().insert(fileId=file_data["id"], body=public_permission).execute()

        return file_data[u'originalFilename']

    def delete(self, name):
        """
        Deletes the specified file from the storage system.
        """
        file_data = self._check_file_exists(name)
        if file_data is not None:
            self._drive_service.files().delete(fileId=file_data['id']).execute()

    def exists(self, name):
        """
        Returns True if a file referenced by the given name already exists in the
        storage system, or False if the name is available for a new file.
        """
        return self._check_file_exists(name) is not None

    def listdir(self, path):
        """
        Lists the contents of the specified path, returning a 2-tuple of lists;
        the first item being directories, the second item being files.
        """
        directories, files = [], []
        if path == "/":
            folder_id = {"id": u"root"}
        else:
            folder_id = self._check_file_exists(path)
        if folder_id:
            file_params = {
                'q': u"'{0}' in parents and mimeType != '{1}'".format(folder_id["id"], self._GOOGLE_DRIVE_FOLDER_MIMETYPE_),
            }
            dir_params = {
                'q': u"'{0}' in parents and mimeType = '{1}'".format(folder_id["id"], self._GOOGLE_DRIVE_FOLDER_MIMETYPE_),
            }
            files_list = self._drive_service.files().list(**file_params).execute()
            dir_list = self._drive_service.files().list(**dir_params).execute()
            for element in files_list["items"]:
                files.append(os.path.join(path, element["title"]))
            for element in dir_list["items"]:
                directories.append(os.path.join(path, element["title"]))
        return directories, files

    def size(self, name):
        """
        Returns the total size, in bytes, of the file specified by name.
        """
        file_data = self._check_file_exists(name)
        if file_data is None:
            return 0
        else:
            return file_data["fileSize"]

    def url(self, name):
        """
        Returns an absolute URL where the file's contents can be accessed
        directly by a Web browser.
        """
        file_data = self._check_file_exists(name)
        if file_data is None:
            return None
        else:
            return file_data["alternateLink"]

    def accessed_time(self, name):
        """
        Returns the last accessed time (as datetime object) of the file
        specified by name.
        """
        return self.modified_time(name)

    def created_time(self, name):
        """
        Returns the creation time (as datetime object) of the file
        specified by name.
        """
        file_data = self._check_file_exists(name)
        if file_data is None:
            return None
        else:
            return parse(file_data['createdDate'])

    def modified_time(self, name):
        """
        Returns the last modified time (as datetime object) of the file
        specified by name.
        """
        file_data = self._check_file_exists(name)
        if file_data is None:
            return None
        else:
            return parse(file_data["modifiedDate"])