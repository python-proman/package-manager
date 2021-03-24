# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Manage dependencies.'''

import os
import site
from typing import Any, Dict, List, Optional

from compendium.config_manager import ConfigManager, Settings
# from distlib.index import PackageIndex
# from distlib.locators import locate
# from distlib.scripts import ScriptMaker
# from distlib.wheel import Wheel
# from semantic_version import Version
import hashin
import urllib3

from . import config, exceptions

http = urllib3.PoolManager()


def get_site_packages_paths() -> List[str]:
    '''Get installed packages from site.'''
    return site.getsitepackages()


class ProjectSettingsMixin:
    '''Provide common methods for project settings.'''

    @staticmethod
    def dependency_type(dev: bool = False) -> str:
        '''Check if development dependency.'''
        return 'dev-dependencies' if dev else 'dependencies'


class SourceTreeManager(ProjectSettingsMixin):
    '''Manage source tree configuration file for project.

    see PEP-0517

    '''

    def __init__(
        self,
        config_path: str = os.path.join(os.getcwd(), 'pyproject.toml'),
        python_versions: tuple = (),
        hash_algorithm: str = 'sha256',
        include_prereleases: bool = False,
        lookup_memory: Optional[str] = None,
        index_url: str = 'https://pypi.org/simple',
    ) -> None:
        '''Initialize source tree defaults.'''
        # TODO: replace
        self.config_path = config_path

        config_manager = ConfigManager(
            application='proman',
            merge_strategy='partition',
            writable=True,
        )

        if os.path.exists(config_path):
            config_manager.load(filepath=config_path)
            self.__settings = config_manager.settings
            print(self.__settings)
        else:
            raise exceptions.PackageManagerConfig(
                'no config found'
            )

        self.python_versions = python_versions
        self.hash_algorithm = hash_algorithm
        self.include_prereleases = include_prereleases
        self.lookup_memory = lookup_memory
        # self.package_version = package_version
        self.index_url = index_url

    def is_dependency(self, package: str, dev: bool = False) -> bool:
        '''Check if dependency exists.'''
        return package in self.__settings.get(
            f"/tool/proman/{self.dependency_type(dev)}"
        )

    def retrieve_dependency(
        self,
        package: str,
        dev: bool = False,
    ) -> Dict[str, str]:
        '''Retrieve depencency configuration.'''
        return {
            x: v
            for x, v in self.__settings.get(
                f"/tool/proman/{self.dependency_type(dev)}"
            ).items()
            if (x == package)
        }

    def add_dependency(
        self,
        package: str,
        version: Optional[str] = None,
        dev: bool = False,
    ) -> None:
        '''Add dependency to configuration.'''
        if not self.is_dependency(package, dev):
            if version is None:
                version = '*'
            self.__settings.create(
                f"/tool/proman/{self.dependency_type(dev)}/{package}",
                version,
            )

    def remove_dependency(self, package: str) -> None:
        '''Remove dependency from configuration.'''
        for dev in [True, False]:
            if self.is_dependency(package, dev):
                self.__settings.delete(
                    f"/tool/proman/{self.dependency_type(dev)}/{package}"
                )

    def update_dependency(
        self,
        package: str,
        version: Optional[str] = None,
    ) -> None:
        '''Update existing dependency.'''
        self.remove_dependency(package)
        for dev in [True, False]:
            self.add_dependency(package, version, dev)


class LockManager(ProjectSettingsMixin):
    '''Manage project lock configuration file.'''

    def __init__(
        self,
        lock_path: str = os.getcwd() + '/proman.json',
        python_versions: Any = (),
        hash_algorithm: str = 'sha256',
        include_prereleases: bool = False,
        lookup_memory: Optional[bool] = None,
        index_url: str = 'https://pypi.org/simple',
    ):
        '''Initialize lock configuration settings.'''
        self.lock_path = lock_path
        self.__lock = Settings(
            application='proman', path=lock_path, writable=True
        )
        if os.path.exists(lock_path):
            self.__lock.load()

        self.python_versions = python_versions
        self.hash_algorithm = hash_algorithm
        self.include_prereleases = include_prereleases
        self.lookup_memory = lookup_memory
        # self.package_version = package_version
        self.index_url = index_url

    def lookup_hashes(
        self,
        package: str,
        version: Optional[str] = None,
    ) -> Dict[str, Any]:
        '''Lookup package hash from configuration.'''
        package_hashes = hashin.get_package_hashes(
            package=package,
            version=version,
            algorithm=self.hash_algorithm,
            python_versions=self.python_versions,
            verbose=False,
            include_prereleases=self.include_prereleases,
            lookup_memory=self.lookup_memory,
            index_url=self.index_url,
        )
        return package_hashes

    def is_locked(self, package: str, dev: bool = False) -> bool:
        '''Check if package lock is in configuration.'''
        result = any(
            package in p['package']
            for p in self.__lock.get('/' + self.dependency_type(dev))
        )
        return result

    def retrieve_lock(self, package: str, dev: bool = False) -> Dict[str, Any]:
        '''Retrieve package lock from configuration.'''
        result = [
            x
            for x in self.__lock.get('/' + self.dependency_type(dev))
            if x['package'] == package
        ]
        return result[0] if result else {}

    def update_lock(
        self,
        package: str,
        version: str,
        dev: bool = False
    ) -> None:
        '''Update existing package lock in configuration.'''
        update_lock = self.lookup_hashes(package, version)
        package_lock = self.retrieve_lock(package, dev)

        # TODO: handle version empty strings
        # if Version(update_lock['version']) > Version(package_lock['version']):
        print(update_lock['package'])
        self.__lock.update(
            '/' + self.dependency_type(dev),
            [
                x
                for x in self.__lock.get('/' + self.dependency_type(dev))
                if not (x['package'] == package_lock['package'])
            ],
        )
        self.__lock.append('/' + self.dependency_type(dev), update_lock)

    def add_lock(
        self,
        package: str,
        version: Optional[str] = None,
        dev: bool = False,
    ) -> None:
        '''Add package lock to configuration.'''
        if not self.is_locked(package, dev):
            package_hashes = self.lookup_hashes(package, version)
            self.__lock.append('/' + self.dependency_type(dev), package_hashes)
        else:
            print('package lock already exists')

    def remove_lock(self, package: str) -> None:
        '''Remove package lock from configuration.'''
        for type in ['dev-dependencies', 'dependencies']:
            self.__lock.update(
                type,
                [
                    x
                    for x in self.__lock.get(type)
                    if not (x['package'] == package)
                ],
            )


class DependencyManager:
    '''Manage local distributions.'''

    def __init__(
        self,
        path: List[str] = config.PATHS,
        include_egg: bool = False,
    ) -> None:
        '''Initialize local distribution.'''
        pass
