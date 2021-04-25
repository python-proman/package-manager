# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Provide configuration for package management.'''

import os
from dataclasses import dataclass
from typing import Optional

from compendium.config_manager import ConfigFile

# from . import exception

INDEX_URL = 'https://test.pypi.org/'
path = os.getenv('VIRTUAL_ENV', None)
PATHS = [path] if path else []

base_dir = os.getcwd()
pyproject_path = os.path.join(base_dir, 'pyproject.toml')
lock_path = os.path.join(base_dir, 'proman.json')
pypackages_dir = os.path.join(base_dir, '__pypackages__')


@dataclass
class PyPIConfigFile:
    pass


@dataclass
class Config(ConfigFile):
    '''Manage settings from configuration file.'''

    filepath: str
    index_url: str = 'https://pypi.org/simple'
    python_versions: tuple = ()
    hash_algorithm: str = 'sha256'
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
