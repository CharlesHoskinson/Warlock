#!/usr/bin/env python3
"""Deterministic, fail-closed package redistribution inventory.

A reviewed disposition is a recorded assertion, not a legal determination.
The caller owns generated metadata and archive verification after this review.
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat

HASH = re.compile(r'^[0-9a-f]{64}$')
ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*$')
CATEGORIES = {'compiler', 'package', 'host', 'native-library', 'asset'}


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key')
        result[key] = value
    return result


def _path(value):
    if not isinstance(value, str) or not value or '\\' in value or '\x00' in value:
        raise ValueError('invalid relative path')
    p = PurePosixPath(value)
    if p.is_absolute() or str(p) != value or any(x in ('.', '..') for x in value.split('/')):
        raise ValueError('invalid relative path')
    return value


def _inside(root, name):
    path = root / _path(name)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('path escapes root')
    return path


def _digest(path):
    with path.open('rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError('not a regular file')
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def _inventory(root, errors):
    rows = []
    if not root.is_dir() or root.is_symlink():
        errors.append('payload root is unavailable or a symlink')
        return rows
    def walk_error(_error):
        errors.append('payload traversal failed')
    for base, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
        dirs.sort(); files.sort()
        for name in sorted(dirs + files):
            path = Path(base) / name
            rel = path.relative_to(root).as_posix()
            try:
                _path(rel)
                mode = path.lstat().st_mode
                if stat.S_ISLNK(mode):
                    target = os.readlink(path)
                    # Relative link spellings may contain .., but must resolve inside root.
                    if not target or os.path.isabs(target) or '\\' in target or '\x00' in target:
                        raise ValueError('invalid symlink target')
                    resolved = path.resolve(strict=True)
                    if not resolved.is_relative_to(root.resolve()) or not resolved.is_file():
                        raise ValueError('symlink target escapes or is not a file')
                    rows.append({'path': rel, 'type': 'symlink', 'target': target})
                    if name in dirs:
                        dirs.remove(name)
                elif stat.S_ISREG(mode):
                    rows.append({'path': rel, 'type': 'file', 'sha256': _digest(path)})
                elif not stat.S_ISDIR(mode):
                    raise ValueError('unsupported payload entry')
            except (OSError, ValueError, RuntimeError) as exc:
                errors.append('payload entry %s: %s' % (rel, str(exc) if isinstance(exc, ValueError) else 'unavailable'))
    return sorted(rows, key=lambda row: row['path'])


def review(payload_dir, catalog_paths, source_root):
    """Return JSON-ready inventory and blockers, without changing the package.

    Provenance paths are repository-relative; notice paths are candidate- and
    payload-relative. Catalogs supply hashes, not permission or source proof.
    """
    root = Path(source_root)
    payload = Path(payload_dir)
    errors = []
    inventory = _inventory(payload, errors)
    components = []
    for index, catalog in enumerate(catalog_paths):
        try:
            data = json.loads(Path(catalog).read_text(encoding='utf-8'), object_pairs_hook=_unique)
            if not isinstance(data, dict) or set(data) != {'schema', 'components'} or type(data['schema']) is not int or data['schema'] != 1 or not isinstance(data['components'], list):
                raise ValueError('invalid catalog envelope')
            components.extend(data['components'])
        except (OSError, ValueError, UnicodeError, TypeError):
            errors.append('catalog %d: unreadable or invalid' % index)
    seen = set(); owners = {}; categories = set(); references = []; notices = []; graph = {}
    valid_components = []
    for index, c in enumerate(components):
        label = 'component %d' % index
        if not isinstance(c, dict) or not isinstance(c.get('id'), str) or not ID.fullmatch(c['id']):
            errors.append(label + ': invalid id'); continue
        label = 'component ' + c['id']
        if c['id'] in seen:
            errors.append(label + ': duplicate id'); continue
        seen.add(c['id']); valid_components.append(c)
        allowed = {'id', 'scope', 'category', 'provenance', 'notices', 'disposition', 'files', 'contains', 'notes', 'notice_disposition'}
        if set(c) - allowed:
            errors.append(label + ': unknown fields')
        category = c.get('category')
        if not isinstance(category, str) or category not in CATEGORIES | {'other'}:
            errors.append(label + ': invalid category')
        else:
            categories.add(category)
        if c.get('scope') not in ('shipped', 'build'):
            errors.append(label + ': invalid scope')
        disposition = c.get('disposition')
        if not isinstance(disposition, dict) or set(disposition) != {'status', 'evidence'} or disposition.get('status') != 'reviewed' or not isinstance(disposition.get('evidence'), str) or not disposition['evidence'].strip():
            errors.append(label + ': redistribution disposition incomplete')
        for field in ('provenance', 'notices', 'files'):
            if not isinstance(c.get(field), list):
                errors.append(label + ': invalid ' + field)
        provenance = c.get('provenance') if isinstance(c.get('provenance'), list) else []
        if not provenance:
            errors.append(label + ': provenance missing')
        for field, base, entries in [('provenance', root, provenance), ('notices', root / 'implementation/warlock', c.get('notices', []))]:
            if not isinstance(entries, list):
                continue
            for row in entries:
                try:
                    if not isinstance(row, dict) or set(row) != {'path', 'sha256'} or not isinstance(row['sha256'], str) or not HASH.fullmatch(row['sha256']):
                        raise ValueError('invalid evidence')
                    path = _inside(base, row['path'])
                    if _digest(path) != row['sha256']:
                        raise ValueError('hash mismatch')
                    if field == 'notices':
                        notices.append((row['path'], row['sha256'], label))
                except (OSError, ValueError, RuntimeError):
                    errors.append(label + ': ' + field + ' evidence invalid or unavailable')
        if not c.get('notices'):
            nd = c.get('notice_disposition')
            if not isinstance(nd, dict) or set(nd) != {'status', 'evidence'} or nd.get('status') != 'reviewed' or not isinstance(nd.get('evidence'), str) or not nd['evidence'].strip():
                errors.append(label + ': notice applicability review incomplete')
        files = c.get('files') if isinstance(c.get('files'), list) else []
        if c.get('scope') == 'build' and files:
            errors.append(label + ': build component owns payload files')
        for row in files:
            try:
                if not isinstance(row, dict):
                    raise ValueError()
                name = _path(row.get('path'))
                if row.get('type') == 'file':
                    if set(row) != {'path', 'type', 'sha256'} or not isinstance(row['sha256'], str) or not HASH.fullmatch(row['sha256']):
                        raise ValueError()
                elif row.get('type') == 'symlink':
                    if set(row) != {'path', 'type', 'target'} or not isinstance(row['target'], str) or not row['target'] or os.path.isabs(row['target']):
                        raise ValueError()
                else:
                    raise ValueError()
                if name in owners:
                    errors.append('payload mapping ' + name + ': duplicate owner')
                else:
                    owners[name] = row
            except (ValueError, TypeError):
                errors.append(label + ': invalid file mapping')
        contains = c.get('contains', [])
        if not isinstance(contains, list) or any(not isinstance(x, str) or not ID.fullmatch(x) for x in contains) or len(set(contains)) != len(contains):
            errors.append(label + ': invalid contains')
        else:
            references.extend((label, x) for x in contains)
            graph[c['id']] = contains
    for category in sorted(CATEGORIES):
        if category not in categories:
            errors.append('missing component category: ' + category)
    for label, ref in references:
        if ref not in seen:
            errors.append(label + ': unknown contained component ' + ref)
    reachable = {c['id'] for c in valid_components if c.get('scope') == 'shipped' and c.get('files')}
    pending = list(reachable)
    while pending:
        for ref in graph.get(pending.pop(), []):
            if ref in seen and ref not in reachable:
                reachable.add(ref); pending.append(ref)
    for c in valid_components:
        if c.get('scope') == 'shipped' and c['id'] not in reachable:
            errors.append('component ' + c['id'] + ': disconnected shipped component')
    actual = {row['path']: row for row in inventory}
    for name in sorted(set(actual) | set(owners)):
        if name not in owners:
            errors.append('payload entry ' + name + ': unaccounted')
        elif name not in actual:
            errors.append('payload entry ' + name + ': missing')
        elif owners[name] != actual[name]:
            errors.append('payload entry ' + name + ': identity mismatch')
    for name, digest, label in notices:
        if actual.get(name) != {'path': name, 'type': 'file', 'sha256': digest} or name not in owners:
            errors.append(label + ': notice absent or changed in payload')
    def public(value):
        if isinstance(value, str) and (value.startswith('/') or re.search(r'\s/', value)):
            errors.append('catalog contains an absolute path')
            return '[absolute path redacted]'
        if isinstance(value, list):
            return [public(v) for v in value]
        if isinstance(value, dict):
            return {public(k): public(v) for k, v in value.items()}
        return value
    public_components = public(sorted(valid_components, key=lambda c: c['id']))
    return {'schema': 1, 'ok': not errors, 'inventory': inventory,
            'components': public_components, 'errors': sorted(errors)}
