# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Manage local distributions.'''

import os
import site
import sys
from typing import Dict, List, Optional

from distlib.database import Distribution, DistributionPath
# from distlib.index import PackageIndex
# from distlib.locators import locate
# from distlib.scripts import ScriptMaker
# from distlib.wheel import Wheel
from importlib_metadata import metadata
import hashin

from . import config


class DistributionMixin(DistributionPath):
    @property
    def packages(self) -> List[Distribution]:
        '''List installed packages.'''
        return [x for x in self.get_distributions()]

    @property
    def package_names(self) -> List[str]:
        '''Get packages names.'''
        return [x.key for x in self.get_distributions()]

    def get_package_version(self, package_name: str) -> Optional[str]:
        '''Get version of installed package.'''
        return next(
            (
                v
                for k, v in self.packages
                if k == package_name
            ),
            None,
        )


class SystemDistribution(DistributionMixin):
    '''Manage system distributions.'''
    ...


class GlobalDistribution(DistributionMixin):
    '''Manage global distributions.'''
    ...


class LocalDistribution(DistributionMixin):
    '''Manage local distributions.'''

    def __init__(
        self,
        paths: Optional[List[str]] = None,
        include_egg: bool = False,
    ) -> None:
        '''Initialize local distribution.'''
        DistributionPath.__init__(self, paths, include_egg)

    @staticmethod
    def load_path(path: Optional[str] = None) -> None:
        '''Add path to sys.path.'''
        path = path or config.pypackages_dir
        if os.path.isdir(path):
            if path not in sys.path:
                sys.path.insert(-1, path)
            # else:
            #     print('path already loaded')
        # else:
        #     print('path does not exist')

    @staticmethod
    def remove_path(path: Optional[str] = None) -> None:
        '''Remove path from sys.path.'''
        path = path or config.pypackages_dir
        if path in sys.path:
            sys.path.remove(path)

    def is_installed(self, name: str) -> bool:
        '''Check is package is installed.'''
        return False if self.get_distribution(name) is None else True

    @staticmethod
    def create_pypackages_dir(base_dir: Optional[str] = None) -> str:
        '''Create base directory.'''
        if not base_dir:
            pypackages_dir = config.pypackages_dir
        else:
            pypackages_dir = os.path.join(base_dir, '__pypackages__')
        dist_dir = os.path.join(
            pypackages_dir,
            f"{str(sys.version_info.major)}.{str(sys.version_info.minor)}",
        )
        if not os.path.exists(dist_dir):
            os.makedirs(dist_dir)
        return dist_dir

    def create_distribution_dir(
        self, base_dir: Optional[str] = None
    ) -> Dict[str, str]:
        '''Create pypackages directory.'''
        dist_dir = self.create_pypackages_dir(base_dir)
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
        self.load_path(f"{dist_dir}/lib")
        self.load_path(f"{dist_dir}/lib64")
        return paths


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


def show_package_metadata(name: str) -> None:
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
