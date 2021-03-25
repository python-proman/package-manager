# type: ignore
import json

from semantic_version import Version

config = {'tool': {}}
# table = tomlkit.table()
config['tool'].update(
    {
        'dependencies': [
            {'package': 'test1', 'version': '1.0.0'},
            {'package': 'test2', 'version': '2.0.0'},
        ],
        'dev-dependencies': [
            {'package': 'dev-test1', 'version': '1.0.0'},
            {'package': 'dev-test2', 'version': '2.0.0'},
        ],
    }
)
# print(json.dumps(config, indent=2, sort_keys=True))


def test_add():
    '''Add package test'''
    config['tool']['dependencies'].append({
        'package': 'test3', 'version': '3.0.0'
    })
    print(json.dumps(config, indent=2, sort_keys=True))


def test_read():
    '''Retrieve package test'''
    package_name = 'test2'
    package_instance = [
        x
        for x in config['tool']['dependencies']
        if (x['package'] == package_name)
    ][0]
    print('This is a package: ' + str(package_instance))


def test_check():
    '''Check if package in store'''
    check = any('test2' in p['package'] for p in config['tool']['dependencies'])
    print('Check if test2 is in store: ' + str(check))


def test_remove():
    '''Remove package test'''
    config['tool']['dependencies'] = [
        x
        for x in config['tool']['dependencies']
        if not (x.get('package') == 'test3')
    ]
    print(json.dumps(config, indent=2, sort_keys=True))


def test_upgrade():
    '''Upgrade package test'''
    update = {'package': 'test2', 'version': '4.0.0'}
    package = [p for p in config['tool']['dependencies']][0]

    if Version(update['version']) > Version(package['version']):
        print('This is our version: ' + update['version'])
        config['tool']['dependencies'] = [
            x
            for x in config['tool']['dependencies']
            if not (x.get('package') == update['package'])
        ]
        config['tool']['dependencies'].append(update)
    else:
        print('Not updated')
    print(json.dumps(config, indent=2, sort_keys=True))
