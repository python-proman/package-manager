# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
'''Resolve package dependencies.'''

from typing import Any, Dict, List

from distlib.database import Distribution

# from . import exception
from .config import Config


class ProjectSettingsMixin:
    '''Provide common methods for project settings.'''

    @staticmethod
    def dependency_type(dev: bool = False) -> str:
        '''Check if development dependency.'''
        return 'dev-dependencies' if dev else 'dependencies'


class SourceTreeFile(ProjectSettingsMixin):
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

    def get_dependencies(self, dev: bool = False) -> List[Dict[str, Any]]:
        '''Retrieve depencency configuration.'''
        return self.__settings.retrieve(
            f"/tool/proman/{self.dependency_type(dev)}"
        )

    def get_dependency(
        self, name: str, dev: bool = False,
    ) -> Dict[str, str]:
        '''Retrieve depencency configuration.'''
        return {
            x: v
            for x, v in self.__settings.retrieve(
                f"/tool/proman/{self.dependency_type(dev)}"
            ).items()
            if (x == name)
        }

    def add_dependency(
        self, package: Distribution, dev: bool = False,
    ) -> None:
        '''Add dependency to configuration.'''
        if not self.is_dependency(package.key, dev):
            if package.version is None:
                version = '*'
            else:
                version = package.version
            self.__settings.create(
                f"/tool/proman/{self.dependency_type(dev)}/{package.name}",
                version,
            )

    def remove_dependency(self, name: str, dev: bool = False) -> None:
        '''Remove dependency from configuration.'''
        if self.is_dependency(name, dev):
            self.__settings.delete(
                f"/tool/proman/{self.dependency_type(dev)}/{name}"
            )

    def update_dependency(
        self, package: Distribution, dev: bool = False
    ) -> None:
        '''Update existing dependency.'''
        self.remove_dependency(package.name, dev)
        self.add_dependency(package, dev)

    def save(self) -> None:
        '''Update the source tree config.'''
        self.__settings.dump(writable=True)


class LockFile(ProjectSettingsMixin):
    '''Manage project lock configuration file.'''

    def __init__(self, lock_config: Config):
        '''Initialize lock configuration settings.'''
        self.__settings = lock_config

    def is_locked(self, name: str, dev: bool = False) -> bool:
        '''Check if package lock is in configuration.'''
        result = any(
            name in p['name']
            for p in self.__settings.retrieve(f"/{self.dependency_type(dev)}")
        )
        return result

    def get_locks(self, dev: bool = False) -> List[Dict[str, Any]]:
        '''Get all dependencies.'''
        return self.__settings.retrieve(f"/{self.dependency_type(dev)}")

    def get_lock(self, name: str, dev: bool = False) -> Dict[str, Any]:
        '''Retrieve package lock from configuration.'''
        result = [
            x
            for x in self.__settings.retrieve(f"/{self.dependency_type(dev)}")
            if x['name'] == name
        ]
        return result[0] if result else {}

    def update_lock(
        self,
        package: Distribution,
        dev: bool = False
    ) -> None:
        '''Update existing package lock in configuration.'''
        self.remove_lock(package.name, dev)
        self.add_lock(package, dev)

    def add_lock(
        self,
        package: Distribution,
        dev: bool = False,
    ) -> None:
        '''Add package lock to configuration.'''
        if not self.is_locked(package.name, dev):
            # package_hashes = self.lookup_hashes(
            #     package.name, package.version
            # )
            print('package', package.__dict__)
            lock = {
                'name': package.name,
                'version': package.version,
                'digests': [':'.join(v) for k, v in package.digests.items()]
            }
            self.__settings.append(f"/{self.dependency_type(dev)}", lock)
        else:
            print('package lock already exists')

    def remove_lock(self, name: str, dev: bool = False) -> None:
        '''Remove package lock from configuration.'''
        self.__settings.set(
            f"/{self.dependency_type(dev)}",
            [
                x
                for x in self.get_locks(dev)
                if not x['name'] == name
            ],
        )

    def save(self) -> None:
        '''Update the source tree config.'''
        self.__settings.dump(writable=True)
