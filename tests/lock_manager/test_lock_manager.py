# type: ignore
import os

from proman_pkgmgr.config import Config
from proman_pkgmgr.source_tree import LockManager

lock_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'proman.json'
)
lock_config = Config(filepath=lock_file, writable=True)
package = 'urllib3'


def test_no_lock():
    lockfile = LockManager(lock_config)
    dep = lockfile.retrieve_lock(package, dev=False)
    assert dep == {}


def test_add_lock():
    lockfile = LockManager(lock_config)
    lockfile.add_lock(package, version='1.20', dev=False)
    dep = lockfile.retrieve_lock(package, dev=False)
    assert package == dep['package']


def test_remove_lock():
    lockfile = LockManager(lock_config)
    lockfile.add_lock(package, version=None, dev=False)
    lockfile.remove_lock(package)
    dep = lockfile.retrieve_lock(package, dev=False)
    assert dep == {}


def test_update_lock():
    lockfile = LockManager(lock_config)
    lockfile.add_lock(package, version='1.21.1', dev=False)
    dep = lockfile.retrieve_lock(package, dev=False)
    assert dep['package'] == 'urllib3'
    assert dep['version'] == '1.21.1'

    lockfile.update_lock(package, version='1.25.1')
    dep = lockfile.retrieve_lock(package, dev=False)
    with open(lock_file, 'r') as f:
        print(f.read())
    assert dep['package'] == 'urllib3'
    assert dep['version'] == '1.25.1'
