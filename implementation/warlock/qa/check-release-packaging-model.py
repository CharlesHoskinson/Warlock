#!/usr/bin/env python3
"""Receipt-aware synthetic correspondence probe, not release acceptance."""
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'adapter'))
import release_builder as b
b.require_scope()


def transport(payload, tar):
    files = {str(p.relative_to(payload)): {'sha256': b.sha(p),
             'symlink': os.readlink(p) if p.is_symlink() else None}
             for p in sorted(payload.rglob('*')) if p.is_file() and p.relative_to(payload).as_posix() != 'MANIFEST.json'}
    manifest = {'files': files}
    (payload / 'MANIFEST.json').write_text(json.dumps(manifest))
    with tarfile.open(tar, 'w') as stream:
        for path in sorted(payload.rglob('*')):
            stream.add(path, arcname='warlock/' + str(path.relative_to(payload)), recursive=False)
    return manifest


def must_refuse(call, expected):
    try:
        call()
    except b.ChangedInput as error:
        assert expected in str(error), str(error)
    else:
        raise AssertionError('expected refusal: ' + expected)


with tempfile.TemporaryDirectory(prefix='warlock-packaging-model-') as temp:
    repo = Path(temp); workspace = repo / 'implementation/warlock'; payload = repo / 'payload'; output = repo / 'output'
    (workspace / 'adapter').mkdir(parents=True); (workspace / 'release/notices').mkdir(parents=True)
    (payload / 'assets').mkdir(parents=True); output.mkdir()
    shutil.copyfile(ROOT / 'adapter/release_compliance.py', workspace / 'adapter/release_compliance.py')
    provenance = repo / 'source'; provenance.write_text('synthetic source')
    notice = workspace / 'release/notices/example.txt'; notice.write_text('synthetic notice')
    app = payload / 'assets/app.js'; app.write_text('reviewed')
    other = payload / 'assets/other.js'; other.write_text('alternative')
    alias = payload / 'assets/alias.js'; alias.symlink_to('app.js')
    components = []
    for category in ('compiler', 'package', 'host', 'native-library', 'asset'):
        components.append({'id': category, 'scope': 'build', 'category': category,
            'provenance': [{'path': 'source', 'sha256': b.sha(provenance)}], 'notices': [],
            'notice_disposition': {'status': 'reviewed', 'evidence': 'fixture'},
            'disposition': {'status': 'reviewed', 'evidence': 'fixture'}, 'files': []})
    asset = components[-1]; asset.pop('notice_disposition')
    asset.update(scope='shipped', notices=[{'path': 'release/notices/example.txt', 'sha256': b.sha(notice)}],
        files=[{'path': 'assets/app.js', 'type': 'file', 'sha256': b.sha(app)},
               {'path': 'assets/other.js', 'type': 'file', 'sha256': b.sha(other)},
               {'path': 'assets/alias.js', 'type': 'symlink', 'target': 'app.js'},
               {'path': 'release/notices/example.txt', 'type': 'file', 'sha256': b.sha(notice)}])
    for name, rows in zip(b.COMPLIANCE_CATALOGS, (components[:2], components[2:])):
        (workspace / name).write_text(json.dumps({'schema': 1, 'components': rows}))
    lock = {'candidate': str(workspace), 'sourceRoot': str(repo), 'sources': [], 'inputs': {}}
    for name in [*b.COMPLIANCE_CATALOGS, 'adapter/release_compliance.py', 'release/notices/example.txt']:
        lock['sources'].append(name); b.add(lock['inputs'], workspace / name, 'candidate-source')
    b.add(lock['inputs'], provenance, 'compliance-provenance')
    b.check_compliance_lock(lock)
    result = b.package_compliance(payload, workspace, lock, output)
    assert result['ok']
    receipt = result['receipt']; tar = repo / 'candidate.tar'
    original_notice = payload / 'release/notices/example.txt'
    metadata = payload / 'release/compliance/SBOM.json'
    cases = [
        ('asset', app, 'changed after review', 'Payload changed after compliance review'),
        ('notice', original_notice, 'changed notice', 'Payload changed after compliance review'),
        ('metadata', metadata, 'changed metadata', 'Compliance metadata changed after review'),
    ]
    package_manifest = transport(payload, tar)
    b.audit_archive(tar, payload, package_manifest, receipt)
    must_refuse(lambda: b.audit_archive(tar, payload, package_manifest), 'Compliance receipt required')
    passed = ['unchanged_receipt_accepted', 'missing_receipt_refused']
    for label, path, changed, error in cases:
        original = path.read_bytes(); path.write_text(changed)
        package_manifest = transport(payload, tar)
        must_refuse(lambda: b.audit_archive(tar, payload, package_manifest, receipt), error)
        path.write_bytes(original); passed.append(label + '_mutation_refused')
    alias.unlink(); alias.symlink_to('other.js')
    package_manifest = transport(payload, tar)
    must_refuse(lambda: b.audit_archive(tar, payload, package_manifest, receipt), 'Payload changed after compliance review')
    alias.unlink(); alias.symlink_to('app.js'); passed.append('symlink_mutation_refused')
    package_manifest = transport(payload, tar)
    b.audit_archive(tar, payload, package_manifest, receipt); passed.append('restored_payload_accepted')
    app.write_text('changed after archive')
    must_refuse(lambda: b.audit_archive(tar, payload, package_manifest, receipt), 'Payload changed after compliance review')
    passed.append('post_archive_mutation_refused')
    print(json.dumps({'passed': passed, 'scope': 'synthetic; no release acceptance'}))
