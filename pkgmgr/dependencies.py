# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Provide dependency management.'''

from semver import Version
from semver import VersionRange
from semver import parse_constraint

from mixology.constraint import Constraint
from mixology.package_source import PackageSource as BasePackageSource
from mixology.range import Range
from mixology.union import Union


class Dependency:

    def __init__(self, name, constraint):  # type: (str, str) -> None
        self.name = name
        self.constraint = parse_constraint(constraint)
        self.pretty_constraint = constraint

    def __str__(self):  # type: () -> str
        return self.pretty_constraint


class PackageSource(BasePackageSource):

    def __init__(self):  # type: () -> None
        self._root_version = Version.parse("0.0.0")
        self._root_dependencies = []
        self._packages = {}

        super(PackageSource, self).__init__()

    @property
    def root_version(self):
        return self._root_version

    def add(
        self, name, version, deps=None
    ):  # type: (str, str, Optional[Dict[str, str]]) -> None
        if deps is None:
            deps = {}

        version = Version.parse(version)
        if name not in self._packages:
            self._packages[name] = {}

        if version in self._packages[name]:
            raise ValueError("{} ({}) already exists".format(name, version))

        dependencies = []
        for dep_name, spec in deps.items():
            dependencies.append(Dependency(dep_name, spec))

        self._packages[name][version] = dependencies

    def root_dep(self, name, constraint):  # type: (str, str) -> None
        self._root_dependencies.append(Dependency(name, constraint))

    def _versions_for(
        self, package, constraint=None
    ):  # type: (Hashable, Any) -> List[Hashable]
        if package not in self._packages:
            return []

        versions = []
        for version in self._packages[package].keys():
            if not constraint or constraint.allows_any(
                Range(version, version, True, True)
            ):
                versions.append(version)

        return sorted(versions, reverse=True)

    def dependencies_for(self, package, version):  # type: (Hashable, Any) -> List[Any]
        if package == self.root:
            return self._root_dependencies

        return self._packages[package][version]

    def convert_dependency(self, dependency):  # type: (Dependency) -> Constraint
        if isinstance(dependency.constraint, VersionRange):
            constraint = Range(
                dependency.constraint.min,
                dependency.constraint.max,
                dependency.constraint.include_min,
                dependency.constraint.include_max,
                dependency.pretty_constraint,
            )
        else:
            # VersionUnion
            ranges = [
                Range(
                    range.min,
                    range.max,
                    range.include_min,
                    range.include_max,
                    str(range),
                )
                for range in dependency.constraint.ranges
            ]
            constraint = Union.of(ranges)

        return Constraint(dependency.name, constraint)
