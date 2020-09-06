# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Provide configuration management for pkgmgr.'''

import site


def get_site_packages_paths():
    '''Get installed packages from site.'''
    return site.getsitepackages()
