# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Manage local installed packages.'''

from importlib_metadata import metadata
from typing import Optional
import pkg_resources


def freeze(package: str):
    '''Output installed packages in requirements format.'''
    pass


def list_installed_packages():
    '''List installed packages.'''
    return sorted([
        "{k} {v}".format(k=i.key, v=i.version)
        for i in pkg_resources.working_set
    ])


def show_package_metadata(package: str):
    '''Show information about installed packages.'''
    # return pkg_resources.get_distribution(package).__dict__
    return metadata(package)


def check():
    '''Verify installed packages have compatible dependencies.'''
    pass


def wheel():
    '''Build wheels from your requirements.'''
    pass


def hash():
    '''Compute hashes of package archives.'''
    pass
