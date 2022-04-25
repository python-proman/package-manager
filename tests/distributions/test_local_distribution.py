# type: ignore
import os
import sys

from proman.dependencies.distributions import LocalDistributionPath

package = "urllib3"


def test_packages():
    # paths, include_egg
    path = os.path.join(
        os.path.dirname(__file__),
        "__pypackages__",
        f"{str(sys.version_info.major)}.{str(sys.version_info.minor)}",
        "lib",
    )
    local_dist = LocalDistributionPath([path])
    assert local_dist.packages[0].name == package
    assert local_dist.is_installed(package) is True

    dist = local_dist.get_distribution(package)

    from distlib.locators import DistPathLocator

    dist_path = DistPathLocator(local_dist)
    print(dist_path._get_project(package))
    for x in dist.list_installed_files():
        print(x)


# def test_remove_dependency():
#     local_dist = LocalDistributionPath(pyproject_config)
#     local_dist.add_dependency(package, version=None, dev=False)
#     local_dist.remove_dependency(package)
#     dep = local_dist.get_dependency(package, dev=False)
#     assert dep == {}
#
#
# def test_update_dependency():
#     local_dist = LocalDistributionPath(pyproject_config)
#     local_dist.add_dependency(package, version='1.20.0', dev=False)
#     dep = local_dist.get_dependency(package, dev=False)
#     for pkg, ver in dep.items():
#         assert pkg == 'urllib3'
#         assert ver == '1.20.0'
#
#     local_dist.update_dependency(package, version='1.25.0')
#     dep = local_dist.get_dependency(package, dev=False)
#     for pkg, ver in dep.items():
#         assert pkg == 'urllib3'
#         assert ver == '1.25.0'
