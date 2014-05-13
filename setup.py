import codecs
from setuptools import setup

long_description = codecs.open('README.rst', "r").read()

setup(
    name = "django-googledrive-storage",
    version = "1.0.0",
    author = "Gian Luca Dalla Torre",
    author_email = "gianluca.dallatorre@gmail.com",
    description = ("Storage implementation for Django that interacts with Google Drive"),
    license = "LICENSE.txt",
    keywords = "django google drive storage googledrive",
    url = "https://github.com/torre76/django-googledrive-storage",
    download_url = "https://github.com/torre76/django-googledrive-storage/tarball/1.0.0",
    packages=['gdstorage'],
    long_description=long_description,
    package_data = {
        '': ['README.rst'],
    },
    install_requires=[
        "Django >= 1.6",
        "google-api-python-client >= 1.2",
        "pycrypto >= 2.6.1",
        "python-dateutil >=2.2",
        "requests >= 2.2.1",
    ],      
    classifiers=[
        "Development Development Status :: 4 - Beta",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2 :: Only"
    ],
)