# type: ignore
import os

from proman_pkgmgr.config import LockManager

settings_path = os.path.dirname(os.path.realpath(__file__))
lock_file = settings_path + '/proman.json'
package = 'urllib3'


def test_no_lock():
    lockfile = LockManager(lock_path=lock_file)
    print(lockfile)
    dep = lockfile.retrieve_lock(package, dev=False)
    assert dep == {}


def test_add_lock():
    lockfile = LockManager(lock_path=lock_file)
    lockfile.add_lock(package, version='1.20', dev=False)
    dep = lockfile.retrieve_lock(package, dev=False)
    assert package == dep['package']


def test_remove_lock():
    lockfile = LockManager(lock_path=lock_file)
    lockfile.add_lock(package, version=None, dev=False)
    lockfile.remove_lock(package)
    dep = lockfile.retrieve_lock(package, dev=False)
    assert dep == {}


def test_update_lock():
    lockfile = LockManager(lock_path=lock_file)
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
