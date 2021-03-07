# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Simple package manager for Python.'''

from . import cli
from argufy import Parser


def main() -> None:
    '''Main function for CLI.'''
    parser = Parser()
    parser.add_commands(cli)
    parser.dispatch()


if __name__ == '__main__':
    '''Ensure execution from CLI.'''
    main()
