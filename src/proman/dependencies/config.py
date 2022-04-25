# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
'''Provide configuration for package management.'''

import os
# from . import exception

INDEX_URL = 'https://pypi.org'
VENV_PATH = os.getenv('VIRTUAL_ENV', None)
PATHS = [VENV_PATH] if VENV_PATH else []

# TODO check VCS for paths
base_dir = os.getcwd()
pyproject_path = os.path.join(base_dir, 'pyproject.toml')
lock_path = os.path.join(base_dir, 'proman-lock.json')
pypackages_dir = os.path.join(base_dir, '__pypackages__')
