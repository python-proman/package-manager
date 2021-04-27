# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Interact with package repository to manage packages.'''

import importlib
# import io
import json
import os
import re
import pkg_resources
import shutil
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

from distlib.database import Distribution
from distlib.index import PackageIndex
from distlib.locators import locate
from distlib.scripts import ScriptMaker
from distlib.wheel import Wheel
import urllib3

from . import config
# from .config import Config
from .distributions import LocalDistribution
from .source_tree import LockManager, SourceTreeManager

http = urllib3.PoolManager()


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
    def get_info(
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
    def download_package(
        package: Distribution,
        dest: str = '.',
        digests: List[str] = [],
    ) -> Optional[str]:
        '''Execute package download.'''
        pkg_data = PyPIRepositoryMixin._lookup_package(package.name)
        # for k, v in pkg_data['releases'].items():
        #     print(k, v)

        # TODO create locator
        if pkg_data != {}:
            pkg = next(
                (
                    p
                    for p in pkg_data['urls']
                    if p['packagetype'] == 'bdist_wheel'
                ),
                (p for p in pkg_data['urls'] if p['packagetype'] == 'sdist'),
            )
            index = PackageIndex(url=urljoin(config.INDEX_URL, 'pypi'))
            filepath = os.path.join(dest, pkg['filename'])  # type: ignore
            index.download_file(
                pkg['url'],  # type: ignore
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
        # packages = []
        # with http.request(
        #     'GET', urljoin(url, 'simple'), preload_content=False
        # ) as rsp:
        #     tree = html.fromstring(rsp.data)
        #     packages = [p for p in tree.xpath('//a/text()') if name in p]
        # return packages


class PackageManager(PyPIRepositoryMixin):
    '''Perform package managment tasks for a project.'''

    def __init__(
        self,
        source_tree: SourceTreeManager,
        lock: LockManager,
        distribution: LocalDistribution,
        force: bool = False,
        update: bool = False,
        pypackages_enabled: bool = True,
        options: Dict[str, Any] = {},
    ) -> None:
        '''Initialize package manager configuration.'''
        self.__source_tree = source_tree
        self.__lockfile = lock
        self.distribution = distribution

        self.force = force
        self.update = update
        self.options = options
        self.pypackages_enabled = pypackages_enabled
        if self.pypackages_enabled:
            self.pypackages_dir = config.pypackages_dir

    @staticmethod
    def _refresh_packages() -> None:
        '''Reload package modules to refresh cache.'''
        # TODO: remove
        importlib.reload(pkg_resources)

    @staticmethod
    def get_dependencies(name: str) -> List[str]:
        '''Retrieve dependencies of a package.'''
        # TODO: remove
        # TODO: try catch if package is not found
        PackageManager._refresh_packages()
        pkg = pkg_resources.working_set.by_key[name.lower()]  # type: ignore
        return [str(req) for req in pkg.requires()]

    @staticmethod
    def get_name(package: str) -> Tuple[str, str]:
        '''Get package name.'''
        regex = '([a-zA-Z0-9._-]*)([<!~=>].*)'
        package_info = [x for x in re.split(regex, package) if x != '']
        name = package_info[0]
        if len(package_info) == 2:
            version = package_info[1]
        else:
            version = '*'
        return name, version

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
        options: dict
    ) -> None:
        '''Install wheel to selected paths.'''
        # create tempdir yield
        paths = self.distribution.create_pypackages()
        wheel = Wheel(filepath)
        wheel.install(paths=paths, maker=ScriptMaker(None, None))

    def __install_sdist(
        self,
        filepath: str,
        force: bool,
        upgrade: bool,
        options: dict
    ) -> None:
        '''Install source distribution to selected paths.'''
        ...

    def _install_package(
        self, package: Distribution, dev: bool = False
    ) -> None:
        '''Perform package installation.'''
        with TemporaryDirectory() as temp_dir:
            # TODO: multi-threading
            filepath = self.download_package(package, temp_dir, digests=[])
            if filepath:
                # TODO: download all packages before install
                self.__install_wheel(
                    filepath, self.force, self.update, self.options
                )
                # TODO: if not legacy egg
                # self.__install_sdist(
                #     package, filepath, self.force, self.update, options
                # )
                # TODO: lock should happen here
            else:
                print('package not found')
        for dependency in package.run_requires:
            self._install_package(locate(dependency), dev)

    # TODO: Split dependency lookup and install
    def install(
        self,
        package_version: str,
        dev: bool = False,
        python: Optional[str] = None,
        platform: Optional[str] = None,
        optional: bool = False,
        prerelease: bool = False,
    ) -> None:
        '''Install package and dependencies.'''
        # self.distribution.create_pypackages()
        package = locate(package_version)
        self.__source_tree.add_dependency(package, dev)
        self._install_package(package, dev)
        self.save()

    # Uninstall package
    def __remove_package(self, name: str) -> None:
        '''Remove package from distribution.'''
        paths = []
        dist = self.distribution.get_distribution(name)
        paths.append(dist.path)
        paths.append(
            os.path.abspath(os.path.join(dist.path, '..', name)).lower()
        )
        # TODO: need to add distribution resource paths
        for p in paths:
            if os.path.exists(p) and os.path.isdir(p):
                shutil.rmtree(p)
            else:
                print(f"{name} uninstall path does not exist")

    def _uninstall_package(self, package: Distribution) -> None:
        '''Perform package uninstall tasks.'''
        if self.distribution.is_installed(package.name):
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
            if self.distribution.is_installed(package.name):
                self.distribution.upgrade(package, force)
                # version = (
                #     self.distribution.get_version(name)
                # )
                # if self.__lockfile.is_locked(name):
                #     self.__lockfile.update_lock(name, version)
                # else:
                #     self.__lockfile.add_lock(name, version)
        else:
            # TODO: iterate and update all locks
            self.distribution.upgrade_all()
