# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
'''Simple package manager for Python.'''

from argufy import Parser

from . import cli


def main() -> None:
    '''Provide main function for CLI.'''
    parser = Parser()
    parser.add_commands(cli)
    parser.dispatch()


if __name__ == '__main__':
    main()
