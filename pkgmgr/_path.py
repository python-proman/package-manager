# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Manage local installed packages.'''

import os
import sys


def create_pypackages_dir(dir: str = os.getcwd()) -> str:
    '''Create base directory.'''
    dist_dir = os.path.join(
        dir,
        '__pypackages__',
        f"{sys.version_info.major}.{sys.version_info.minor}",
    )
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
    return dist_dir


def create_distribution_dir() -> None:
    '''Create pypackages directory.'''
    dist_dir = create_pypackages_dir()
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
