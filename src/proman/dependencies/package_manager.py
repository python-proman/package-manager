# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
'''Interact with package repository to manage packages.'''

# import io
import json
import logging
import os
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from urllib.parse import urljoin

from distlib import DistlibException
from distlib.database import Distribution
from distlib.index import PackageIndex
from distlib.locators import locate, Locator
from distlib.scripts import ScriptMaker
from distlib.wheel import Wheel
from packaging.specifiers import SpecifierSet
from proman.common.packaging_bases import PackageManagerBase
import urllib3

from . import config
from .dependencies import Dependency

if TYPE_CHECKING:
    from distlib.database import (
        DistributionPath,
        EggInfoDistribution,
        InstalledDistribution
    )
    from proman.common.manifest import Manifest

log = logging.getLogger(__name__)
http = urllib3.PoolManager(maxsize=16)


class PackageManager(PackageManagerBase):
    '''Perform package managment tasks for a project.'''

    def __init__(
        self,
        manifest: Optional['Manifest'],
        distribution_path: 'DistributionPath',
        locator: Locator,
        **options: Any,
    ) -> None:
        '''Initialize package manager configuration.'''
        self.__manifest = manifest
        self.__locator = locator
        self.distribution_path = distribution_path

        self.pypackages_enabled = options.get('pypackages_enabled', True)
        if self.pypackages_enabled:
            self.pypackages_dir = options.get(
                'pypackages_dir', config.pypackages_dir
            )

        if 'log_level' in options:
            log.setLevel(getattr(logging, options.pop('log_level').upper()))
        if 'log_handler' in options:
            log_handler = options.pop('log_handler')
            log.addHandler(logging.StreamHandler(log_handler))

    # Repository
    @staticmethod
    def _lookup_package(name: str) -> Dict[str, Any]:
        '''Get package metadata.'''
        # TODO: refactor to distlib
        url_path = urljoin(config.INDEX_URL, f"pypi/{name}/json")
        rsp = http.request('GET', url_path)
        if rsp.status == 200:
            data = json.loads(rsp.data.decode('utf-8'))
            return data
        else:
            log.error(f"{name} package not found")
            return {}

    @staticmethod
    def info(
        name: str,
        section: Optional[str] = None,
    ) -> Dict[str, Any]:
        '''Get package information.'''
        # TODO: refactor to distlib
        rst = PackageManager._lookup_package(name)
        if section:
            return rst[section]
        else:
            return rst

    @staticmethod
    def get_release(
        package: 'Distribution',
        package_type: str = 'bdist_wheel',
    ) -> Optional[Dict[str, Any]]:
        '''Get release from index.'''
        # TODO: refactor to distlib
        pkg_data = PackageManager._lookup_package(package.name)
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
    def download(
        package: Union['Distribution', Dict[str, Any]],
        dest: str = '.',
        digests: List[str] = [],
    ) -> Optional[str]:
        '''Execute package download.'''
        if isinstance(package, Distribution):
            release = PackageManager.get_release(package)
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
    def search(query: Any, **options: Any) -> Dict[str, Any]:
        '''Search PyPI for packages.'''
        operation = options.get('operation', None)
        url = options.get('url', urljoin(config.INDEX_URL, 'pypi'))
        index = PackageIndex(url=url)
        return index.search(
            {k: v for k, v in query.items() if v is not None},
            operation
        )

    @staticmethod
    def get_dependencies(package: 'Distribution') -> List['Distribution']:
        '''Get package dependencies.'''
        dependencies = []
        for sequence in package.run_requires:
            dependency = Dependency(sequence)
            dependencies.append(dependency)
            sub_dependencies = (
                PackageManager.get_dependencies(dependency)
            )
            dependencies = dependencies + sub_dependencies
        return dependencies

    def get_digests(self, sequence: str) -> Dict[str, Any]:
        '''Provide access to digests when not locally available.'''
        package = self.__locator.locate(sequence)
        return package.digests

    def save(self) -> None:
        '''Save each configuration.'''
        if self.__manifest:
            self.__manifest.source_tree.save()
            self.__manifest.lockfile.save()

    # def get_install(
    #     self,
    #     package: 'Distribution'
    # ) -> Optional['Distribution']:
    #     '''Check installed package is installed.'''
    #     install = next(
    #         (
    #             x
    #             for x in self.distribution_path.packages
    #             if x.key == list(package.keys())[0]
    #         ),
    #         None
    #     )
    #     return install

    # Install package
    def __install_wheel(
        self, filepath: str, **options: Any,
    ) -> 'InstalledDistribution':
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
            log.error('wheel did not pass validation')

    def __install_sdist(
        self, filepath: str, **options: Any,
    ) -> 'EggInfoDistribution':
        '''Install source distribution to selected paths.'''
        log.warning('sdist is here')
        return None

    def _install_package(
        self, package: 'Distribution', **options: str
    ) -> Optional['Dependency']:
        '''Perform package installation.'''
        release = (
            self.get_release(package)
            or self.get_release(package, package_type='sdist')
        )
        if release:
            # TODO: download all packages before install
            # print('---', release)
            digests = list(options.get('digests', []))
            filepath = self.download(
                release,
                options['temp_dir'],
                digests=digests
            )
            if filepath:
                if release['packagetype'] == 'bdist_wheel':
                    installed = Dependency(
                        self.__install_wheel(filepath, **options)
                    )
                elif release['packagetype'] == 'sdist':
                    installed = Dependency(
                        self.__install_sdist(filepath, **options)
                    )
                else:
                    log.error('no supported distribution found')
                return installed
            else:
                log.error('package could not be downloaded')
                return None
        else:
            log.error('package not found')
            return None

    def _perform_install(
        self, package: 'Distribution', **options: Any
    ) -> Optional['Dependency']:
        '''Perform coordination of installation processes.'''
        # check is package already installed
        installed = None
        if self.distribution_path.is_installed(package.name):
            installed = self.distribution_path.get_distribution(package.name)
            log.info('package installed:', installed)

        # check if package already locked
        locked = None
        if (
            self.__manifest
            and self.__manifest.lockfile.is_locked(package)
        ):
            locked = self.__manifest.lockfile.get_lock(package)
            log.info('package locked:', locked)

        if not installed:
            if locked:
                if self.__manifest:
                    lock = self.__manifest.lockfile.get_lock(
                        package.name,
                        package.is_dev,
                    )
                options['digests'] = lock['digests']

            installed = self._install_package(package, **options)
            print('---', type(installed))
            if installed and not locked:
                if installed.digests == {}:
                    # TODO: need to add missing digests
                    # installed.digests = self.get_digests(package.name)
                    pass
                if self.__manifest:
                    self.__manifest.lockfile.add_lock(installed)
        else:
            if self.__manifest and not locked:
                self.__manifest.lockfile.add_lock(installed)
        return installed

    def install(self, *packages: Any, **options: Any) -> None:
        '''Install package and dependencies.'''
        dev = options.get('dev', False)

        # create distribution paths
        self.distribution_path.create_pypackages()

        dependencies = []
        if packages:
            for package in packages:
                # TODO: json/rpc does not include run_requires
                # package = self.__locator.locate(sequence)
                dependency = Dependency(package, **options)
                log.debug(
                    'package specifier:',
                    SpecifierSet(f">={dependency.version}")
                )
                if self.__manifest:
                    self.__manifest.source_tree.add_dependency(dependency)
                dependencies += (
                    [dependency] + self.get_dependencies(dependency)
                )
                log.debug('installing dependencies:', dependencies)
        elif self.__manifest:
            for lock in self.__manifest.lockfile.get_locks(dev):
                # TODO: need better load from lockfile
                dependencies.append(Dependency(lock['name']))
        else:
            log.error('no depdencies found')

        if dependencies != []:
            with TemporaryDirectory() as temp_dir:
                options['temp_dir'] = temp_dir
                with ThreadPoolExecutor(max_workers=8) as executor:
                    jobs = [
                        executor.submit(
                            self._perform_install, dependency, **options
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
                            print('installed', installed)
            self.save()

    # Uninstall package
    def __remove_package(self, package: 'Distribution') -> None:
        '''Perform package uninstall tasks.'''
        # paths to be removed
        paths = []

        # add distribution info path
        dist = self.distribution_path.get_distribution(package.name)
        paths.append(dist.path)

        # add package paths
        installed = self.distribution_path.get_distribution(package.name)
        for filepath in installed.list_installed_files():
            for path in self.distribution_path.path:
                p = os.path.join(path, filepath[0].split(os.sep)[0])
                if p not in paths:
                    paths.append(p)

        # remove all paths
        for p in paths:
            if os.path.exists(p) and os.path.isfile(p):
                os.remove(p)
            elif os.path.exists(p) and os.path.isdir(p):
                shutil.rmtree(p)
            else:
                log.info(f"{package.name} uninstall path does not exist")

    def _uninstall_package(
        self, package: 'Distribution', **options: Any
    ) -> Optional[Union['EggInfoDistribution', 'InstalledDistribution']]:
        '''Perform coordination of installation processes.'''
        installed = None
        if self.distribution_path.is_installed(package.name):
            installed = self.distribution_path.get_distribution(package.name)
            self.__remove_package(installed)
            log.info('package uninstalled:', installed)
        else:
            log.info('could not uninstall non-existent package:', package.name)

        locked = None
        if (
            self.__manifest
            and self.__manifest.lockfile.is_locked(package)
        ):
            locked = self.__manifest.lockfile.get_lock(
                package.name,
                package.is_dev,
            )
            self.__manifest.lockfile.remove_lock(package)
            log.info('package unlocked:', locked)
        return installed

    def uninstall(self, *packages: Any, **options: Any) -> None:
        '''Uninstall package and dependencies.'''
        # TODO: compare removed dependencies with remaining
        dev = options.get('dev', False)
        if packages:
            for package in packages:
                # TODO: json/rpc does not include run_requires
                # package = self.__locator.locate(sequence)
                dependency = Dependency(packages[0])

                if (
                    dependency
                    and self.__manifest
                    and self.__manifest.source_tree.is_dependency(dependency)
                ):
                    self.__manifest.source_tree.remove_dependency(dependency)
                dependencies = [dependency] + self.get_dependencies(dependency)
        else:
            dependencies = []
            if self.__manifest:
                for lock in self.__manifest.lockfile.get_locks(dev):
                    # TODO: need better load from lockfile
                    dependencies.append(Dependency(lock['name']))

        if dependencies != []:
            with ThreadPoolExecutor(max_workers=8) as executor:
                jobs = [
                    executor.submit(
                        self._uninstall_package, dependency, **options
                    )
                    for dependency in dependencies
                ]
                for future in as_completed(jobs):
                    result = future.result()
                    if result:
                        print('result', result)
            self.save()

    # Upgrade package
    def update(self, *packages: Any, **options: Any) -> None:
        '''Upgrade/downgrade package and dependencies.'''
        # self.distribution_path.clear_cache()
        force = options.get('force', False)
        if packages:
            package = Dependency(packages[0])
            if self.distribution_path.is_installed(package.name):
                self.distribution_path.upgrade(package, force)
                # version = (
                #     self.distribution_path.get_version(name)
                # )
                # if self.__manifest.lockfile.is_locked(name):
                #     self.__manifest.lockfile.update_lock(name, version)
                # else:
                #     self.__manifest.lockfile.add_lock(name, version)
        else:
            # TODO: iterate and update all locks
            # self.distribution_path.upgrade_all()
            print('need process to uninstall and update packages')
