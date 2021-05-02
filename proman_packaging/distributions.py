# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Manage local distributions.'''

import logging
import os
import site
import sys
from typing import List, Optional

from distlib.database import Distribution, DistributionPath
# from distlib.index import PackageIndex
# from distlib.locators import locate
# from distlib.scripts import ScriptMaker
# from distlib.wheel import Wheel
from importlib_metadata import metadata
from importlib_metadata._meta import PackageMetadata
import hashin

from . import config

logger = logging.getLogger(__name__)


class DistributionPathMixin(DistributionPath):
    @property
    def packages(self) -> List[Distribution]:
        '''List installed packages.'''
        return [x for x in self.get_distributions()]

    @property
    def package_names(self) -> List[str]:
        '''Get packages names.'''
        return [x.name for x in self.get_distributions()]

    def get_version(self, name: str) -> Optional[str]:
        '''Get version of installed package.'''
        return next(
            (v for k, v in self.packages if k == name),
            None,
        )


class SystemDistributionPath(DistributionPathMixin):
    '''Manage system distributions.'''
    ...


class GlobalDistributionPath(DistributionPathMixin):
    '''Manage global distributions.'''
    ...


class LocalDistributionPath(DistributionPathMixin):
    '''Manage local distributions.'''

    def __init__(
        self,
        paths: List[str] = [],
        include_egg: bool = False,
    ) -> None:
        '''Initialize local distribution.'''
        self.dist_dir = os.path.join(
            config.pypackages_dir,
            f"{str(sys.version_info.major)}.{str(sys.version_info.minor)}",
        )
        # TODO: use pth
        paths.append(os.path.join(self.dist_dir, 'lib'))
        paths.append(os.path.join(self.dist_dir, 'lib64'))
        DistributionPath.__init__(self, paths, include_egg)

    def load_path(self) -> None:
        '''Add path to sys.path.'''
        for path in self.path:
            if os.path.isdir(path):
                if path not in sys.path:
                    sys.path.insert(-1, path)
            #     else:
            #         print('path already loaded')
            # else:
            #     print('path does not exist')

    def remove_path(self) -> None:
        '''Remove path from sys.path.'''
        for path in self.path:
            if path in sys.path:
                sys.path.remove(path)

    def is_installed(self, name: str) -> bool:
        '''Check is package is installed.'''
        return False if self.get_distribution(name) is None else True

    def create_pypackages(
        self, base_dir: Optional[str] = None
    ) -> None:
        '''Create pypackages directory.'''
        if not os.path.exists(self.dist_dir):
            os.makedirs(self.dist_dir)
        self.paths = {
            'prefix': self.dist_dir,
            'purelib': f"{self.dist_dir}/lib",
            'platlib': f"{self.dist_dir}/lib64",
            'scripts': f"{self.dist_dir}/bin",
            'headers': f"{self.dist_dir}/src",
            'data': f"{self.dist_dir}/share",
        }
        for k, v in self.paths.items():
            if k != 'prefix':
                os.makedirs(os.path.join(self.dist_dir, v), exist_ok=True)
        # self.load_path()


def get_site_packages_paths() -> List[str]:
    '''Get installed packages from site.'''
    # NOTE: site should probably be part of venv
    return site.getsitepackages()


def freeze() -> None:
    '''Output installed packages in requirements format.'''
    hashin.run(
        ['hashin'],
        'requirements.txt',
        'sha256',
        # args.python_version,
        # verbose=args.verbose,
        # include_prereleases=args.include_prereleases,
        # dry_run=args.dry_run,
        # interactive=args.interactive,
        # synchronous=args.synchronous,
        # index_url=args.index_url
    )


def show_package_metadata(name: str) -> PackageMetadata:
    '''Show information about installed packages.'''
    return metadata(name)


# def check() -> None:
#     '''Verify installed packages have compatible dependencies.'''
#     pass


# def wheel() -> None:
#     '''Build wheels from your requirements.'''
#     pass


# def hash() -> None:
#     '''Compute hashes of package archives.'''
#     pass
