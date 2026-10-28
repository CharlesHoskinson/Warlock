#!/usr/bin/env python3
"""Controlled correspondence probes; does not qualify a real release."""
import hashlib
import io
import json
import shutil
from pathlib import Path
import sys
import tarfile
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'adapter'))
import release_builder as builder
import release_compliance as compliance


def manifest(root):
    files = {str(p.relative_to(root)): {'sha256': builder.sha(p),
              'symlink': p.readlink().as_posix() if p.is_symlink() else None}
             for p in sorted(root.rglob('*')) if p.is_file() and p.name != 'MANIFEST.json'}
    result = {'files': files}
    (root / 'MANIFEST.json').write_text(json.dumps(result))
    return result


def archive(root, dest, mutation=None):
    with tarfile.open(dest, 'w') as t:
        for p in sorted(root.rglob('*')):
            name = 'warlock/' + str(p.relative_to(root))
            if mutation == 'missing' and p.name == 'data':
                continue
            if mutation == 'type' and p.name == 'data':
                info = tarfile.TarInfo(name); info.type = tarfile.DIRTYPE; t.addfile(info)
            elif mutation == 'content' and p.name == 'data':
                info = tarfile.TarInfo(name); info.size = 3; t.addfile(info, io.BytesIO(b'bad'))
            else:
                t.add(p, arcname=name, recursive=False)
            if mutation == 'duplicate' and p.name == 'data':
                t.add(p, arcname=name, recursive=False)
        if mutation == 'unexpected':
            info = tarfile.TarInfo('warlock/extra'); info.size = 0; t.addfile(info, io.BytesIO())


def rejected(fn, reason=None):
    try:
        fn()
    except (ValueError, builder.ChangedInput) as error:
        assert reason is None or reason in str(error), str(error)
        return
    raise AssertionError('expected rejection')


def main():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td); root = base / 'payload'; root.mkdir()
        (root / 'data').write_bytes(b'abc')
        (root / 'same').write_bytes(b'abc')
        (root / 'alias').symlink_to('data')
        tar = base / 'package.tar'
        m = manifest(root); archive(root, tar); builder.audit_archive(tar, root, m)
        errors = []; rows = compliance._inventory(root, errors)
        assert not errors and any(r == {'path': 'alias', 'type': 'symlink', 'target': 'data'} for r in rows)
        for name in ('../data', 'a//b', '/absolute', 'a\\b'):
            rejected(lambda: compliance._path(name))
        for case in ('duplicate', 'missing', 'unexpected', 'type', 'content'):
            archive(root, tar, case); rejected(lambda: builder.audit_archive(tar, root, m))
        archive(root, tar)
        (root / 'alias').unlink(); (root / 'alias').symlink_to('same')
        rejected(lambda: builder.audit_archive(tar, root, m))
        m = manifest(root); archive(root, tar); builder.audit_archive(tar, root, m)
        (base / 'outside').write_bytes(b'abc')
        (root / 'alias').unlink(); (root / 'alias').symlink_to('../outside')
        errors = []; compliance._inventory(root, errors); assert errors
        rejected(lambda: compliance._inside(root, 'alias'))
        # Even generic audits must refuse matching but unsafe transport.
        m = manifest(root); archive(root, tar)
        rejected(lambda: builder.audit_archive(tar, root, m), 'Unsafe payload inventory')
        (root / 'alias').unlink(); (root / 'alias').symlink_to('data')
        m = manifest(root); archive(root, tar); builder.audit_archive(tar, root, m)
        receipt_cases(base)
        print('PASS: generic archive mutations and escape; reviewed receipt retarget, escape and restore')


def receipt_cases(base):
    candidate = base / 'implementation/warlock'
    (candidate / 'adapter').mkdir(parents=True)
    (candidate / 'release/notices').mkdir(parents=True)
    shutil.copyfile(Path(compliance.__file__), candidate / 'adapter/release_compliance.py')
    notice = candidate / 'release/notices/example.txt'; notice.write_text('fixture notice\n')
    source = base / 'source.txt'; source.write_text('fixture source\n')
    root = base / 'reviewed'; root.mkdir()
    (root / 'data').write_bytes(b'abc'); (root / 'same').write_bytes(b'abc')
    (root / 'alias').symlink_to('data')
    provenance = [{'path': 'source.txt', 'sha256': builder.sha(source)}]
    rows = []
    for category in ('compiler', 'package', 'host', 'native-library', 'asset'):
        rows.append({'id': category, 'scope': 'build', 'category': category,
                     'provenance': provenance, 'notices': [],
                     'notice_disposition': {'status': 'reviewed', 'evidence': 'fixture only'},
                     'disposition': {'status': 'reviewed', 'evidence': 'fixture only'}, 'files': []})
    rows[-1].pop('notice_disposition')
    rows[-1].update(scope='shipped', notices=[{'path': 'release/notices/example.txt', 'sha256': builder.sha(notice)}],
                    files=[{'path': n, 'type': 'file', 'sha256': builder.sha(root / n)} for n in ('data', 'same')] +
                          [{'path': 'alias', 'type': 'symlink', 'target': 'data'},
                           {'path': 'release/notices/example.txt', 'type': 'file', 'sha256': builder.sha(notice)}])
    for name, components in zip(builder.COMPLIANCE_CATALOGS, (rows[:2], rows[2:])):
        (candidate / name).write_text(json.dumps({'schema': 1, 'components': components}))
    config = {'candidate': str(candidate), 'sourceRoot': str(base), 'inputs': {
        str(candidate / 'adapter/release_compliance.py'): {'sha256': builder.sha(candidate / 'adapter/release_compliance.py')}}}
    output = base / 'review-output'; output.mkdir()
    result = builder.package_compliance(root, candidate, config, output)
    receipt = result['receipt']
    assert result['ok'] and isinstance(receipt, builder.ComplianceReceipt)
    tar = base / 'reviewed.tar'
    m = manifest(root); archive(root, tar)
    builder.audit_archive(tar, root, m, receipt)
    rejected(lambda: builder.audit_archive(tar, root, m), 'Compliance receipt required')
    alias = root / 'alias'; alias.unlink(); alias.symlink_to('same')
    m = manifest(root); archive(root, tar)
    rejected(lambda: builder.audit_archive(tar, root, m, receipt), 'Payload changed after compliance review')
    alias.unlink(); alias.symlink_to('../outside')
    m = manifest(root); archive(root, tar)
    rejected(lambda: builder.audit_archive(tar, root, m, receipt), 'Unsafe payload inventory')
    alias.unlink(); alias.symlink_to('data')
    m = manifest(root); archive(root, tar)
    builder.audit_archive(tar, root, m, receipt)


if __name__ == '__main__':
    main()
