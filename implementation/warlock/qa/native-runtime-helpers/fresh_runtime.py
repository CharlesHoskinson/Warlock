"""Validate a pinned fresh runtime tuple; does not start or load any process.

The caller supplies both trusted hashes out of band. This additive schema never
changes or substitutes historical current-native-pair/current-search-build.
"""
import hashlib
import json
import os
from pathlib import Path
import re

HEX = re.compile(r'^[0-9a-f]{64}$')
MAX_CHECKS = 10000


class InvalidRuntime(ValueError):
    pass


def digest(path):
    try:
        with Path(path).open('rb') as stream:
            return hashlib.file_digest(stream, 'sha256').hexdigest()
    except OSError as exc:
        raise InvalidRuntime('unavailable pinned input: ' + str(path)) from exc


def checked(path, expected):
    if not isinstance(expected, str) or not HEX.fullmatch(expected) or digest(path) != expected:
        raise InvalidRuntime('pinned input changed: ' + str(path))


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidRuntime('duplicate JSON key: ' + key)
        result[key] = value
    return result


def _read_pinned(path, expected):
    # Read exactly the bytes whose hash is checked, preventing parse/re-read races.
    try:
        raw = Path(path).read_bytes()
        if not isinstance(expected, str) or not HEX.fullmatch(expected) or hashlib.sha256(raw).hexdigest() != expected:
            raise InvalidRuntime('pinned manifest changed: ' + str(path))
        data = json.loads(raw, object_pairs_hook=_unique)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InvalidRuntime('invalid pinned manifest: ' + str(path)) from exc
    if not isinstance(data, dict):
        raise InvalidRuntime('manifest must be an object')
    return data


def load(tuple_path, tuple_sha256, preflight_path, preflight_sha256, *, source_base):
    """Return canonical tuple after checking fixed preflight inventory and bindings.

    Inputs must come from an independently reviewed pin, not from the tuple
    being validated. The validation is a snapshot, not a runtime/ABI verdict.
    """
    t = _read_pinned(tuple_path, tuple_sha256)
    p = _read_pinned(preflight_path, preflight_sha256)
    try:
        if (t['schema'] != 1 or t['sourceBase'] != source_base or t['readyForRootReview'] is not True
                or t['nativeAcceptance'] is not False or t['pluginLoaded'] is not False
                or p['schema'] != 1 or p['passed'] is not True or p['nativeAcceptance'] is not False
                or p['pluginLoaded'] is not False or p['errors'] != [] or p['tupleSHA256'] != tuple_sha256):
            raise InvalidRuntime('fresh tuple/preflight status mismatch')
        rows = p['checks']
        if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_CHECKS:
            raise InvalidRuntime('invalid preflight inventory size')
        for row in rows:
            if row['passed'] is not True:
                raise InvalidRuntime('failed preflight check')
            if 'expectedSHA256' in row:
                checked(row['path'], row['expectedSHA256'])
            elif row.get('label') == 'aquamarine soname alias':
                alias = Path(row['path'])
                if not alias.is_symlink() or os.readlink(alias) != row['target']:
                    raise InvalidRuntime('preflight alias changed')
            else:
                raise InvalidRuntime('unknown preflight check')
        for row in t['reports'].values():
            checked(row['path'], row['sha256'])
        slots = t['slots']
        for name in ('core', 'aquamarine', 'authority', 'host'):
            checked(slots[name]['path'], slots[name]['sha256'])
        if slots['authority']['staticClosureOnly'] is not True or slots['authority']['loaded'] is not False:
            raise InvalidRuntime('authority disposition mismatch')
        for name in ('authority', 'host'):
            checked(slots[name]['report']['path'], slots[name]['report']['sha256'])
        aq = slots['aquamarine']; alias = Path(aq['sonameAlias'])
        if (not alias.is_symlink() or os.readlink(alias) != aq['aliasTarget']
                or alias.resolve(strict=True) != Path(aq['path']).resolve(strict=True)):
            raise InvalidRuntime('aquamarine alias changed')
        assets = slots['host']['assets']
        if set(assets) != {'assets/elm.js', 'assets/bar.js', 'assets/popup.js'}:
            raise InvalidRuntime('compiled asset inventory changed')
        for row in assets.values():
            checked(row['path'], row['sha256'])
    except (KeyError, TypeError, AttributeError, OSError, ValueError) as exc:
        if isinstance(exc, InvalidRuntime):
            raise
        raise InvalidRuntime('malformed fresh runtime reference') from exc
    return t
