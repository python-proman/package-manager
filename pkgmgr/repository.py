# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Interact with package repository to manage packages.'''

# from lxml import html
# from tempfile import TemporaryDirectory
from typing import Optional
from urllib.parse import urljoin

from distlib.index import PackageIndex
# from distlib.locators import locate
import hashin

# import io
import json
import os
# import sys
# import shutil
import urllib3

from .local import _create_pypackages_path

http = urllib3.PoolManager()
INDEX_URL = 'https://test.pypi.org/'


def _lookup_hashes(
    name,
    version=None,
    hash_algorithm='sha256',
    python_versions=(),
    verbose=False,
    include_prereleases=False,
    lookup_memory={},
    index_url=INDEX_URL
):
    '''Lookup package hash from configuration.'''
    package_hashes = hashin.get_package_hashes(
        package=name,
        version=version,
        algorithm=hash_algorithm,
        python_versions=python_versions,
        verbose=False,
        include_prereleases=include_prereleases,
        lookup_memory=lookup_memory,
        index_url=index_url,
    )
    return package_hashes


def _get_package_data(package):
    '''Get package metadata.'''
    rsp = http.request('GET', urljoin(INDEX_URL, f"pypi/{package}/json"))
    # from pprint import pprint
    # pprint(vars(rsp))
    if rsp.status == 200:
        return json.loads(rsp.data.decode('utf-8'))
    else:
        print('package not found')


def get_package_info(name: str, section: Optional[str] = None):
    '''Get package information.'''
    rst = _get_package_data(name)
    if section:
        return rst[section]
    else:
        return rst


def download_package(name, dest='.', digests=[]):
    '''Execute package download.'''
    rst = _get_package_data(name)
    # TODO create locator
    pkg = next(
        (p for p in rst['urls'] if p['packagetype'] == 'bdist_wheel'),
        (p for p in rst['urls'] if p['packagetype'] == 'sdist')
    )
    index = PackageIndex(url=urljoin(INDEX_URL, 'pypi'))
    # with TemporaryDirectory() as td:
    filepath = os.path.join(dest, pkg['filename'])
    index.download_file(pkg['url'], filepath, digest=None, reporthook=None)


def install_package(name: str, version: str = None):
    '''Execute package install.'''
    # enumerate dependencies
    # reconcile versions
    # check gpg trust
    # download packages
    # check hashes
    # install
    _create_pypackages_path()


def uninstall_package(name: str):
    '''Execute package uninstall.'''
    # clean orphans
    pass


def search(
    query: dict,
    operation: str = None,
    url: str = urljoin(INDEX_URL, 'pypi')
):
    '''Search PyPI for packages.'''
    index = PackageIndex(url=url)
    return index.search({
            k: v
            for k, v in query.items() if v is not None
        },
        operation
    )
    # packages = []
    # with http.request(
    #     'GET',
    #     url + 'simple',
    #     preload_content=False
    # ) as rsp:
    #     tree = html.fromstring(rsp.data)
    #     packages = [p for p in tree.xpath('//a/text()') if name in p]
    # return packages
