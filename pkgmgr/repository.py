# -*- coding: utf-8 -*-
# copyright: (c) 2020 by Jesse Johnson.
# license: Apache 2.0, see LICENSE for more details.
'''Interact with package repository to manage packages.'''

from lxml import html
import io
import json
import os
import shutil
import urllib3

http = urllib3.PoolManager()
repo = 'https://pypi.org/pypi'


def _get_package_data(package):
    '''Get package metadata.'''
    rsp = http.request('GET', repo + "/{}/json".format(package))
    return json.loads(rsp.data.decode('utf-8'))


def get_package_info(package):
    '''Get package information.'''
    rst = _get_package_data(package)
    print(json.dumps(rst['info'], indent=2))


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


def install_package(package: str):
    '''Execute package install.'''
    pass


def uninstall_package(package: str):
    '''Execute package uninstall.'''
    pass


def search(package: str, index: str = repo):
    '''Search PyPI for packages.'''
    packages = []
    with http.request('GET', 'https://pypi.org/simple', preload_content=False) as rsp:
        tree = html.fromstring(rsp.data)
        packages = [p for p in tree.xpath('//a/text()') if package in p]
    print(packages)
