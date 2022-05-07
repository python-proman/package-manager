# SPDX-FileCopyrightText: © 2020-2022 Jesse Johnson <jpj6652@gmail.com>
# SPDX-License-Identifier: LGPL-3.0-or-later

from proman.dependencies import __version__


def test_version() -> None:
    assert __version__ == '0.1.1.dev4'
