# type: ignore
import os

from pkgmgr.config import SourceTreeManager

settings_path = os.path.dirname(__file__)
package_file = f"{settings_path}/pyproject.toml"
package = 'urllib3'


def test_add_dependency():
    src = SourceTreeManager(config_path=package_file)
    src.add_dependency(package, semver='1.20.0', dev=False)
    dep = src.retrieve_dependency(package, dev=False)
    assert package == list(dep.keys())[0]


def test_remove_dependency():
    src = SourceTreeManager(config_path=package_file)
    src.add_dependency(package, semver=None, dev=False)
    src.remove_dependency(package)
    dep = src.retrieve_dependency(package, dev=False)
    assert dep == {}


def test_update_dependency():
    src = SourceTreeManager(config_path=package_file)
    src.add_dependency(package, semver='1.20.0', dev=False)
    dep = src.retrieve_dependency(package, dev=False)
    for pkg, ver in dep.items():
        assert pkg == 'urllib3'
        assert ver == '1.20.0'

    src.update_dependency(package, semver='1.25.0')
    dep = src.retrieve_dependency(package, dev=False)
    for pkg, ver in dep.items():
        assert pkg == 'urllib3'
        assert ver == '1.25.0'
