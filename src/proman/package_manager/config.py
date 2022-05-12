# SPDX-FileCopyrightText: © 2020-2022 Jesse Johnson <jpj6652@gmail.com>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Provide configuration for package management."""

import os
# from . import exception

INDEX_URL = 'https://pypi.org'
VENV_PATH = os.getenv('VIRTUAL_ENV', None)
PATHS = [VENV_PATH] if VENV_PATH else []

# TODO check VCS for paths
base_dir = os.getcwd()
pyproject_path = os.path.join(base_dir, 'pyproject.toml')
lock_path = os.path.join(base_dir, 'proman-lock.json')
pypackages_dir = os.path.join(base_dir, '__pypackages__')
