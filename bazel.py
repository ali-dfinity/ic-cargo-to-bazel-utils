#!/usr/bin/python3
import re


NAME = re.compile('\s+name = "(.+)"')
CRATE_NAME = re.compile('\s+crate_name = "(.+)"')
CRATE = re.compile('\s+crate = "(.+)"')


def loads(text):
    lines = text.split('\n')

    result = []
    entry = {}
    for line in lines:
        if line == 'rust_library(':
            entry['rule'] = 'rust_library'
            continue

        if line == 'rust_binary(':
            entry['rule'] = 'rust_binary'
            continue

        if line == 'rust_test(':
            entry['rule'] = 'rust_test'
            continue

        if line == 'rust_test_suite(':
            entry['rule'] = 'rust_test_suite'
            continue

        if match := NAME.match(line):
            entry['name'] = match.group(1)
            continue

        if match := CRATE_NAME.match(line):
            entry['crate_name'] = match.group(1)
            continue

        if match := CRATE.match(line):
            entry['crate'] = match.group(1)
            continue

        if line == ')':
            if entry.get('rule') in ['rust_library', 'rust_binary', 'rust_test', 'rust_test_suite']:
                result.append(entry)

            entry = {}
            continue

    return result


def is_bazelized_bin_or_lib(package_name, data):
    crate_name = package_name.replace('-', '_')

    binaries_or_libs = [
        x for x in data if x.get('rule') in ['rust_library', 'rust_binary']
    ]
    for x in binaries_or_libs:
        if crate_name in [x.get('name'), x.get('crate_name')]:
            return True
    return False


def is_bazelized_test(package_name, data):
    crate_name = package_name.replace('-', '_')

    binaries_or_libs = [
        x for x in data if x.get('rule') in ['rust_library', 'rust_binary']
    ]
    tests_or_suites = [
        x for x in data if x.get('rule') in ['rust_test', 'rust_test_suite']
    ]
    for test in tests_or_suites:
        test_crate = test.get('crate')
        if test_crate is None:
            continue
        test_crate = test_crate.replace(':', '')
        for bin in binaries_or_libs:
            if test_crate == bin.get('name') and crate_name in [bin.get('name'), bin.get('crate_name')]:
                return True

    return False