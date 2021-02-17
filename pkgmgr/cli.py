# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Arguments for inspection based CLI parser.'''

import json
from typing import Optional

from . import configuration
from . import local
from . import repository


def info(name: str):
    '''Get package info.'''
    info = repository.get_package_info(name)
    print(json.dumps(info, indent=2))


def download(name: str, dest: str = '.'):
    '''Download packages.'''
    repository.download_package(name, dest)


def install(name: str, version: str = None):
    '''Install packages.'''
    repository.install_package(name, version)


def uninstall(name: str):
    '''Uninstall packages.'''
    pass


def freeze():
    '''Output installed packages in requirements format.'''
    local.freeze()


def list():
    '''List installed packages.'''
    for p in local.list_installed_packages():
        print(p)


def show(name: str):
    '''Show information about installed packages.'''
    for key, val in local.show_package_metadata(name).items():
        print("{k} {v}".format(k=key, v=val))


def check():
    '''Verify installed packages have compatible dependencies.'''
    pass


def config():
    '''Manage local and global configuration.'''
    print(configuration.get_site_packages_paths())


def search(
    name: str,
    version: Optional[str] = None,
    stable_version: Optional[str] = None,
    author: Optional[str] = None,
    author_email: Optional[str] = None,
    maintainer: Optional[str] = None,
    maintainer_email: Optional[str] = None,
    home_page: Optional[str] = None,
    license: Optional[str] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    keywords: Optional[str] = None,
    platform: Optional[str] = None,
    download_url: Optional[str] = None,
    classifiers: Optional[str] = None,
    project_url: Optional[str] = None,
    docs_url: Optional[str] = None,
    operation: Optional[str] = None,
):
    '''Search PyPI for packages.'''
    packages = repository.search(
        query={
            'name': name,
            'version': version,
            'stable_version': stable_version,
            'author': author,
            'author_email': author_email,
            'maintainer': maintainer,
            'maintainer_email': maintainer_email,
            'home_page': home_page,
            'license': license,
            'summary': summary,
            'description': description,
            'keywords': keywords,
            'platform': platform,
            'download_url': download_url,
            'classifiers': classifiers,
            'project_url': project_url,
            'docs_url': docs_url,
        },
        operation=operation,
    )
    for package in packages:
        print(
            package['name'].ljust(25),
            package['version'].ljust(15),
            package['summary']
        )


def wheel():
    '''Build wheels from your requirements.'''
    pass


def hash(package: str, algorithm: str = 'sha256'):
    '''Compute hashes of package archives.'''
    print(repository._lookup_hashes(package))


def completion():
    '''A helper command used for command completion.'''
    pass
