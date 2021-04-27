# type: ignore
import os

from distlib.locators import locate

from proman_pkgmgr.config import Config
from proman_pkgmgr.source_tree import SourceTreeManager

pyproject_file = os.path.join(os.path.dirname(__file__), 'pyproject.toml')
pyproject_config = Config(filepath=pyproject_file, writable=True)
package = locate('urllib3==1.20.0')
update = locate('urllib3==1.25.0')


def test_add_dependency():
    src = SourceTreeManager(pyproject_config)
    src.add_dependency(package, dev=False)
    dep = src.retrieve_dependency(package.name, dev=False)
    assert package.name == list(dep.keys())[0]


def test_remove_dependency():
    src = SourceTreeManager(pyproject_config)
    src.add_dependency(package, dev=False)
    src.remove_dependency(package.name)
    dep = src.retrieve_dependency(package.name, dev=False)
    assert dep == {}


def test_update_dependency():
    src = SourceTreeManager(pyproject_config)
    src.add_dependency(package, dev=False)
    dep = src.retrieve_dependency(package.name, dev=False)
    for pkg, ver in dep.items():
        assert pkg == package.name
        assert ver == package.version

    src.update_dependency(update)
    dep = src.retrieve_dependency(update.name, dev=False)
    for pkg, ver in dep.items():
        assert pkg == update.name
        assert ver == update.version
