# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Provide configuration management for packaging.'''

import logging
import os
import site
from typing import Sequence
from urllib.parse import urljoin

from distlib.locators import PyPIJSONLocator

from . import config
from .config import Config
from .distributions import LocalDistributionPath, UserDistributionPath
from .package_manager import PackageManager
from .manifest import LockFile, SourceTreeFile

logger = logging.getLogger(__name__)

if site.ENABLE_USER_SITE:
    user_distribution = UserDistributionPath()

# Setup distribution paths
local_distribution = LocalDistributionPath()

# Load configuration files
if not os.path.exists(config.pyproject_path):
    source_tree_cfg = None
    source_tree_file = None
else:
    source_tree_cfg = Config(filepath=config.pyproject_path, writable=True)
    source_tree_file = SourceTreeFile(source_tree_cfg)
    local_distribution.create_pypackages_pth()
    # local_distribution.load_pypackages()

    if not os.path.exists(config.lock_path):
        lock_cfg = None
        lock_file = None
    else:
        lock_cfg = Config(filepath=config.lock_path, writable=True)
        lock_file = LockFile(lock_cfg)

print(source_tree_cfg)

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

__all__: Sequence[str] = [
    'local_distribution', 'package_manager', 'source_tree_cfg'
]
