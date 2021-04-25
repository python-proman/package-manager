# type: ignore
import os

from proman_pkgmgr.config import Config
from proman_pkgmgr.source_tree import SourceTreeManager

pyproject_file = os.path.join(os.path.dirname(__file__), 'pyproject.toml')
pyproject_config = Config(filepath=pyproject_file, writable=True)
package = 'urllib3'


def test_add_dependency():
    src = SourceTreeManager(pyproject_config)
    src.add_dependency(package, version='1.20.0', dev=False)
    dep = src.retrieve_dependency(package, dev=False)
    assert package == list(dep.keys())[0]


def test_remove_dependency():
    src = SourceTreeManager(pyproject_config)
    src.add_dependency(package, version=None, dev=False)
    src.remove_dependency(package)
    dep = src.retrieve_dependency(package, dev=False)
    assert dep == {}


def test_update_dependency():
    src = SourceTreeManager(pyproject_config)
    src.add_dependency(package, version='1.20.0', dev=False)
    dep = src.retrieve_dependency(package, dev=False)
    for pkg, ver in dep.items():
        assert pkg == 'urllib3'
        assert ver == '1.20.0'

    src.update_dependency(package, version='1.25.0')
    dep = src.retrieve_dependency(package, dev=False)
    for pkg, ver in dep.items():
        assert pkg == 'urllib3'
        assert ver == '1.25.0'
