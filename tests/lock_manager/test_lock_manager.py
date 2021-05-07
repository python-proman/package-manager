# type: ignore
import os

from distlib.locators import locate

from proman_packaging.config import Config
from proman_packaging.source_tree import LockManager

lock_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'proman-lock.json'
)
lock_config = Config(filepath=lock_file, writable=True)

pyproject_file = os.path.join(os.path.dirname(__file__), 'pyproject.toml')
pyproject_config = Config(filepath=pyproject_file, writable=True)
package = locate('urllib3==1.20.0')
update = locate('urllib3==1.25.0')


def test_no_lock(fs):
    fs.add_real_file(lock_file, False)
    lockfile = LockManager(lock_config)
    dep = lockfile.get_lock(package)
    assert dep == {}


def test_add_lock(fs):
    fs.add_real_file(lock_file, False)
    lockfile = LockManager(lock_config)
    lockfile.add_lock(package)
    dep = lockfile.get_lock(package.name)
    assert package.name == dep['name']


def test_remove_lock(fs):
    fs.add_real_file(lock_file, False)
    lockfile = LockManager(lock_config)
    lockfile.add_lock(package)
    lockfile.remove_lock(package)
    dep = lockfile.get_lock(package)
    assert dep == {}


def test_update_lock(fs):
    fs.add_real_file(lock_file, False)
    lockfile = LockManager(lock_config)
    lockfile.add_lock(package)
    dep = lockfile.get_lock(package.name)
    assert dep['name'] == package.name
    assert dep['version'] == package.version

    lockfile.update_lock(update)
    dep_up = lockfile.get_lock(update.name)
    assert dep_up['name'] == update.name
    assert dep_up['version'] == update.version
