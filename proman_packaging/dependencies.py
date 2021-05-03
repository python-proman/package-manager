# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Resolve package dependencies.'''

from typing import List

from distlib.database import Distribution
# from distlib.index import PackageIndex
# from distlib.locators import locate
# from distlib.scripts import ScriptMaker
# from distlib.wheel import Wheel
# from semantic_version import Version

from transitions import Machine

from . import config


class Dependency:
    '''Manage dependencies of a distribution.'''

    states = ['unknown', 'installed', 'uninstalled', 'outdated']

    def __init__(
        self,
        package: Distribution,
        path: List[str] = config.PATHS,
        include_egg: bool = False,
    ) -> None:
        '''Initialize local distribution.'''
        self.__package = package

        self.machine = Machine(
            model=self, states=Dependency.states, initial='uknown'
        )

    @property
    def name(self) -> str:
        '''Get package name.'''
        return self.__package.name
