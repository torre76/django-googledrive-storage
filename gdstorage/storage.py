import enum
import json
import mimetypes
import os
from io import BytesIO

from dateutil.parser import parse
from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload


class GoogleDrivePermissionType(enum.Enum):
    """
    Describe a permission type for Google Drive as described on
    `Drive docs <https://developers.google.com/drive/v3/reference/permissions>`_
    """  # noqa: E501

    USER = 'user'  # Permission for single user

    GROUP = 'group'  # Permission for group defined in Google Drive

    DOMAIN = 'domain'  # Permission for domain defined in Google Drive

    ANYONE = 'anyone'  # Permission for anyone


class GoogleDrivePermissionRole(enum.Enum):
    """
    Describe a permission role for Google Drive as described on
    `Drive docs <https://developers.google.com/drive/v3/reference/permissions>`_
    """  # noqa: E501

    OWNER = 'owner'  # File Owner

    READER = 'reader'  # User can read a file

    WRITER = 'writer'  # User can write a file

    COMMENTER = 'commenter'  # User can comment a file


@deconstructible
class GoogleDriveFilePermission(object):
    """
    Describe a permission for Google Drive as described on
    `Drive docs <https://developers.google.com/drive/v3/reference/permissions>`_

    :param gdstorage.GoogleDrivePermissionRole g_role: Role associated to this permission
    :param gdstorage.GoogleDrivePermissionType g_type: Type associated to this permission
    :param str g_value: email address that qualifies the User associated to this permission

    """  # noqa: E501

    @property
    def role(self):
        """
        Role associated to this permission

        :return: Enumeration that states the role associated to this permission
        :rtype: gdstorage.GoogleDrivePermissionRole
        """
        return self._role

    @property
    def type(self):
        """
        Type associated to this permission

        :return: Enumeration that states the role associated to this permission
        :rtype: gdstorage.GoogleDrivePermissionType
        """
        return self._type

    @property
    def value(self):
        """
        Email that qualifies the user associated to this permission
        :return: Email as string
        :rtype: str
        """
        return self._value

    @property
    def raw(self):
        """
        Transform the :class:`.GoogleDriveFilePermission` instance into a
        string used to issue the command to Google Drive API

        :return: Dictionary that states a permission compliant with Google Drive API
        :rtype: dict
        """  # noqa: E501

        result = {
            'role': self.role.value,
            'type': self.type.value
        }

        if self.value is not None:
            result['emailAddress'] = self.value

        return result

    def __init__(self, g_role, g_type, g_value=None):
        """
        Instantiate this class
        """
        if not isinstance(g_role, GoogleDrivePermissionRole):
            raise ValueError(
                'Role should be a GoogleDrivePermissionRole instance'
            )
        if not isinstance(g_type, GoogleDrivePermissionType):
            raise ValueError(
                'Permission should be a GoogleDrivePermissionType instance'
            )
        if g_value is not None and not isinstance(g_value, str):
            raise ValueError('Value should be a String instance')

        self._role = g_role
        self._type = g_type
        self._value = g_value


_ANYONE_CAN_READ_PERMISSION_ = GoogleDriveFilePermission(
    GoogleDrivePermissionRole.READER,
    GoogleDrivePermissionType.ANYONE
)


