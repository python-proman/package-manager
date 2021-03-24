# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Manage local distributions.'''

import os
import sys
from typing import Dict, List, Optional

from distlib.database import Distribution, DistributionPath
# from distlib.index import PackageIndex
# from distlib.locators import locate
# from distlib.scripts import ScriptMaker
# from distlib.wheel import Wheel
from importlib_metadata import metadata
import hashin
import urllib3

from . import config

http = urllib3.PoolManager()


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


def get_installed_packages(
    paths: List[str] = [],
) -> List[Distribution]:
    '''List installed packages.'''
    dist_path = LocalDistribution(paths)
    return dist_path.installed_packages


def show_package_metadata(name: str) -> None:
    '''Show information about installed packages.'''
    return metadata(name)


def check() -> None:
    '''Verify installed packages have compatible dependencies.'''
    pass


def wheel() -> None:
    '''Build wheels from your requirements.'''
    pass


def hash() -> None:
    '''Compute hashes of package archives.'''
    pass


class LocalDistribution(DistributionPath):
    '''Manage local distributions.'''

    def __init__(
        self,
        path: List[str] = config.PATHS,
        include_egg: bool = False,
    ) -> None:
        '''Initialize local distribution.'''
        DistributionPath.__init__(self)

    @property
    def packages(self) -> List[Distribution]:
        '''List installed packages.'''
        return [x for x in self.get_distributions()]

    @property
    def package_names(self) -> List[str]:
        '''Get packages names.'''
        return [x.key for x in self.get_distributions()]

    @staticmethod
    def get_package_version(package_name: str) -> Optional[str]:
        '''Get version of installed package.'''
        return next(
            (
                v
                for k, v in LocalDistribution.packages  # type: ignore
                if k == package_name
            ),
            None,
        )

    def is_installed(self, name: str) -> bool:
        '''Check is package is installed.'''
        return False if self.get_distribution(name) is None else True

    def create_pypackages_dir(self, base_dir: Optional[str] = None) -> str:
        '''Create base directory.'''
        if not base_dir:
            base_dir = os.getcwd()
        dist_dir = os.path.join(
            base_dir,
            '__pypackages__',
            f"{str(sys.version_info.major)}.{str(sys.version_info.minor)}",
        )
        if not os.path.exists(dist_dir):
            os.makedirs(dist_dir)
        return dist_dir

    def create_distribution_dir(self) -> Dict[str, str]:
        '''Create pypackages directory.'''
        dist_dir = self.create_pypackages_dir()
        paths = {
            'prefix': dist_dir,
            'purelib': f"{dist_dir}/lib",
            'platlib': f"{dist_dir}/lib64",
            'scripts': f"{dist_dir}/bin",
            'headers': f"{dist_dir}/src",
            'data': f"{dist_dir}/share",
        }
        for k, v in paths.items():
            if k != 'prefix':
                os.makedirs(os.path.join(dist_dir, v), exist_ok=True)
        sys.path.append(f"{dist_dir}/lib")
        sys.path.append(f"{dist_dir}/lib64")
        return paths
