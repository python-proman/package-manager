# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Provide exceptions.'''


class PackageManagerException(Exception):
    '''Provide base errors in PackageManager.'''


class PackageManagerDriver(PackageManagerException):
    '''Provide exception for driver errors.'''


class PackageManagerConfig(PackageManagerException):
    '''Provide exception for Config errors.'''


class PackageManagerSettings(PackageManagerException):
    '''Provide exception for Settings errors.'''
