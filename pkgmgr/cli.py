# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Arguments for inspection based CLI parser.'''

from . import local
from . import repository
from typing import Optional


def info(package: str):
    repository.get_package_info(package)


def download(package: str, dest: str = '.'):
    '''Download packages.'''
    repository.download_package(package, dest)


def install(package: str):
    '''Install packages.'''
    pass


def uninstall(package: str):
    '''Uninstall packages.'''
    pass


def freeze(package: str):
    '''Output installed packages in requirements format.'''
    pass


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
    pass


def search(package: str):
    '''Search PyPI for packages.'''
    repository.search(package)


def wheel():
    '''Build wheels from your requirements.'''
    pass


def hash():
    '''Compute hashes of package archives.'''
    pass


def completion():
    '''A helper command used for command completion.'''
    pass


def debug():
    '''Show information useful for debugging.'''
    pass
