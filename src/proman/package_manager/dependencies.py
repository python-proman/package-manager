# SPDX-FileCopyrightText: © 2020-2022 Jesse Johnson <jpj6652@gmail.com>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Resolve package dependencies."""

import re
from typing import Any, Dict, Tuple

# from distlib.database import Distribution
# from distlib.index import PackageIndex
from distlib.database import EggInfoDistribution, InstalledDistribution
from distlib.locators import locate

# from distlib.scripts import ScriptMaker
# from distlib.wheel import Wheel
# from packaging.specifiers import SpecifierSet
from proman.common.dependencies import DependencyBase

# from . import config


class Dependency(DependencyBase):
    """Manage dependency of a project."""

    def __init__(
        self,
        sequence: Any,
        **options: Any,
    ) -> None:
        """Initialize dependency."""
        self.__dev = options.get('dev', False)
        self.__python = options.get('python', None)
        self.__platform = options.get('platform', None)
        self.__optional = options.get('optional', False)
        self.__prerelease = options.get('prerelease', False)
        # path: List[str] = config.PATHS,
        # include_egg: bool = False,

        if isinstance(sequence, InstalledDistribution) or isinstance(
            sequence, EggInfoDistribution
        ):
            self._distribution = sequence
        else:
            # TODO: json/rpc does not include run_requires
            # package = self.__locator.locate(sequence)
            self._distribution = locate(
                sequence, prereleases=self.__prerelease
            )

    def __getattr__(self, attr: str) -> Any:
        """Provide proxy for distribution."""
        return getattr(self._distribution, attr)

    @staticmethod
    def __get_specifier(package: str) -> Tuple[str, str]:
        """Get package name and version."""
        regex = '^([a-zA-Z0-9][a-zA-Z0-9._-]*)([<!~=>].*)$'
        package_info = [x for x in re.split(regex, package) if x != '']
        name = package_info[0]
        if len(package_info) == 2:
            version = package_info[1]
        else:
            version = '*'
        return name, version

    @property
    def name(self) -> str:
        """Get name."""
        return self._distribution.name

    @property
    def version(self) -> str:
        """Get version."""
        return self._distribution.version

    @property
    def digests(self) -> Tuple[Dict[str, str]]:
        """Get digests."""
        return self._distribution.digests

    @property
    def url(self) -> str:
        """Get url."""
        return ''
