# SPDX-FileCopyrightText: © 2020-2022 Jesse Johnson <jpj6652@gmail.com>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Simple package manager for Python."""

from argufy import Parser

from . import cli


def main() -> None:
    """Provide main function for CLI."""
    parser = Parser(use_module_args=True)
    parser.add_commands(cli)
    parser.dispatch()


if __name__ == '__main__':
    main()
