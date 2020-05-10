import codecs
import setuptools
import sys

long_description = codecs.open('README.rst', "r").read()

# Conditional load of enumeration
# See https://hynek.me/articles/conditional-python-dependencies/

INSTALL_REQUIRES = [
    "google-api-python-client >= 1.8.2",
    "python-dateutil >= 2.5.3",
    "requests >= 2.10.0",
    "django-appconf >= 1.0.2",
    "oauth2client >= 2.2.0",
    "six >= 1.10.0",
    "Django >= 3.0"
]

setuptools.setup(
    name="django-googledrive-storage",
    version="1.5.0",
    author="Gian Luca Dalla Torre",
    author_email="gianluca.dallatorre@gmail.com",
    description=("Storage implementation for Django that interacts with Google Drive"),
    license="LICENSE.txt",
    keywords="django google drive storage googledrive",
    url="https://github.com/torre76/django-googledrive-storage",
    download_url="https://github.com/torre76/django-googledrive-storage/tarball/1.5.0",
    packages=setuptools.find_packages(exclude=["django_googledrive_storage", "gdstorage.tests", "docs"]),
    long_description=long_description,
    package_data={
        '': ['README.rst'],
    },
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8"
    ],
)
