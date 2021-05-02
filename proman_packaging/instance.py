# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Provide configuration management for packaging.'''

from . import config
from .config import Config
from .source_tree import LockManager, SourceTreeManager
from .package_manager import PackageManager

pyproject_cfg = Config(filepath=config.pyproject_path, writable=True)
lock_cfg = Config(filepath=config.lock_path, writable=True)
src_tree_mgr = SourceTreeManager(pyproject_cfg)
lock_mgr = LockManager(lock_cfg)
package_mgr = PackageManager()
