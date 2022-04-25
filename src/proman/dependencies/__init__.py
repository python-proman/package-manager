# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Simple package manager for Python."""

import logging

import os
import site
from typing import List, Optional
from urllib.parse import urljoin

from distlib.locators import PyPIJSONLocator
from proman.common.config import Config
from proman.common.manifest import LockFile, SpecFile, Manifest

from . import config
from .distributions import LocalDistributionPath, UserDistributionPath
from .package_manager import PackageManager

__author__ = 'Jesse P. Johnson'
__title__ = 'proman-dependencies'
__version__ = '0.1.1-dev3'
__license__ = 'MPL-2.0'

logging.getLogger(__name__).addHandler(logging.NullHandler())

if site.ENABLE_USER_SITE:
    user_distribution = UserDistributionPath()

# Setup distribution paths
local_distribution = LocalDistributionPath()


def get_package_manager() -> 'PackageManager':
    """Get package manager."""
    # Load configuration files
    specfile = None
    lockfile = None

    if os.path.exists(config.pyproject_path):
        spec_cfg = Config(filepath=config.pyproject_path, writable=True)
        specfile = SpecFile(spec_cfg)
        local_distribution.create_pypackages_pth()
        # local_distribution.load_pypackages()

        if os.path.exists(config.lock_path):
            lock_cfg = Config(filepath=config.lock_path, writable=True)
            lockfile = LockFile(lock_cfg)
        else:
            logging.warning(f"log no lock found {config.lock_path}")
    else:
        logging.warning(f"log no source tree found {config.pyproject_path}")

    manifest: Optional[Manifest] = None
    if specfile and lockfile:
        manifest = Manifest(
            specfile=specfile,
            lockfile=lockfile,
            dependency_class={
                'module': 'dependencies.dependencies',
                'class': 'Dependency',
            }
        )
    else:
        print(specfile, lockfile)
    print(manifest)

    # TODO setup proxy capability
    # setup repository
    locator = PyPIJSONLocator(urljoin(config.INDEX_URL, 'pypi'))

    # Setup package manager
    return PackageManager(
        manifest=manifest,
        distribution_path=local_distribution,
        locator=locator,
    )


__all__: List[str] = [
    'local_distribution', 'package_manager', 'spec_cfg'
]
