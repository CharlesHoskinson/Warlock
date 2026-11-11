#!/usr/bin/env python3
"""Read-only planning advice for exact provider/scenario limitations. No authority."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat

SHA = re.compile(r"[0-9a-f]{64}")
REGISTRY = 'plugins/warlock-contributor/references/provider-capabilities.json'
EVIDENCE = {'findings', 'review', 'nativeFailure'}


def _result(status='unknown', reason='No exact qualified limitation is recorded.', evidence=None):
    return {'schema': 1, 'status': status, 'reason': reason, 'evidence': evidence or {},
            'advisoryOnly': True, 'executionAuthorized': False, 'executionPerformed': False,
            'nativeAcceptance': False, 'sourceReady': False}


def _regular(path, limit):
    path = Path(path).absolute()
    if path.resolve(strict=True) != path:
        raise ValueError('File aliases are not evidence')
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
            raise ValueError('Evidence file type or size differs')
        with os.fdopen(os.dup(descriptor), 'rb') as stream:
            body = stream.read(limit + 1)
        after = os.fstat(descriptor)
        current = path.stat()
        stamp = lambda value: (value.st_dev, value.st_ino, value.st_size,
                               value.st_mtime_ns, value.st_ctime_ns)
        if len(body) > limit or stamp(before) != stamp(after) or stamp(after) != stamp(current):
            raise ValueError('Evidence changed during observation')
        return body
    finally:
        os.close(descriptor)


def _relative(root, name):
    if not isinstance(name, str):
        raise ValueError('Evidence path must be relative')
    relative = PurePosixPath(name)
    if relative.is_absolute() or '..' in relative.parts or str(relative) != name or not relative.parts:
        raise ValueError('Evidence path must be canonical and relative')
    return Path(root).absolute() / name


def assess(root, registry, provider_sha256, requirement, scenario):
    """A supplied digest is a lookup key, not a live process or authorization proof."""
    try:
        if not isinstance(provider_sha256, str) or not SHA.fullmatch(provider_sha256):
            return _result(reason='Provider SHA256 is unknown or malformed.')
        if not isinstance(requirement, str) or not isinstance(scenario, str):
            return _result(reason='Original requirement/scenario identity is missing.')
        if not isinstance(registry, dict) or set(registry) != {'schema', 'entries'}:
            return _result(reason='Registry shape is unknown.')
        if type(registry['schema']) is not int or registry['schema'] != 1:
            return _result(reason='Registry schema is unknown.')
        rows = registry['entries']
        if not isinstance(rows, list) or len(rows) > 256:
            return _result(reason='Registry entries are invalid or exceed the advisory bound.')
        keys = set()
        match = None
        for row in rows:
            if not isinstance(row, dict) or set(row) != {
                    'providerSha256', 'requirement', 'scenario', 'status', 'reason', 'evidence'}:
                return _result(reason='Registry entry is malformed.')
            if (not isinstance(row['providerSha256'], str) or not SHA.fullmatch(row['providerSha256'])
                    or any(not isinstance(row[name], str) or not row[name]
                           for name in ('requirement', 'scenario', 'reason'))
                    or row['status'] != 'unsupported'):
                return _result(reason='Registry cannot establish supported behavior.')
            key = (row['providerSha256'], row['requirement'], row['scenario'])
            if key in keys:
                return _result(reason='Registry identity is ambiguous.')
            keys.add(key)
            if key == (provider_sha256, requirement, scenario):
                match = row
        if match is None:
            return _result()
        evidence = match['evidence']
        if not isinstance(evidence, dict) or set(evidence) != EVIDENCE:
            return _result(reason='Limitation evidence is incomplete.')
        checked = {}
        for role in sorted(EVIDENCE):
            reference = evidence[role]
            if (not isinstance(reference, dict) or set(reference) != {'path', 'sha256'}
                    or not isinstance(reference['sha256'], str)
                    or not SHA.fullmatch(reference['sha256'])):
                return _result(reason='Limitation evidence reference is malformed.')
            body = _regular(_relative(root, reference['path']), 8 * 1024 * 1024)
            if hashlib.sha256(body).hexdigest() != reference['sha256']:
                return _result(reason='Limitation evidence digest differs.')
            checked[role] = dict(reference)
        return _result('unsupported', match['reason'], checked)
    except (OSError, ValueError, TypeError):
        return _result(reason='Limitation evidence is unavailable or changed.')


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON field')
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--requirement', required=True)
    parser.add_argument('--scenario', required=True)
    args = parser.parse_args()
    try:
        registry = json.loads(_regular(_relative(args.root, REGISTRY), 1024 * 1024),
                              object_pairs_hook=_unique)
        digest = hashlib.sha256(_regular(args.binary, 128 * 1024 * 1024)).hexdigest()
        result = assess(args.root, registry, digest, args.requirement, args.scenario)
        result['providerSha256'] = digest
    except (OSError, ValueError, TypeError):
        result = _result(reason='Provider binary or registry could not be read consistently.')
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
