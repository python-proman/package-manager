'''Simple package manager for Python.'''
# -*- coding: utf-8 -*-

from typing import List
import logging

__author__ = 'Jesse P. Johnson'
__title__ = 'proman-packaging'
__version__ = '0.1.1-dev3'
__license__ = 'Apache-2.0'
__all__: List[str] = []

logging.getLogger(__name__).addHandler(logging.NullHandler())
