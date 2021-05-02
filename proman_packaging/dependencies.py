# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Resolve package dependencies.'''

from typing import List

# from distlib.index import PackageIndex
# from distlib.locators import locate
# from distlib.scripts import ScriptMaker
# from distlib.wheel import Wheel
# from semantic_version import Version

from . import config


class DependencyManager:
    '''Manage dependencies of a distribution.'''

    def __init__(
        self,
        path: List[str] = config.PATHS,
        include_egg: bool = False,
    ) -> None:
        '''Initialize local distribution.'''
        pass
