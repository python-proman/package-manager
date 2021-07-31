# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Provide configuration for package management.'''

import os
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin

from compendium.loader import ConfigFile

# from . import exception

INDEX_URL = 'https://pypi.org'
VENV_PATH = os.getenv('VIRTUAL_ENV', None)
PATHS = [VENV_PATH] if VENV_PATH else []

# TODO check VCS for paths
base_dir = os.getcwd()
pyproject_path = os.path.join(base_dir, 'pyproject.toml')
lock_path = os.path.join(base_dir, 'proman-lock.json')
pypackages_dir = os.path.join(base_dir, '__pypackages__')


@dataclass
class Config(ConfigFile):
    '''Manage settings from configuration file.'''

    filepath: str
    index_url: str = urljoin(INDEX_URL, 'simple')
    python_versions: tuple = ()
    digest_algorithm: str = 'sha256'
    include_prereleases: bool = False
    lookup_memory: Optional[str] = None
    writable: bool = True

    def __post_init__(self) -> None:
        '''Initialize settings from configuration.'''
        super().__init__(self.filepath)
        if os.path.isfile(self.filepath):
            self.load()

        # try:
        #     self.load()
        # except Exception:
        #     raise exception.PackageManagerConfig('no config found')
