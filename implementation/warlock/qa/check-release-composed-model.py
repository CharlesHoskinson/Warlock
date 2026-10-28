#!/usr/bin/env python3
"""Check the production archive audit at and after its observation boundary."""
import hashlib
import json
import sys
import tarfile
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'adapter'))
from release_builder import audit_archive, ChangedInput

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    payload = root / 'package'
    payload.mkdir()
    body = payload / 'body'
    body.write_bytes(b'original')
    manifest = {'files': {'body': {'sha256': hashlib.sha256(b'original').hexdigest(), 'symlink': None}}}
    (payload / 'MANIFEST.json').write_text(json.dumps(manifest))
    archive = root / 'candidate.tar'
    with tarfile.open(archive, 'w') as stream:
        for path in sorted(payload.iterdir()):
            stream.add(path, arcname='warlock/' + path.name)
    audit_archive(archive, payload, manifest)
    body.write_bytes(b'changed')
    try:
        audit_archive(archive, payload, manifest)
    except ChangedInput:
        pass
    else:
        raise AssertionError('changed payload was not rejected on re-audit')
    # The first returned audit is a historical observation; it does not prevent
    # a later filesystem write. No assertion equates it with release acceptance.
    assert body.read_bytes() == b'changed'
print('archive audit accepts matching bytes, rejects changed bytes on re-audit; later mutation possible')

# Independently assemble a reviewed fixture through the production API, then
# rebuild matching manifest/archive after each mutation. This specifically checks
# the receipt boundary rather than only an archive/live-payload discrepancy.
import os
import shutil
import release_builder as builder

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    candidate = root / 'candidate'
    (candidate / 'adapter').mkdir(parents=True)
    (candidate / 'release').mkdir()
    payload = root / 'payload'; payload.mkdir()
    output = root / 'output'; output.mkdir()
    shutil.copyfile(Path(builder.__file__).with_name('release_compliance.py'), candidate / 'adapter/release_compliance.py')
    source = root / 'source'; source.write_bytes(b'provenance')
    app = payload / 'app'; app.write_bytes(b'reviewed')
    rows = []
    for category in ('compiler', 'package', 'host', 'native-library', 'asset'):
        item = {'id': category, 'category': category, 'scope': 'build',
                'provenance': [{'path': 'source', 'sha256': builder.sha(source)}],
                'notices': [], 'notice_disposition': {'status': 'reviewed', 'evidence': 'fixture'},
                'disposition': {'status': 'reviewed', 'evidence': 'fixture'}, 'files': []}
        rows.append(item)
    rows[-1].update(scope='shipped', files=[{'path': 'app', 'type': 'file', 'sha256': builder.sha(app)}])
    for name, group in zip(builder.COMPLIANCE_CATALOGS, (rows[:2], rows[2:])):
        (candidate / name).write_text(json.dumps({'schema': 1, 'components': group}))
    lock = {'candidate': str(candidate), 'sourceRoot': str(root), 'sources': [], 'inputs': {}}
    for name in [*builder.COMPLIANCE_CATALOGS, 'adapter/release_compliance.py']:
        lock['sources'].append(name)
        builder.add(lock['inputs'], candidate / name, 'candidate-source')
    builder.add(lock['inputs'], source, 'compliance-provenance')
    builder.check_compliance_lock(lock)
    receipt = builder.package_compliance(payload, candidate, lock, output)['receipt']
    archive = root / 'candidate.tar'
    def rebuild():
        manifest = {'files': {str(p.relative_to(payload)): {'sha256': builder.sha(p),
                    'symlink': os.readlink(p) if p.is_symlink() else None}
                    for p in sorted(payload.rglob('*')) if p.is_file() and p.name != 'MANIFEST.json'}}
        (payload / 'MANIFEST.json').write_text(json.dumps(manifest))
        with tarfile.open(archive, 'w') as stream:
            for p in sorted(payload.rglob('*')):
                stream.add(p, arcname='warlock/' + str(p.relative_to(payload)), recursive=False)
        return manifest
    def refused(manifest, receipt_arg, expected):
        try:
            builder.audit_archive(archive, payload, manifest, receipt_arg)
        except ChangedInput as exc:
            assert expected in str(exc), str(exc)
        else:
            raise AssertionError('expected refusal: ' + expected)
    manifest = rebuild()
    builder.audit_archive(archive, payload, manifest, receipt)
    refused(manifest, None, 'Compliance receipt required')
    app.write_bytes(b'changed')
    refused(rebuild(), receipt, 'Payload changed after compliance review')
    app.write_bytes(b'reviewed')
    metadata = payload / 'release/compliance/SBOM.json'
    old = metadata.read_bytes(); metadata.write_bytes(b'changed metadata')
    refused(rebuild(), receipt, 'Compliance metadata changed after review')
    metadata.write_bytes(old)
    (root / 'outside').write_bytes(b'outside')
    (payload / 'escape').symlink_to('../outside')
    refused(rebuild(), receipt, 'Unsafe payload inventory')
    print('receipt fixture: accepted reviewed package; refused missing receipt, changed payload, changed metadata and escaping link')
