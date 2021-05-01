# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Interact with package repository to manage packages.'''

# import io
import json
import logging
import os
import re
import shutil
# import thread
from concurrent.futures import ThreadPoolExecutor, as_completed
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin

from distlib.database import (
    Distribution, EggInfoDistribution, InstalledDistribution
)
from distlib.index import PackageIndex
from distlib.locators import locate
from distlib.scripts import ScriptMaker
from distlib.wheel import Wheel
import urllib3

from . import config
# from .config import Config
from .distributions import LocalDistributionPath
from .source_tree import LockManager, SourceTreeManager

http = urllib3.PoolManager()
logger = logging.getLogger(__name__)


class PyPIRepositoryMixin:
    '''Provide Python Package Index integration.'''

    # Repository
    @staticmethod
    def _lookup_package(name: str) -> Dict[str, Any]:
        '''Get package metadata.'''
        url_path = urljoin(config.INDEX_URL, f"pypi/{name}/json")
        rsp = http.request('GET', url_path)
        if rsp.status == 200:
            data = json.loads(rsp.data.decode('utf-8'))
            return data
        else:
            print(f"{name} package not found")
            return {}

    @staticmethod
    def get_package_info(
        name: str,
        section: Optional[str] = None,
    ) -> Dict[str, Any]:
        '''Get package information.'''
        rst = PyPIRepositoryMixin._lookup_package(name)
        if section:
            return rst[section]
        else:
            return rst

    @staticmethod
    def get_release(
        package: Distribution,
        package_type: str = 'bdist_wheel',
    ) -> Optional[Dict[str, Any]]:
        '''Get release from index.'''
        pkg_data = PyPIRepositoryMixin._lookup_package(package.name)
        # from pprint import pprint
        # pprint(pkg_data)
        if pkg_data != {}:
            release = next(
                (
                    r
                    for r in pkg_data['releases'][package.version]
                    if r['packagetype'] == package_type
                ),
                None
            )
            return release
        else:
            return None

    @staticmethod
    def download_package(
        package: Union[Distribution, Dict[str, Any]],
        dest: str = '.',
        digests: List[str] = [],
    ) -> Optional[str]:
        '''Execute package download.'''
        if isinstance(package, Distribution):
            release = PyPIRepositoryMixin.get_release(package)
        else:
            release = package

        # TODO create locator
        if release:
            filepath = os.path.join(dest, release['filename'])
            index = PackageIndex(url=urljoin(config.INDEX_URL, 'pypi'))
            index.download_file(
                release['url'],
                filepath,
                digest=None,
                reporthook=None
            )
            return filepath
        else:
            return None

    @staticmethod
    def search(
        query: dict,
        operation: str = None,
        url: str = urljoin(config.INDEX_URL, 'pypi'),
    ) -> Dict[str, Any]:
        '''Search PyPI for packages.'''
        index = PackageIndex(url=url)
        return index.search(
            {k: v for k, v in query.items() if v is not None},
            operation
        )


