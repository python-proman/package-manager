# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Interact with package repository to manage packages.'''

from lxml import html
import hashin
import io
import json
import os
import sys
import shutil
import urllib3

http = urllib3.PoolManager()
INDEX_URL = 'https://pypi.org/'


def _get_package_data(package):
    '''Get package metadata.'''
    rsp = http.request('GET', INDEX_URL + "pypi/{}/json".format(package))
    return json.loads(rsp.data.decode('utf-8'))


def _lookup_hashes(
    package,
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
        package=package,
        version=version,
        algorithm=hash_algorithm,
        python_versions=python_versions,
        verbose=False,
        include_prereleases=include_prereleases,
        lookup_memory=lookup_memory,
        index_url=index_url,
    )
    return package_hashes


def get_package_info(package, section=None):
    '''Get package information.'''
    rst = _get_package_data(package)
    if section:
        return rst[section]
    else:
        return rst


def download_package(package, dest='.', digests=[]):
    '''Execute package download.'''
    rst = _get_package_data(package)
    pkg = next(
        (p for p in rst['urls'] if p['packagetype'] == 'bdist_wheel'),
        (p for p in rst['urls'] if p['packagetype'] == 'sdist')
    )
    filepath = os.path.join(dest, pkg['filename'])
    with http.request('GET', pkg['url'], preload_content=False) as rsp:
        with open(filepath, 'wb') as f:
            shutil.copyfileobj(rsp, f)


def install_package(package: str, version: str = None):
    '''Execute package install.'''
    pass


def uninstall_package(package: str):
    '''Execute package uninstall.'''
    pass


def search(package: str, index_url: str = INDEX_URL):
    '''Search PyPI for packages.'''
    packages = []
    with http.request('GET', index_url + 'simple', preload_content=False) as rsp:
        tree = html.fromstring(rsp.data)
        packages = [p for p in tree.xpath('//a/text()') if package in p]
    return packages
