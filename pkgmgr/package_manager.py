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
import site
# import shutil
import sys
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

from distlib.index import PackageIndex
# from distlib.locators import locate
from distlib.scripts import ScriptMaker
from distlib.wheel import Wheel
import hashin
# from lxml import html
import urllib3

from . import _path, config
from .config import INDEX_URL, SourceTreeManager
from .distributions import LocalDistribution

distribution = LocalDistribution()
http = urllib3.PoolManager()


def _lookup_hashes(
    name: str,
    version: Optional[str] = None,
    hash_algorithm: str = 'sha256',
    python_versions: tuple = (),
    verbose: bool = False,
    include_prereleases: bool = False,
    lookup_memory: Optional[bool] = None,
    index_url: str = INDEX_URL,
) -> Dict[str, Any]:
    '''Lookup package hash from configuration.'''
    package_hashes = hashin.get_package_hashes(
        package=name,
        version=version,
        algorithm=hash_algorithm,
        python_versions=python_versions,
        verbose=False,
        include_prereleases=include_prereleases,
        lookup_memory=lookup_memory,
        index_url=index_url,
    )
    return package_hashes


def _get_package_data(package: str) -> Dict[str, Any]:
    '''Get package metadata.'''
    rsp = http.request('GET', urljoin(INDEX_URL, f"pypi/{package}/json"))
    # from pprint import pprint
    # pprint(vars(rsp))
    if rsp.status == 200:
        return json.loads(rsp.data.decode('utf-8'))
    else:
        print('package not found')
        return {}


def get_package_info(
    name: str,
    section: Optional[str] = None,
) -> Dict[str, Any]:
    '''Get package information.'''
    rst = _get_package_data(name)
    if section:
        return rst[section]
    else:
        return rst


def download_package(
    name: str,
    dest: str = '.',
    digests: List[str] = [],
) -> str:
    '''Execute package download.'''
    rst = _get_package_data(name)
    # TODO create locator
    pkg = next(
        (p for p in rst['urls'] if p['packagetype'] == 'bdist_wheel'),
        (p for p in rst['urls'] if p['packagetype'] == 'sdist'),
    )
    index = PackageIndex(url=urljoin(INDEX_URL, 'pypi'))
    filepath = os.path.join(dest, pkg['filename'])  # type: ignore
    index.download_file(
        pkg['url'], filepath, digest=None, reporthook=None  # type: ignore
    )
    return filepath


def install_package(name: str, version: str = None) -> None:
    '''Execute package install.'''
    # enumerate dependencies
    # reconcile versions
    # check gpg trust
    # download packages
    dist_dir = _path.create_pypackages_dir()
    with TemporaryDirectory() as td:
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
        filepath = download_package(name, td, digests=[])
        wheel = Wheel(filepath)
        wheel.install(paths=paths, maker=ScriptMaker(None, None))
    # check hashes
    # install


def uninstall_package(name: str) -> None:
    '''Execute package uninstall.'''
    # clean orphans
    pass


def search(
    query: dict,
    operation: str = None,
    url: str = urljoin(INDEX_URL, 'pypi'),
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


class PackageManager(SourceTreeManager):
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
            self.pypackages_dir = os.path.join(
                os.getcwd(),
                '__pypackages__',
                f"{str(sys.version_info.major)}.{str(sys.version_info.minor)}",
                'lib',
            )
            sys.path.append(self.pypackages_dir)
            print(site.getsitepackages())

    @staticmethod
    def __refresh_packages() -> None:
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
    def list(versions: bool = False) -> None:
        '''List installed packages.'''
        if versions:
            for k, v in distribution.installed_packages:
                print("{k} {v}".format(k=k, v=v))
        else:
            print('\n'.join(distribution.installed_package_names))

    @staticmethod
    def is_installed(package: str) -> bool:
        '''Check if a package is installed.'''
        return distribution.is_installed(package)

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
    def get_package_version(package_name: str) -> Optional[str]:
        '''Get package version.'''
        return next(
            (
                v
                for k, v in distribution.installed_packages
                if k == package_name
            ),
            None,
        )

    def _get_package_data(self, package_name: str) -> Dict[str, Any]:
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
            print(f"{package_name} package not found")
            return {}

    def __get_options(self, dev: bool = False) -> Dict[str, Any]:
        '''Get package management options.'''
        # TODO: need to figure out how to separate dev/app modules
        if self.pypackages_enabled:  # and not dev:
            self.options['target'] = self.pypackages_dir
        return self.options

    def add_package(
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
        package_name, package_version = self.get_package_name(package)
        options = self.__get_options()
        # TODO: Should dependencies be nested...
        self.add_package(package_name, self.force, self.update, options)

        self.__refresh_packages()
        for dependency in self.get_package_dependencies(package_name):
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
        package_name, package_version = self.get_package_name(package)
        self.add_dependency(package_name, package_version, dev)
        self._install_package(package, dev)

    def remove_package(self, package_name: str) -> None:
        '''Remove package from distribution.'''
        pass

    def _uninstall_package(self, package: str) -> None:
        '''Perform package uninstall tasks.'''
        package_name, packag_semver = self.get_package_name(package)
        # options = self.__get_options()

        if self.is_installed(package_name):
            for dependency in self.get_package_dependencies(package_name):
                self.uninstall(dependency)
            self.remove_package(package_name)
            # self.remove_lock(package_name)
        else:
            print("{p} is not installed".format(p=package_name))

    def uninstall(self, package: str) -> None:
        '''Uninstall package and dependencies.'''
        self.remove_dependency(package)
        self._uninstall_package(package)

    def upgrade(self, package: str = 'all', force: bool = False) -> None:
        '''Upgrade/downgrade package and dependencies.'''
        package_name, package_version = self.get_package_name(package)

        if package != 'all' and self.is_installed(package_name):
            distribution.upgrade(package, force)
            # package_version = self.get_package_version(package_name)
            # if self.is_locked(package_name):
            #     self.update_lock(package_name, package_version)
            # else:
            #     self.add_lock(package_name, package_version)
        else:
            # TODO: iterate and update all locks
            distribution.upgrade_all()

    def download_package(
        self,
        name: str,
        dest: str = '.',
        digests: List[str] = [],
    ) -> str:
        '''Execute package download.'''
        pkg_data = self._get_package_data(name)
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