@deconstructible
class GoogleDriveStorage(Storage):
    """
    Storage class for Django that interacts with Google Drive as persistent
    storage.
    This class uses a system account for Google API that create an
    application drive (the drive is not owned by any Google User, but it is
    owned by the application declared on Google API console).
    """

    _UNKNOWN_MIMETYPE_ = 'application/octet-stream'
    _GOOGLE_DRIVE_FOLDER_MIMETYPE_ = 'application/vnd.google-apps.folder'
    KEY_FILE_PATH = 'GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE'
    KEY_FILE_CONTENT = 'GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE_CONTENTS'

    def __init__(self, json_keyfile_path=None, permissions=None):
        """
        Handles credentials and builds the google service.

        :param json_keyfile_path: Path
        :raise ValueError:
        """
        settings_keyfile_path = getattr(settings, self.KEY_FILE_PATH, None)
        self._json_keyfile_path = json_keyfile_path or settings_keyfile_path

        if self._json_keyfile_path:
            credentials = Credentials.from_service_account_file(
                self._json_keyfile_path,
                scopes=['https://www.googleapis.com/auth/drive'],
            )
        else:
            credentials = Credentials.from_service_account_info(
                json.loads(os.environ[self.KEY_FILE_CONTENT]),
                scopes=['https://www.googleapis.com/auth/drive'],
            )

        self._permissions = None
        if permissions is None:
            self._permissions = (_ANYONE_CAN_READ_PERMISSION_,)
        else:
            if not isinstance(permissions, (tuple, list,)):
                raise ValueError(
                    'Permissions should be a list or a tuple of '
                    'GoogleDriveFilePermission instances'
                )
            else:
                for p in permissions:
                    if not isinstance(p, GoogleDriveFilePermission):
                        raise ValueError(
                            'Permissions should be a list or a tuple of '
                            'GoogleDriveFilePermission instances'
                        )
                # Ok, permissions are good
                self._permissions = permissions

        self._drive_service = build('drive', 'v3', credentials=credentials)

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
        if folder_data is not None:
            return folder_data

        # Folder does not exists, have to create
        split_path = self._split_path(path)

        if split_path[:-1]:
            parent_path = os.path.join(*split_path[:-1])
            current_folder_data = self._get_or_create_folder(
                parent_path, parent_id=parent_id
            )
        else:
            current_folder_data = None

        meta_data = {
            'name': split_path[-1],
            'mimeType': self._GOOGLE_DRIVE_FOLDER_MIMETYPE_
        }
        if current_folder_data is not None:
            meta_data['parents'] = [current_folder_data['id']]
        else:
            # This is the first iteration loop so we have to set
            # the parent_id obtained by the user, if available
            if parent_id is not None:
                meta_data['parents'] = [parent_id]
        current_folder_data = self._drive_service.files().create(
            body=meta_data).execute()
        return current_folder_data

    def _check_file_exists(self, filename, parent_id=None):
        """
        Check if a file with specific parameters exists in Google Drive.
        :param filename: File or folder to search
        :type filename: string
        :param parent_id: Unique identifier for its parent (folder)
        :type parent_id: string
        :returns: dict containing file / folder data if exists or None if does not exists
        """  # noqa: E501
        if len(filename) == 0:
            # This is the lack of directory at the beginning of a 'file.txt'
            # Since the target file lacks directories, the assumption
            # is that it belongs at '/'
            return self._drive_service.files().get(fileId='root').execute()
        split_filename = self._split_path(filename)
        if len(split_filename) > 1:
            # This is an absolute path with folder inside
            # First check if the first element exists as a folder
            # If so call the method recursively with next portion of path
            # Otherwise the path does not exists hence
            # the file does not exists
            q = "mimeType = '{0}' and name = '{1}'".format(
                self._GOOGLE_DRIVE_FOLDER_MIMETYPE_, split_filename[0],
            )
            if parent_id is not None:
                q = "{0} and '{1}' in parents".format(q, parent_id)
            results = self._drive_service.files().list(
                q=q, fields='nextPageToken, files(*)').execute()
            items = results.get('files', [])
            for item in items:
                if item['name'] == split_filename[0]:
                    # Assuming every folder has a single parent
                    return self._check_file_exists(
                        os.path.sep.join(split_filename[1:]), item['id'])
            return None
        # This is a file, checking if exists
        q = "name = '{0}'".format(split_filename[0])
        if parent_id is not None:
            q = "{0} and '{1}' in parents".format(q, parent_id)
        results = self._drive_service.files().list(
            q=q, fields='nextPageToken, files(*)').execute()
        items = results.get('files', [])
        if len(items) > 0:
            return items[0]
        q = '' if parent_id is None else "'{0}' in parents".format(parent_id)
        results = self._drive_service.files().list(
            q=q, fields='nextPageToken, files(*)').execute()
        items = results.get('files', [])
        for item in items:
            if split_filename[0] in item['name']:
                return item
        return None

    # Methods that had to be implemented
    # to create a valid storage for Django

    def _open(self, name, mode='rb'):
        """For more details see
        https://developers.google.com/drive/api/v3/manage-downloads?hl=id#download_a_file_stored_on_google_drive
        """  # noqa: E501
        file_data = self._check_file_exists(name)
        request = self._drive_service.files().get_media(
            fileId=file_data['id'])
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            _, done = downloader.next_chunk()
        fh.seek(0)
        return File(fh, name)

    def _save(self, name, content):
        name = os.path.join(settings.GOOGLE_DRIVE_STORAGE_MEDIA_ROOT, name)
        folder_path = os.path.sep.join(self._split_path(name)[:-1])
        folder_data = self._get_or_create_folder(folder_path)
        parent_id = None if folder_data is None else folder_data['id']
        # Now we had created (or obtained) folder on GDrive
        # Upload the file
        mime_type, _ = mimetypes.guess_type(name)
        if mime_type is None:
            mime_type = self._UNKNOWN_MIMETYPE_
        media_body = MediaIoBaseUpload(
            content.file, mime_type, resumable=True, chunksize=1024 * 512)
        body = {
            'name': self._split_path(name)[-1],
            'mimeType': mime_type
        }
        # Set the parent folder.
        if parent_id:
            body['parents'] = [parent_id]
        file_data = self._drive_service.files().create(
            body=body,
            media_body=media_body).execute()

        # Setting up permissions
        for p in self._permissions:
            self._drive_service.permissions().create(
                fileId=file_data['id'], body={**p.raw}).execute()

        return file_data.get('originalFilename', file_data.get('name'))

    def delete(self, name):
        """
        Deletes the specified file from the storage system.
        """
        file_data = self._check_file_exists(name)
        if file_data is not None:
            self._drive_service.files().delete(
                fileId=file_data['id']).execute()

    def exists(self, name):
        """
        Returns True if a file referenced by the given name already exists
        in the storage system, or False if the name is available for
        a new file.
        """
        return self._check_file_exists(name) is not None

    def listdir(self, path):
        """
        Lists the contents of the specified path, returning a 2-tuple of lists;
        the first item being directories, the second item being files.
        """
        directories, files = [], []
        if path == '/':
            folder_id = {'id': 'root'}
        else:
            folder_id = self._check_file_exists(path)
        if folder_id:
            file_params = {
                'q': "'{0}' in parents and mimeType != '{1}'".format(
                    folder_id['id'], self._GOOGLE_DRIVE_FOLDER_MIMETYPE_),
            }
            dir_params = {
                'q': "'{0}' in parents and mimeType = '{1}'".format(
                    folder_id['id'], self._GOOGLE_DRIVE_FOLDER_MIMETYPE_),
            }
            files_results = self._drive_service.files().list(**file_params).execute()  # noqa: E501
            dir_results = self._drive_service.files().list(**dir_params).execute()  # noqa: E501
            files_list = files_results.get('files', [])
            dir_list = dir_results.get('files', [])
            for element in files_list:
                files.append(os.path.join(path, element['name']))
            for element in dir_list:
                directories.append(os.path.join(path, element['name']))
        return directories, files

    def size(self, name):
        """
        Returns the total size, in bytes, of the file specified by name.
        """
        file_data = self._check_file_exists(name)
        if file_data is None:
            return 0
        return file_data['size']

    def url(self, name):
        """
        Returns an absolute URL where the file's contents can be accessed
        directly by a Web browser.
        """
        file_data = self._check_file_exists(name)
        if file_data is None:
            return None
        return file_data['webContentLink']

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
        return parse(file_data['createdDate'])

    def modified_time(self, name):
        """
        Returns the last modified time (as datetime object) of the file
        specified by name.
        """
        file_data = self._check_file_exists(name)
        if file_data is None:
            return None
        return parse(file_data['modifiedDate'])

    def deconstruct(self):
        """
        Handle field serialization to support migration
        """
        name, path, args, kwargs = super().deconstruct()
        if self._service_email is not None:
            kwargs['service_email'] = self._service_email
        if self._json_keyfile_path is not None:
            kwargs['json_keyfile_path'] = self._json_keyfile_path
        return name, path, args, kwargs
