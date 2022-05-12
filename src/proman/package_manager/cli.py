# SPDX-FileCopyrightText: © 2020-2022 Jesse Johnson <jpj6652@gmail.com>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Arguments for inspection based CLI parser."""

import json
import logging
import sys
from typing import Any, Optional

from . import (
    local_distribution as _local_distribution,
    get_package_manager as _get_package_manager,
)

log_level: Optional[str] = None
_log = logging.getLogger(__name__)
_package_manager = _get_package_manager()


def config() -> None:
    """Manage distributions and global configuration."""
    pass


# def init(name: str) -> None:
#     """Initialize a new project."""
#     if source_tree_cfg and not os.path.isfile(source_tree_cfg.filepath):
#         source_tree_cfg['project'] = {
#             'name': name,
#             'description': 'Description for the project',
#             'version': '0.1.0',
#             'authors': ['Jesse P. Johnson'],
#             'dependencies': {},
#             'dev-dependencies': {}
#         }
#         # source_tree_cfg['build-system'] = {
#         #     'requires': ["build"],
#         #     'build-backend': 'build.api:main'
#         # }
#         source_tree_cfg.dump(writable=True)
#     else:
#         print('project is already initialized')


def info(name: str, output: str = None) -> None:
    """Get package info."""
    info = _package_manager.info(name)
    print(json.dumps(info, indent=2))


def download(name: str, dest: str = '.') -> None:
    """Download packages."""
    _package_manager.download(name, dest)


def install(*packages: str, **options: Any) -> None:
    """Install package(s) and dependencies.

    Parameters
    ----------
    name: str
        name of package to be installed
    dev: bool
        add package as a development dependency
    python: str
        version of Python allowed
    prerelease: bool
        allow prerelease version of package
    optional: bool
        optional package that is not required
    platform: str
        restrict package to specific platform

    """
    options['log_level'] = log_level
    _package_manager.install(*packages, **options)


def uninstall(*packages: str, **options: Any) -> None:
    """Uninstall package(s) and dependencies.

    Parameters
    ----------
    name: str
        name of package(s) to be uninstalled

    """
    options['log_level'] = log_level
    _package_manager.uninstall(*packages, **options)


def update(*packages: str, **options: Any) -> None:
    """Update package(s) and dependencies.

    Parameters
    ----------
    name: str
        name of package to be installed
    force: bool
        force changes

    """
    options['log_level'] = log_level
    _package_manager.update(*packages, **options)


def list(versions: bool = True) -> None:
    """List installed packages."""
    if versions:
        for k in _local_distribution.packages:
            print(k.name.ljust(25), k.version.ljust(15), file=sys.stdout)
    else:
        print('\n'.join(_local_distribution.package_names), file=sys.stdout)


def search(
    name: str,
    version: Optional[str] = None,
    stable_version: Optional[str] = None,
    author: Optional[str] = None,
    author_email: Optional[str] = None,
    maintainer: Optional[str] = None,
    maintainer_email: Optional[str] = None,
    home_page: Optional[str] = None,
    terms: Optional[str] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    keywords: Optional[str] = None,
    platform: Optional[str] = None,
    download_url: Optional[str] = None,
    classifiers: Optional[str] = None,
    project_url: Optional[str] = None,
    docs_url: Optional[str] = None,
    operation: Optional[str] = None,
) -> None:
    """Search PyPI for packages."""
    packages = _package_manager.search(
        query={
            'name': name,
            'version': version,
            'stable_version': stable_version,
            'author': author,
            'author_email': author_email,
            'maintainer': maintainer,
            'maintainer_email': maintainer_email,
            'home_page': home_page,
            'license': terms,
            'summary': summary,
            'description': description,
            'keywords': keywords,
            'platform': platform,
            'download_url': download_url,
            'classifiers': classifiers,
            'project_url': project_url,
            'docs_url': docs_url,
        },
        operation=operation,
    )
    for package in packages:
        print(
            package['name'].ljust(25),  # type: ignore
            package['version'].ljust(15),  # type: ignore
            package['summary'],  # type: ignore
            file=sys.stdout,
        )


# def build() -> None:
#     """Build wheels from your requirements."""
#     pass
