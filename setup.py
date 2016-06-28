import codecs
from setuptools import setup, find_packages

long_description = codecs.open('README.rst', "r").read()

setup(
    name = "django-googledrive-storage",
    version = "1.2.0",
    author = "Gian Luca Dalla Torre",
    author_email = "gianluca.dallatorre@gmail.com",
    description = ("Storage implementation for Django that interacts with Google Drive"),
    license = "LICENSE.txt",
    keywords = "django google drive storage googledrive",
    url = "https://github.com/torre76/django-googledrive-storage",
    download_url = "https://github.com/torre76/django-googledrive-storage/tarball/1.2.0",
    packages=find_packages(exclude=["django_googledrive_storage", "gdstorage.tests", "docs"]),
    long_description=long_description,
    package_data = {
        '': ['README.rst'],
    },
    install_requires=[
        "Django >= 1.7",
        "google-api-python-client >= 1.5.1",
        "python-dateutil >= 2.5.3",
        "requests >= 2.10.0",
        "django-appconf >= 1.0.2",
        "oauth2client >= 2.2.0"
    ],      
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    ],
)