class PackageManager(PyPIRepositoryMixin):
    '''Perform package managment tasks for a project.'''

    def __init__(
        self,
        source_tree: SourceTreeManager,
        lock: LockManager,
        distribution: LocalDistributionPath,
        force: bool = False,
        update: bool = False,
        pypackages_enabled: bool = True,
        options: Dict[str, Any] = {},
    ) -> None:
        '''Initialize package manager configuration.'''
        self.__source_tree = source_tree
        self.__lockfile = lock
        self.distribution_path = distribution

        self.force = force
        self.update = update
        self.options = options
        self.pypackages_enabled = pypackages_enabled
        if self.pypackages_enabled:
            self.pypackages_dir = config.pypackages_dir

    @staticmethod
    def get_name_version(package: str) -> Tuple[str, str]:
        '''Get package name and version.'''
        regex = '([a-zA-Z0-9._-]*)([<!~=>].*)'
        package_info = [x for x in re.split(regex, package) if x != '']
        name = package_info[0]
        if len(package_info) == 2:
            version = package_info[1]
        else:
            version = '*'
        return name, version

    @staticmethod
    def get_dependencies(package: Distribution) -> List[Distribution]:
        '''Get package dependencies.'''
        dependencies = []
        for package_version in package.run_requires:
            dependency = locate(package_version)
            dependencies.append(dependency)
            sub_dependencies = (
                PackageManager.get_dependencies(dependency)
            )
            dependencies = dependencies + sub_dependencies
        return dependencies

    def save(self) -> None:
        '''Save each configuration.'''
        self.__source_tree.save()
        self.__lockfile.save()

    # Install package
    def __install_wheel(
        self,
        filepath: str,
        force: bool,
        upgrade: bool,
        options: dict,
    ) -> InstalledDistribution:
        '''Install wheel to selected paths.'''
        wheel = Wheel(filepath)
        return wheel.install(
            paths=self.distribution_path.paths,
            maker=ScriptMaker(None, None),
            # bytecode_hashed_invalidation=True
        )

    def __install_sdist(
        self,
        filepath: str,
        force: bool,
        upgrade: bool,
        options: dict,
    ) -> EggInfoDistribution:
        '''Install source distribution to selected paths.'''
        print('sdist is here')
        return None

    def _install_package(
        self, package: Distribution, dev: bool = False, **kwargs: str
    ) -> Optional[Union[EggInfoDistribution, InstalledDistribution]]:
        '''Perform package installation.'''
        release = (
            self.get_release(package)
            or self.get_release(package, package_type='sdist')
        )
        if release:
            # TODO: download all packages before install
            filepath = self.download_package(
                release,
                kwargs['temp_dir'],
                digests=list(kwargs.get('digests', []))
            )
            if filepath:
                if release['packagetype'] == 'bdist_wheel':
                    installed_dist = self.__install_wheel(
                        filepath, self.force, self.update, self.options
                    )
                elif release['packagetype'] == 'sdist':
                    installed_dist = self.__install_sdist(
                        filepath, self.force, self.update, self.options
                    )
                else:
                    print('no supported distribution found')
                installed = (
                    self.distribution_path.get_distribution(package.name)
                )
                print(installed)
                # XXX: not getting hashes due to locaters/cache :/
                if installed_dist.digests == {}:
                    installed_dist.digests = release['digests']
                return installed_dist
            else:
                print('package could not be downloaded')
                return None
        else:
            print('package not found')
            return None

    def install(
        self,
        package_version: str,
        dev: bool = False,
        python: Optional[str] = None,
        platform: Optional[str] = None,
        optional: bool = False,
        prerelease: bool = False,
        **kwargs: Any,
    ) -> None:
        '''Install package and dependencies.'''
        # TODO: determine distribution path
        self.distribution_path.clear_cache()
        self.distribution_path.create_pypackages()
        package = locate(package_version)
        if self.distribution_path.is_installed(package.name):
            print('package is installed')
            # check source tree
            dependency = self.__source_tree.get_dependency(package.name, dev)
            if dependency:
                installed = next(
                    (
                        x
                        for x in self.distribution_path.packages
                        if x.name.lower() == list(dependency.keys())[0]
                    ),
                    None
                )
                print('dependency already defined', installed)
                # TODO: if in source tree get lock
            if 'update' in kwargs:
                print('check if update and update exists')
        # TODO: check existing packages
        self.__source_tree.add_dependency(package, dev)
        with TemporaryDirectory() as temp_dir:
            kwargs['temp_dir'] = temp_dir
            with ThreadPoolExecutor(max_workers=8) as executor:
                # for dep in [package] + self.get_dependencies(package):
                #     self._install_package(dep, dev, **kwargs)
                dependencies = [package] + self.get_dependencies(package)
                jobs = [
                    executor.submit(
                        self._install_package, dependency, dev, **kwargs
                    )
                    for dependency in dependencies
                ]
                for future in as_completed(jobs):
                    result = future.result()
                    if result:
                        print(
                            '---', result.key in [x.key for x in dependencies]
                        )
                        # lock = None
                        for x in dependencies:
                            # print(x.name, result.name)
                            for i in x.__dict__.items():
                                print(i)
                            # if x.key == result.key:
                            #     lock = x
                            #     print(lock.digests or lock.digest)
                        self.__lockfile.add_lock(result, dev)
        self.save()

    # Uninstall package
    def __remove_package(self, name: str) -> None:
        '''Remove package from distribution.'''
        paths = []
        dist = self.distribution_path.get_distribution(name)
        paths.append(dist.path)
        paths.append(
            os.path.abspath(os.path.join(dist.path, '..', name)).lower()
        )
        # TODO: need to add distribution resource paths None
        for p in paths:
            if os.path.exists(p) and os.path.isdir(p):
                shutil.rmtree(p)
            else:
                print(f"{name} uninstall path does not exist")

    def _uninstall_package(self, package: Distribution) -> None:
        '''Perform package uninstall tasks.'''
        if self.distribution_path.is_installed(package.name):
            for dependency in package.run_requires:
                self.uninstall(dependency)
            self.__remove_package(package.name)
            # self.__lockfile.remove_lock(name)
        else:
            print("{p} is not installed".format(p=package.name))

    def uninstall(self, name: str) -> None:
        '''Uninstall package and dependencies.'''
        # TODO: compare removed dependencies with remaining
        self.__source_tree.remove_dependency(name)
        self._uninstall_package(locate(name))
        self.save()

    # Upgrade package
    def upgrade(
        self, package_version: str = 'all', force: bool = False
    ) -> None:
        '''Upgrade/downgrade package and dependencies.'''
        if package_version != 'all':
            package = locate(package_version)
            if self.distribution_path.is_installed(package.name):
                self.distribution_path.upgrade(package, force)
                # version = (
                #     self.distribution_path.get_version(name)
                # )
                # if self.__lockfile.is_locked(name):
                #     self.__lockfile.update_lock(name, version)
                # else:
                #     self.__lockfile.add_lock(name, version)
        else:
            # TODO: iterate and update all locks
            self.distribution_path.upgrade_all()