# SPDX-FileCopyrightText: © 2020-2022 Jesse Johnson <jpj6652@gmail.com>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Manage distribution paths."""

import logging
import os
import site
import sys
from typing import Any, List, Optional

from distlib.database import Distribution, DistributionPath

# from distlib.index import PackageIndex
# from distlib.locators import locate
# from distlib.scripts import ScriptMaker
# from distlib.wheel import Wheel

from . import config

logger = logging.getLogger(__name__)


class DistributionPathMixin(DistributionPath):
    """Provide distribution path tools."""

    @property
    def packages(self) -> List[Distribution]:
        """List installed packages."""
        return [x for x in self.get_distributions()]

    @property
    def package_names(self) -> List[str]:
        """Get packages names."""
        return [x.name for x in self.get_distributions()]

    def get_version(self, name: str) -> Optional[str]:
        """Get version of installed package."""
        return next(
            (v for k, v in self.packages if k == name),
            None,
        )

    def is_installed(self, name: str) -> bool:
        """Check is package is installed."""
        return False if self.get_distribution(name) is None else True


class SystemDistributionPath(DistributionPathMixin):
    """Manage system distributions."""

    def __init__(
        self,
        paths: List[str] = [],
        include_egg: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize local distribution."""
        DistributionPath.__init__(self, paths, include_egg)


class UserDistributionPath(DistributionPathMixin):
    """Manage global distributions."""

    def __init__(
        self,
        paths: List[str] = [],
        include_egg: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize local distribution."""
        if site.USER_SITE:
            paths += [site.USER_SITE]

        DistributionPath.__init__(self, paths, include_egg)


class LocalDistributionPath(DistributionPathMixin):
    """Manage local distributions."""

    def __init__(
        self,
        paths: List[str] = [],
        include_egg: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize local distribution."""
        self.project_name = kwargs.pop('name', os.path.basename(os.getcwd()))
        self.pypackages_dir = kwargs.pop(
            'pypackages_dir', config.pypackages_dir
        )
        self.env_version = (
            f"{str(sys.version_info.major)}.{str(sys.version_info.minor)}"
        )
        self.__dist_dir = os.path.join(self.pypackages_dir, self.env_version)

        DistributionPath.__init__(self, paths, include_egg)

    def create_dist_pth(self) -> None:
        """Create pth file for distibution version."""
        pth_file = os.path.join(
            self.pypackages_dir, f"proman-{self.env_version}.pth"
        )
        if not os.path.exists(pth_file):
            with open(pth_file, 'a+') as f:
                for subpath in ['lib', 'lib64']:
                    path = os.path.join(self.env_version, subpath)
                    f.write(os.linesep)
                    f.write(path)

    def create_pypackages_pth(
        self, site_dir: Optional[str] = site.USER_SITE
    ) -> None:
        """Create pth file for pypackages."""
        if not os.path.exists(self.pypackages_dir):
            os.makedirs(self.pypackages_dir)

        # XXX: need to determine best way to link pypackages
        # for site_packages_dir in site.getusersitepackages():
        if site_dir:
            if os.path.exists(site_dir) and os.path.isdir(site_dir):
                with open(
                    os.path.join(site_dir, f"proman-{self.project_name}.pth"),
                    'w',
                ) as f:
                    f.write(self.pypackages_dir)

    def create_pypackages(self, base_dir: Optional[str] = None) -> None:
        """Create pypackages directory."""
        if not os.path.exists(self.__dist_dir):
            os.makedirs(self.__dist_dir)
        self.paths = {
            'prefix': self.__dist_dir,
            'purelib': os.path.join(self.__dist_dir, 'lib'),
            'platlib': os.path.join(self.__dist_dir, 'lib64'),
            'scripts': os.path.join(self.__dist_dir, 'bin'),
            'headers': os.path.join(self.__dist_dir, 'src'),
            'data': os.path.join(self.__dist_dir, 'share'),
        }
        for k, v in self.paths.items():
            if k != 'prefix':
                os.makedirs(os.path.join(self.__dist_dir, v), exist_ok=True)
        self.create_dist_pth()

    def load_pypackages(self, project_dir: str = os.getcwd()) -> None:
        """Load pypackages into paths."""
        site.addsitedir(self.pypackages_dir)
        site.addsitedir(project_dir)
