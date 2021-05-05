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
from concurrent.futures import ThreadPoolExecutor, as_completed
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin

from distlib.database import (
    Distribution, DistributionPath, EggInfoDistribution, InstalledDistribution
)
from distlib import DistlibException
from distlib.index import PackageIndex
from distlib.locators import locate, Locator
from distlib.resources import finder
from distlib.scripts import ScriptMaker
from distlib.wheel import Wheel
import urllib3

from . import config
# from .config import Config
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
        distribution: DistributionPath,
        locator: Locator,
        force: bool = False,
        update: bool = False,
        pypackages_enabled: bool = True,
        options: Dict[str, Any] = {},
    ) -> None:
        '''Initialize package manager configuration.'''
        self.__source_tree = source_tree
        self.__lockfile = lock
        self.distribution_path = distribution
        self.locator = locator

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
        for sequence in package.run_requires:
            dependency = locate(sequence)
            dependencies.append(dependency)
            sub_dependencies = (
                PackageManager.get_dependencies(dependency)
            )
            dependencies = dependencies + sub_dependencies
        return dependencies

    def get_digests(self, sequence: str) -> Dict[str, Any]:
        '''Provide access to digests when not locally available.'''
        package = self.locator.locate(sequence)
        return package.digests

    def save(self) -> None:
        '''Save each configuration.'''
        self.__source_tree.save()
        self.__lockfile.save()

    def get_install(self, package: Distribution) -> Optional[Distribution]:
        '''Check installed package is installed.'''
        install = next(
            (
                x
                for x in self.distribution_path.packages
                if x.key == list(package.keys())[0]
            ),
            None
        )
        return install

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
        try:
            wheel.verify()
            return wheel.install(
                paths=self.distribution_path.paths,
                maker=ScriptMaker(None, None),
                # bytecode_hashed_invalidation=True
            )
        except DistlibException:
            print('wheel did not pass validation')

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
            print('----', release)
            digests = list(kwargs.get('digests', []))
            filepath = self.download_package(
                release,
                kwargs['temp_dir'],
                digests=digests
            )
            if filepath:
                if release['packagetype'] == 'bdist_wheel':
                    installed = self.__install_wheel(
                        filepath, self.force, self.update, self.options
                    )
                elif release['packagetype'] == 'sdist':
                    installed = self.__install_sdist(
                        filepath, self.force, self.update, self.options
                    )
                else:
                    print('no supported distribution found')
                return installed
            else:
                print('package could not be downloaded')
                return None
        else:
            print('package not found')
            return None

    def _perform_install(
        self, package: Distribution, dev: bool, **kwargs: Any
    ) -> Optional[Union[EggInfoDistribution, InstalledDistribution]]:
        '''Perform coordination of installation processes.'''
        installed = None
        if self.distribution_path.is_installed(package.name):
            installed = self.distribution_path.get_distribution(package.name)
            print('package installed:', installed)

        locked = None
        if self.__lockfile.is_locked(package.name, dev):
            locked = self.__lockfile.get_lock(package.name, dev)
            print('package locked:', locked)

        if not installed:
            if locked:
                lock = self.__lockfile.get_lock(package.name, dev)
                kwargs['digests'] = lock['digests']
            installed = self._install_package(package, dev, **kwargs)
            if installed and not locked:
                if installed.digests == {}:
                    installed.digests = self.get_digests(package.name)
                self.__lockfile.add_lock(installed, dev)
        else:
            if not locked:
                self.__lockfile.add_lock(installed, dev)
        return installed

    def install(
        self,
        sequence: Optional[str] = None,
        dev: bool = False,
        python: Optional[str] = None,
        platform: Optional[str] = None,
        optional: bool = False,
        prerelease: bool = False,
        **kwargs: Any,
    ) -> None:
        '''Install package and dependencies.'''
        # TODO: selectable distribution path
        # self.distribution_path.clear_cache()
        self.distribution_path.create_pypackages()

        if sequence:
            package = locate(sequence)
            # TODO: json/rpc does not include run_requires
            # package = self.locator.locate(sequence)

            self.__source_tree.add_dependency(package, dev)
            dependencies = [package] + self.get_dependencies(package)
        else:
            dependencies = []
            for lock in self.__lockfile.get_locks(dev):
                # TODO: need better load from lockfile
                dependencies.append(locate(lock['name']))

        if dependencies != []:
            with TemporaryDirectory() as temp_dir:
                kwargs['temp_dir'] = temp_dir
                with ThreadPoolExecutor(max_workers=8) as executor:
                    jobs = [
                        executor.submit(
                            self._perform_install, dependency, dev, **kwargs
                        )
                        for dependency in dependencies
                    ]
                    for future in as_completed(jobs):
                        result = future.result()
                        if result:
                            # print(
                            #     '---',
                            #     result.key in [x.key for x in dependencies]
                            # )
                            installed = [
                              x
                              for x in dependencies
                              if x.key == result.key
                            ][0]

                            print(installed)
            self.save()

    # Uninstall package
    def _uninstall_package(self, package: Distribution, dev: bool) -> None:
        '''Perform package uninstall tasks.'''
        # paths to be removed
        paths = []

        # add distribution info path
        dist = self.distribution_path.get_distribution(package.name)
        paths.append(dist.path)

        # add package paths
        for x in finder(package.key).iterator(''):
            print(package.key, x.name, x.is_container, x.path)
            paths.append(x.path)

        # remove all paths
        for p in paths:
            if os.path.exists(p) and os.path.isfile(p):
                os.remove(p)
            elif os.path.exists(p) and os.path.isdir(p):
                shutil.rmtree(p)
            else:
                print(f"{package.name} uninstall path does not exist")

    def _perform_uninstall(
        self, package: Distribution, dev: bool, **kwargs: Any
    ) -> Optional[Union[EggInfoDistribution, InstalledDistribution]]:
        '''Perform coordination of installation processes.'''
        installed = None
        if self.distribution_path.is_installed(package.name):
            installed = self.distribution_path.get_distribution(package.name)
            self._uninstall_package(installed, dev)
            print('package uninstalled:', installed)

        locked = None
        if self.__lockfile.is_locked(package.name, dev):
            locked = self.__lockfile.get_lock(package.name, dev)
            self.__lockfile.remove_lock(package.name, dev)
            print('package unlocked:', locked)
        return installed

    def uninstall(
        self,
        sequence: Optional[str] = None,
        dev: bool = False,
        **kwargs: Any
    ) -> None:
        '''Uninstall package and dependencies.'''
        # TODO: compare removed dependencies with remaining

        if sequence:
            package = locate(sequence)
            # TODO: json/rpc does not include run_requires
            # package = self.locator.locate(sequence)

            if package and self.__source_tree.is_dependency(package.name, dev):
                self.__source_tree.remove_dependency(package.name, dev)

            dependencies = [package] + self.get_dependencies(package)
        else:
            dependencies = []
            for lock in self.__lockfile.get_locks(dev):
                # TODO: need better load from lockfile
                dependencies.append(locate(lock['name']))

        if dependencies != []:
            with ThreadPoolExecutor(max_workers=8) as executor:
                jobs = [
                    executor.submit(
                        self._perform_uninstall, dependency, dev, **kwargs
                    )
                    for dependency in dependencies
                ]
                for future in as_completed(jobs):
                    result = future.result()
                    if result:
                        print(result)
            self.save()

    # Upgrade package
    def upgrade(
        self, sequence: Optional[str], force: bool = False
    ) -> None:
        '''Upgrade/downgrade package and dependencies.'''
        if sequence:
            package = locate(sequence)
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
            # self.distribution_path.upgrade_all()
            print('need process to uninstall and update packages')
