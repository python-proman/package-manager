# SPDX-FileCopyrightText: © 2020-2022 Jesse Johnson <jpj6652@gmail.com>
# SPDX-License-Identifier: LGPL-3.0-or-later
"""Provide exceptions."""


class PackageManagerException(Exception):
    """Provide base errors in PackageManager."""


class PackageManagerDriver(PackageManagerException):
    """Provide exception for driver errors."""


class PackageManagerConfig(PackageManagerException):
    """Provide exception for Config errors."""


class PackageManagerSettings(PackageManagerException):
    """Provide exception for Settings errors."""
