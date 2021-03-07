# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Arguments for inspection based CLI parser.'''

import json
from typing import List, Optional

from . import config as cfg
from . import distributions
from . import package_manager
from .package_manager import PackageManager


__package_manager = PackageManager(force=False, update=False, options={})


def info(name: str) -> None:
    '''Get package info.'''
    info = package_manager.get_package_info(name)
    print(json.dumps(info, indent=2))


def download(name: str, dest: str = '.') -> None:
    '''Download packages.'''
    package_manager.download_package(name, dest)


# def install(name: str, version: str = None):
#     '''Install packages.'''
#     # package_manager.install_package(name, version)


def install(
    name: str,
    dev: bool = False,
    python: Optional[str] = None,
    platform: Optional[str] = None,
    optional: bool = False,
    prerelease: bool = False,
) -> None:
    '''Install package and dependencies.

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

    '''
    if not name.startswith('-'):
        __package_manager.install(
            name, dev, python, platform, optional,  prerelease
        )
    else:
        print('error: not a valid install argument')


def uninstall(name: str) -> None:
    '''Uninstall packages.'''
    pass


def freeze() -> None:
    '''Output installed packages in requirements format.'''
    distributions.freeze()


def list(path: List[str] = []) -> None:
    '''List installed packages.'''
    for p in distributions.get_installed_packages(path):
        # print(p.__dict__)
        print(f"{p.key}=={p.version}")


# def show(name: str) -> None:
#     '''Show information about installed packages.'''
#     for key, val in distributions.show_package_metadata(name).items():
#         print("{k} {v}".format(k=key, v=val))


def check() -> None:
    '''Verify installed packages have compatible dependencies.'''
    pass


def config() -> None:
    '''Manage distributions and global configuration.'''
    print(cfg.get_site_packages_paths())


def search(
    name: str,
    version: Optional[str] = None,
    stable_version: Optional[str] = None,
    author: Optional[str] = None,
    author_email: Optional[str] = None,
    maintainer: Optional[str] = None,
    maintainer_email: Optional[str] = None,
    home_page: Optional[str] = None,
    license: Optional[str] = None,
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
    '''Search PyPI for packages.'''
    packages = package_manager.search(
        query={
            'name': name,
            'version': version,
            'stable_version': stable_version,
            'author': author,
            'author_email': author_email,
            'maintainer': maintainer,
            'maintainer_email': maintainer_email,
            'home_page': home_page,
            'license': license,
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
        )


def wheel() -> None:
    '''Build wheels from your requirements.'''
    pass


def hash(package: str, algorithm: str = 'sha256') -> None:
    '''Compute hashes of package archives.'''
    print(package_manager._lookup_hashes(package))


def completion() -> None:
    '''A helper command used for command completion.'''
    pass
