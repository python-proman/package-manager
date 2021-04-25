# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Resolve package dependencies.'''

from typing import Any, Dict, Optional

# from distlib.index import PackageIndex
# from distlib.locators import locate
# from distlib.scripts import ScriptMaker
# from distlib.wheel import Wheel
# from semantic_version import Version
import hashin

# from . import exception
from .config import Config


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

    def __init__(self, config_file: Config) -> None:
        '''Initialize source tree defaults.'''
        self.__settings = config_file

    def is_dependency(self, package: str, dev: bool = False) -> bool:
        '''Check if dependency exists.'''
        return package in self.__settings.retrieve(
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
            for x, v in self.__settings.retrieve(
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

    def save(self) -> None:
        '''Update the source tree config.'''
        self.__settings.dump(writable=True)


class LockManager(ProjectSettingsMixin):
    '''Manage project lock configuration file.'''

    def __init__(self, lock_config: Config):
        '''Initialize lock configuration settings.'''
        self.__settings = lock_config

    def lookup_hashes(
        self,
        package: str,
        version: Optional[str] = None,
    ) -> Dict[str, Any]:
        '''Lookup package hash from configuration.'''
        package_hashes = hashin.get_package_hashes(
            package=package,
            version=version,
            algorithm=self.__settings.hash_algorithm,
            python_versions=self.__settings.python_versions,
            verbose=False,
            include_prereleases=self.__settings.include_prereleases,
            lookup_memory=self.__settings.lookup_memory,
            index_url=self.__settings.index_url,
        )
        return package_hashes

    def is_locked(self, package: str, dev: bool = False) -> bool:
        '''Check if package lock is in configuration.'''
        result = any(
            package in p['package']
            for p in self.__settings.retrieve(f"/{self.dependency_type(dev)}")
        )
        return result

    def retrieve_lock(self, package: str, dev: bool = False) -> Dict[str, Any]:
        '''Retrieve package lock from configuration.'''
        result = [
            x
            for x in self.__settings.retrieve(f"/{self.dependency_type(dev)}")
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
        # print(update_lock['package'])
        self.__settings.set(
            f"/{self.dependency_type(dev)}",
            [
                x
                for x in self.__settings.retrieve(
                    f"/{self.dependency_type(dev)}"
                )
                if not (x['package'] == package_lock['package'])
            ],
        )
        self.__settings.append(f"/{self.dependency_type(dev)}", update_lock)

    def add_lock(
        self,
        package: str,
        version: Optional[str] = None,
        dev: bool = False,
    ) -> None:
        '''Add package lock to configuration.'''
        if not self.is_locked(package, dev):
            package_hashes = self.lookup_hashes(package, version)
            self.__settings.append(
                f"/{self.dependency_type(dev)}", package_hashes
            )
        else:
            print('package lock already exists')

    def remove_lock(self, package: str) -> None:
        '''Remove package lock from configuration.'''
        for type in ['dev-dependencies', 'dependencies']:
            self.__settings.set(
                type,
                [
                    x
                    for x in self.__settings.retrieve(type)
                    if not (x['package'] == package)
                ],
            )

    def save(self) -> None:
        '''Update the source tree config.'''
        self.__settings.dump(writable=True)
