# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Provide configuration management for pkgmgr.'''

import os
import site
from typing import Dict, List, Optional

# from semantic_version import Version

from compendium.config_manager import ConfigManager

path = os.getenv('VIRTUAL_ENV', None)
PATHS = [path] if path else []
INDEX_URL = 'https://test.pypi.org/'


def get_site_packages_paths() -> List[str]:
    '''Get installed packages from site.'''
    return site.getsitepackages()


class ProjectSettingsMixin:
    '''Provide common methods for project settings.'''

    @staticmethod
    def dependency_type(dev: bool = False) -> str:
        '''Check if development dependency.'''
        return 'dev-dependencies' if dev else 'dependencies'


class PyPIConfigManager:
    pass


class SourceTreeManager(ProjectSettingsMixin):
    '''Manage source tree configuration file for project.'''

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
