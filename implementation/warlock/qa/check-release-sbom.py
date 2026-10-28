#!/usr/bin/env python3
"""Independent negative checks for the delivery-005 inventory boundary.

Synthetic dispositions exercise mechanics only; they are not license approvals.
Run through the protected CPU launcher.
"""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'window-integration-qa'))
from qa_launch import require_qa_scope

spec = importlib.util.spec_from_file_location('release_compliance', REPO / 'implementation/warlock/adapter/release_compliance.py')
compliance = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compliance)
sys.path.insert(0, str(REPO / 'implementation/warlock/adapter'))
import release_builder


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    require_qa_scope()
    with tempfile.TemporaryDirectory(prefix='warlock-sbom-review-') as tmp:
        root = Path(tmp)
        source = root / 'source'
        candidate = source / 'implementation/warlock'
        payload = root / 'package'
        candidate.mkdir(parents=True)
        payload.mkdir()
        (source / 'origin').write_bytes(b'fixture origin\n')
        (candidate / 'notice.txt').write_bytes(b'fixture notice\n')
        (payload / 'notice.txt').write_bytes(b'fixture notice\n')
        (payload / 'artifact').write_bytes(b'fixture artifact\n')
        (payload / 'alias').symlink_to('artifact')
        provenance = [{'path': 'origin', 'sha256': digest(b'fixture origin\n')}]
        notice = [{'path': 'notice.txt', 'sha256': digest(b'fixture notice\n')}]
        common = {'provenance': provenance, 'notices': notice,
                  'disposition': {'status': 'reviewed', 'evidence': 'Synthetic test assertion only'}}
        components = [dict(common, id=category, category=category, scope='build', files=[])
                      for category in ('compiler', 'package', 'host', 'native-library')]
        components.append(dict(common, id='asset', category='asset', scope='shipped',
            contains=['compiler', 'package', 'host', 'native-library'], files=[
                {'path': 'artifact', 'type': 'file', 'sha256': digest(b'fixture artifact\n')},
                {'path': 'notice.txt', 'type': 'file', 'sha256': digest(b'fixture notice\n')},
                {'path': 'alias', 'type': 'symlink', 'target': 'artifact'}]))
        catalog = root / 'catalog.json'
        def check(rows):
            catalog.write_text(json.dumps({'schema': 1, 'components': rows}))
            return compliance.review(payload, [catalog], source)
        def reject(name, rows, fragment):
            result = check(rows)
            assert not result['ok'] and any(fragment in e for e in result['errors']), (name, result)
            print('PASS ' + name)
        baseline = check(components)
        assert baseline['ok'], baseline
        assert baseline == check(copy.deepcopy(components))
        print('PASS deterministic baseline')
        (payload / 'unaccounted').write_bytes(b'extra')
        reject('unaccounted shipped file', components, 'unaccounted')
        (payload / 'unaccounted').unlink()
        changed = copy.deepcopy(components)
        changed[-1]['files'].append(copy.deepcopy(changed[-1]['files'][0]))
        reject('duplicate mapping', changed, 'duplicate owner')
        (payload / 'notice.txt').write_bytes(b'changed')
        reject('changed notice', components, 'notice absent or changed')
        (payload / 'notice.txt').write_bytes(b'fixture notice\n')
        changed = copy.deepcopy(components)
        changed[0]['disposition']['status'] = 'unknown'
        reject('unknown review', changed, 'disposition incomplete')
        (payload / 'other').write_bytes(b'fixture artifact\n')
        (payload / 'alias').unlink()
        (payload / 'alias').symlink_to('other')
        reject('same-content symlink retarget', components, 'identity mismatch')
        (payload / 'alias').unlink()
        (payload / 'alias').symlink_to('../origin')
        reject('escaping symlink', components, 'payload entry alias')
        (payload / 'alias').unlink()
        (payload / 'other').unlink()
        (payload / 'alias').symlink_to('artifact')
        changed = copy.deepcopy(components)
        changed[-1]['files'][0]['path'] = '../artifact'
        reject('unsafe mapped path', changed, 'invalid file mapping')
        changed = copy.deepcopy(components)
        changed[0]['notices'] = []
        reject('unreviewed notice applicability', changed, 'notice')
        changed = copy.deepcopy(components)
        changed.append(dict(common, id='orphan', category='asset', scope='shipped', files=[]))
        reject('disconnected shipped attribution', changed, 'shipped')
        changed = copy.deepcopy(components)
        changed.extend([dict(common, id='cycle-a', category='asset', scope='shipped', files=[], contains=['cycle-b']),
                        dict(common, id='cycle-b', category='asset', scope='shipped', files=[], contains=['cycle-a'])])
        reject('isolated zero-file cycle', changed, 'disconnected shipped component')
        for field, value, fragment in [('category', [], 'invalid category'),
                                       ('contains', [{}], 'invalid contains'),
                                       ('contains', ['missing-component'], 'unknown contained component')]:
            changed = copy.deepcopy(components)
            changed[-1][field] = value
            reject('malformed ' + field + ' ' + str(value), changed, fragment)
        def failed_walk(path, *, followlinks, onerror):
            onerror(PermissionError('synthetic traversal failure'))
            return iter(())
        with patch.object(compliance.os, 'walk', failed_walk):
            reject('inventory traversal error', components, 'payload traversal failed')
        (candidate / 'notice.txt').write_bytes(b'changed source')
        reject('changed source notice', components, 'notices evidence invalid')
        (candidate / 'notice.txt').write_bytes(b'fixture notice\n')
        catalog.write_text('{"schema":1,"schema":1,"components":[]}')
        result = compliance.review(payload, [catalog], source)
        assert not result['ok'] and any('catalog' in e for e in result['errors']), result
        print('PASS duplicate JSON keys')
        assert check(components)['ok']
        print('PASS restoration')
        # Independently exercise the builder's actual archive audit with a
        # transport fixture, including a duplicate entry hidden by a dict.
        package_manifest = {'files': {
            'artifact': {'sha256': digest(b'fixture artifact\n'), 'symlink': None},
            'notice.txt': {'sha256': digest(b'fixture notice\n'), 'symlink': None},
            'alias': {'sha256': digest(b'fixture artifact\n'), 'symlink': 'artifact'}}}
        (payload / 'MANIFEST.json').write_text(json.dumps(package_manifest))
        archive = root / 'fixture.tar'
        def make_archive(skip=None, duplicate=False):
            with tarfile.open(archive, 'w') as stream:
                for path in sorted(payload.rglob('*')):
                    if path.name != skip:
                        stream.add(path, arcname='warlock/' + path.relative_to(payload).as_posix(), recursive=False)
                if duplicate:
                    stream.add(payload / 'artifact', arcname='warlock/artifact')
        make_archive()
        release_builder.audit_archive(archive, payload, package_manifest)
        print('PASS archive matches package')
        for name, options in [('archive missing file', {'skip': 'artifact'}),
                              ('archive duplicate member', {'duplicate': True})]:
            make_archive(**options)
            try:
                release_builder.audit_archive(archive, payload, package_manifest)
            except release_builder.ChangedInput:
                print('PASS ' + name)
            else:
                raise AssertionError(name + ' was accepted')
        with tarfile.open(archive, 'w') as stream:
            for path in sorted(payload.rglob('*')):
                if path.name == 'artifact':
                    member = tarfile.TarInfo('warlock/artifact')
                    member.type = tarfile.DIRTYPE
                    stream.addfile(member)
                else:
                    stream.add(path, arcname='warlock/' + path.relative_to(payload).as_posix(), recursive=False)
        try:
            release_builder.audit_archive(archive, payload, package_manifest)
        except release_builder.ChangedInput:
            print('PASS archive member type mismatch')
        else:
            raise AssertionError('archive type mismatch was accepted')
        make_archive()
        (payload / 'artifact').write_bytes(b'altered')
        try:
            release_builder.audit_archive(archive, payload, package_manifest)
        except release_builder.ChangedInput:
            print('PASS archive/package content mismatch')
        else:
            raise AssertionError('changed package was accepted')
    catalogs = [REPO / 'implementation/warlock/release/language-components.json',
                REPO / 'implementation/warlock/release/native-components.json']
    with tempfile.TemporaryDirectory(prefix='warlock-catalog-review-') as empty:
        actual = compliance.review(Path(empty), catalogs, REPO)
        assert not actual['ok'] and any('redistribution disposition incomplete' in e for e in actual['errors']), actual
        assert actual['components'] and any(c['disposition']['status'] == 'unknown' for c in actual['components'])
        print('PASS current catalogs retain unknown dispositions and block review')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
