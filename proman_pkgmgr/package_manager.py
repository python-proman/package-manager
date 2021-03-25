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
# import shutil
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

from distlib.index import PackageIndex
# from distlib.locators import locate
from distlib.scripts import ScriptMaker
from distlib.wheel import Wheel
# from lxml import html
import urllib3

from . import config
from .config import SourceTreeManager
# from .dependencies import SourceTreeManager
from .distributions import LocalDistribution

distribution = LocalDistribution()
http = urllib3.PoolManager()


class PyPIRepositoryMixin:
    # Repository
    @staticmethod
    def _lookup_package(package_name: str) -> Dict[str, Any]:
        '''Get package metadata.'''
        rsp = http.request(
            'GET', urljoin(config.INDEX_URL, f"pypi/{package_name}/json")
        )
        # from pprint import pprint
        # pprint(vars(rsp))
        if rsp.status == 200:
            data = json.loads(rsp.data.decode('utf-8'))
            return data
        else:
            # print(f"{package_name} package not found")
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
    def download_package(
        name: str,
        dest: str = '.',
        digests: List[str] = [],
    ) -> str:
        '''Execute package download.'''
        pkg_data = PyPIRepositoryMixin._lookup_package(name)
        # TODO create locator
        pkg = next(
            (p for p in pkg_data['urls'] if p['packagetype'] == 'bdist_wheel'),
            (p for p in pkg_data['urls'] if p['packagetype'] == 'sdist'),
        )
        index = PackageIndex(url=urljoin(config.INDEX_URL, 'pypi'))
        filepath = os.path.join(dest, pkg['filename'])  # type: ignore
        index.download_file(
            pkg['url'], filepath, digest=None, reporthook=None  # type: ignore
        )
        return filepath

    @staticmethod
    def search(
        query: dict,
        operation: str = None,
        url: str = urljoin(config.INDEX_URL, 'pypi'),
    ) -> Dict[str, Any]:
        '''Search PyPI for packages.'''
        index = PackageIndex(url=url)
        return index.search({
                k: v
                for k, v in query.items() if v is not None
            },
            operation
        )
        # packages = []
        # with http.request(
        #     'GET',
        #     url + 'simple',
        #     preload_content=False
        # ) as rsp:
        #     tree = html.fromstring(rsp.data)
        #     packages = [p for p in tree.xpath('//a/text()') if name in p]
        # return packages


class PackageManager(SourceTreeManager, PyPIRepositoryMixin):
    '''Perform package managment tasks for a project.'''

    def __init__(
        self,
        force: bool = False,
        update: bool = False,
        pypackages_enabled: bool = True,
        options: Dict[str, Any] = {},
    ) -> None:
        '''Initialize package manager configuration.'''
        SourceTreeManager.__init__(self)

        self.force = force
        self.update = update
        self.options = options
        # TODO: should go with requirements
        # options('require-hashes')
        self.options['no-deps'] = True
        self.pypackages_enabled = pypackages_enabled
        if self.pypackages_enabled:
            # TODO: should depend on driver
            self.pypackages_dir = os.getcwd()
            self.pypackages_libs = [
                os.path.join(f"{self.pypackages_dir}, lib"),
                os.path.join(f"{self.pypackages_dir}, lib64"),
            ]
            distribution.create_pypackages_dir(
                base_dir=self.pypackages_dir
            )
            # print(site.getsitepackages())

    @staticmethod
    def _refresh_packages() -> None:
        '''Reload package modules to refresh cache.'''
        # TODO: refresh the cache not the module :/
        importlib.reload(pkg_resources)

    @staticmethod
    def get_package_dependencies(package_name: str) -> List[str]:
        '''Retrieve dependencies of a package.'''
        # TODO: try catch if package is not found
        pkg = pkg_resources\
            .working_set\
            .by_key[package_name.lower()]  # type: ignore
        return [str(req) for req in pkg.requires()]

    @staticmethod
    def get_package_name(package: str) -> Tuple[str, str]:
        '''Get package name.'''
        regex = '([a-zA-Z0-9._-]*)([<!~=>].*)'
        package_info = [x for x in re.split(regex, package) if x != '']
        package_name = package_info[0]
        if len(package_info) == 2:
            package_version = package_info[1]
        else:
            package_version = '*'
        return package_name, package_version

    @staticmethod
    def list(versions: bool = False) -> None:
        '''List installed packages.'''
        if versions:
            for k, v in distribution.packages:
                print("{k} {v}".format(k=k, v=v))
        else:
            print('\n'.join(distribution.package_names))

    def __get_options(self, dev: bool = False) -> Dict[str, Any]:
        '''Get package management options.'''
        # TODO: need to figure out how to separate dev/app modules
        if self.pypackages_enabled:  # and not dev:
            self.options['target'] = self.pypackages_dir
        return self.options

    # Install package
    def __install_wheel(
        self, package: str, force: bool, upgrade: bool, options: dict
    ) -> None:
        '''Add package to distribution.'''
        # create tempdir yield
        paths = distribution.create_distribution_dir()
        with TemporaryDirectory() as temp_dir:
            filepath = self.download_package(
                package, temp_dir, digests=[]
            )
            wheel = Wheel(filepath)
            wheel.install(paths=paths, maker=ScriptMaker(None, None))

    def _install_package(self, package: str, dev: bool = False) -> None:
        '''Perform package installation.'''
        package_name, package_version = PackageManager.get_package_name(package)
        options = self.__get_options()
        # TODO: Should dependencies be nested...
        self.__install_wheel(package_name, self.force, self.update, options)

        PackageManager._refresh_packages()
        for dependency in PackageManager.get_package_dependencies(package_name):
            self._install_package(dependency, dev)

    # TODO: Split dependency lookup and install
    def install(
        self,
        package: str,
        dev: bool = False,
        python: Optional[str] = None,
        platform: Optional[str] = None,
        optional: bool = False,
        prerelease: bool = False,
    ) -> None:
        '''Install package and dependencies.'''
        package_name, package_version = PackageManager.get_package_name(package)
        self.add_dependency(package_name, package_version, dev)
        self._install_package(package, dev)

    # Uninstall package
    def __remove_package(self, package_name: str) -> None:
        '''Remove package from distribution.'''
        pass

    def _uninstall_package(self, package: str) -> None:
        '''Perform package uninstall tasks.'''
        package_name, packag_version = PackageManager.get_package_name(package)
        # options = self.__get_options()

        if distribution.is_installed(package_name):
            for dependency in PackageManager.get_package_dependencies(
                package_name
            ):
                self.uninstall(dependency)
            self.__remove_package(package_name)
            # self.remove_lock(package_name)
        else:
            print("{p} is not installed".format(p=package_name))

    def uninstall(self, package: str) -> None:
        '''Uninstall package and dependencies.'''
        self.remove_dependency(package)
        self._uninstall_package(package)

    # Upgrade package
    def upgrade(self, package: str = 'all', force: bool = False) -> None:
        '''Upgrade/downgrade package and dependencies.'''
        package_name, package_version = PackageManager.get_package_name(package)

        if package != 'all' and distribution.is_installed(package_name):
            distribution.upgrade(package, force)
            # package_version = distribution.get_package_version(package_name)
            # if self.is_locked(package_name):
            #     self.update_lock(package_name, package_version)
            # else:
            #     self.add_lock(package_name, package_version)
        else:
            # TODO: iterate and update all locks
            distribution.upgrade_all()
