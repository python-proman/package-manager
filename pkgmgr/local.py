# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Manage local installed packages.'''

import os
import sys
from importlib_metadata import metadata
import hashin
import pkg_resources


def _create_pypackages_path(dir: str = os.getcwd()) -> None:
    install_dir = os.path.join(
        dir,
        '__pypackages__',
        'lib',
        f"{sys.version_info.major}.{sys.version_info.minor}",
    )
    if not os.path.exists(install_dir):
        os.makedirs(install_dir)


def freeze():
    '''Output installed packages in requirements format.'''
    print([i for i in pkg_resources.working_set])
    hashin.run(
        ['hashin'],
        'requirements.txt',
        'sha256',
        # args.python_version,
        # verbose=args.verbose,
        # include_prereleases=args.include_prereleases,
        # dry_run=args.dry_run,
        # interactive=args.interactive,
        # synchronous=args.synchronous,
        # index_url=args.index_url
    )


def list_installed_packages():
    '''List installed packages.'''
    return sorted([
        "{k}=={v}".format(k=i.key, v=i.version)
        for i in pkg_resources.working_set
    ])


def show_package_metadata(package: str):
    '''Show information about installed packages.'''
    return metadata(package)


def check():
    '''Verify installed packages have compatible dependencies.'''
    pass


def wheel():
    '''Build wheels from your requirements.'''
    pass


def hash():
    '''Compute hashes of package archives.'''
    pass
