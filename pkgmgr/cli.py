# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Arguments for inspection based CLI parser.'''

from . import configuration
from . import local
from . import repository
from typing import Optional
import json


def info(package: str):
    '''Get package info.'''
    info = repository.get_package_info(package)
    print(json.dumps(info, indent=2))


def download(package: str, dest: str = '.'):
    '''Download packages.'''
    repository.download_package(package, dest)


def install(package: str):
    '''Install packages.'''
    pass


def uninstall(package: str):
    '''Uninstall packages.'''


def freeze():
    '''Output installed packages in requirements format.'''
    local.freeze()


def list():
    '''List installed packages.'''
    for p in local.list_installed_packages():
        print(p)


def show(package: str):
    '''Show information about installed packages.'''
    for key, val in local.show_package_metadata(package).items():
         print("{k} {v}".format(k=key, v=val))


def check():
    '''Verify installed packages have compatible dependencies.'''
    pass


def config():
    '''Manage local and global configuration.'''
    print(configuration.get_site_packages_paths())


def search(package: str):
    '''Search PyPI for packages.'''
    packages = repository.search(package)
    for package in packages:
        print(package)


def wheel():
    '''Build wheels from your requirements.'''
    pass


def hash(package: str, algorithm: str = 'sha256'):
    '''Compute hashes of package archives.'''
    print(repository._lookup_hashes(package))


def completion():
    '''A helper command used for command completion.'''
    pass


def debug():
    '''Show information useful for debugging.'''
    pass
