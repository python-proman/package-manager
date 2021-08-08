# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
'''Simple package manager for Python.'''

import logging

import os
import site
from typing import List
from urllib.parse import urljoin

from distlib.locators import PyPIJSONLocator

from . import config
from .config import Config
from .distributions import LocalDistributionPath, UserDistributionPath
from .package_manager import PackageManager
from .manifest import LockFile, SourceTreeFile

__author__ = 'Jesse P. Johnson'
__title__ = 'proman-dependencies'
__version__ = '0.1.1-dev3'
__license__ = 'MPL-2.0'

logging.getLogger(__name__).addHandler(logging.NullHandler())

if site.ENABLE_USER_SITE:
    user_distribution = UserDistributionPath()

# Setup distribution paths
local_distribution = LocalDistributionPath()

# Load configuration files
if os.path.exists(config.pyproject_path):
    source_tree_cfg = Config(filepath=config.pyproject_path, writable=True)
    source_tree_file = SourceTreeFile(source_tree_cfg)
    local_distribution.create_pypackages_pth()
    # local_distribution.load_pypackages()

    if not os.path.exists(config.lock_path):
        lock_cfg = Config(filepath=config.lock_path, writable=True)
        lock_file = LockFile(lock_cfg)
    else:
        logging.warning('log no config found')
else:
    logging.warning('log no lock found')

# TODO: is ephemeral pkgutil or site load with cleanup on exit
# atexit.register(local_distribution.remove_path)

# TODO setup proxy capability
# setup repository
locator = PyPIJSONLocator(urljoin(config.INDEX_URL, 'pypi'))

# Setup package manager
package_manager = PackageManager(
    source_tree=source_tree_file,
    lock=lock_file,
    distribution=local_distribution,
    locator=locator,
    force=False,
    update=False,
    options={}
)

__all__: List[str] = [
    'local_distribution', 'package_manager', 'source_tree_cfg'
]
