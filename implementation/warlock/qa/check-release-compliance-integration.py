#!/usr/bin/env python3
"""Protected fixture for release-builder compliance wiring, not release approval."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import tarfile
import os
import shutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'adapter'))
import release_builder as builder

builder.require_scope()
checks = []
def check(name, result):
    checks.append(name)
    assert result, name

def refused(call, text):
    try:
        call()
    except builder.ChangedInput as error:
        return text in str(error)
    return False

with tempfile.TemporaryDirectory(prefix='warlock-compliance-') as tmp:
    repo = Path(tmp); candidate = repo / 'implementation/warlock'
    (candidate / 'release/notices').mkdir(parents=True)
    notice = candidate / 'release/notices/example.txt'; notice.write_text('fixture notice\n')
    (candidate / 'adapter').mkdir()
    shutil.copyfile(ROOT / 'adapter/release_compliance.py', candidate / 'adapter/release_compliance.py')
    provenance = repo / 'source.txt'; provenance.write_text('fixture source\n')
    evidence = [{'path': 'source.txt', 'sha256': builder.sha(provenance)}]
    notice_evidence = [{'path': 'release/notices/example.txt', 'sha256': builder.sha(notice)}]
    components = []
    for category in ('compiler', 'package', 'host', 'native-library', 'asset'):
        component = {'id': category, 'scope': 'build', 'category': category,
            'provenance': evidence, 'notices': [], 'notice_disposition': {'status': 'reviewed', 'evidence': 'fixture only'}, 'disposition': {'status': 'reviewed', 'evidence': 'fixture only'}, 'files': []}
        components.append(component)
    components[-1].pop('notice_disposition')
    components[-1].update(scope='shipped', notices=notice_evidence,
        files=[{'path': 'release/notices/example.txt', 'type': 'file', 'sha256': builder.sha(notice)},
               {'path': 'assets/app.js', 'type': 'file', 'sha256': __import__('hashlib').sha256(b'fixture app\n').hexdigest()},
               {'path': 'assets/alias', 'type': 'symlink', 'target': 'app.js'}])
    for name, rows in zip(builder.COMPLIANCE_CATALOGS, (components[:2], components[2:])):
        (candidate / name).write_text(json.dumps({'schema': 1, 'components': rows}))
    manifest = {'candidate': str(candidate), 'sourceRoot': str(repo), 'sources': [], 'inputs': {}}
    for path in [candidate / name for name in builder.COMPLIANCE_CATALOGS] + [notice, candidate / 'adapter/release_compliance.py']:
        manifest['sources'].append(str(path.relative_to(candidate)))
        builder.add(manifest['inputs'], path, 'candidate-source')
    builder.add(manifest['inputs'], provenance, 'compliance-provenance')
    builder.check_compliance_lock(manifest)
    check('LockedEvidencePresent', True)
    relocated = repo / 'relocated'; shutil.copytree(candidate, relocated)
    moved = copy.deepcopy(manifest); moved['candidate'] = str(relocated)
    for name in moved['sources']:
        row = moved['inputs'].pop(str(candidate / name))
        row['resolved'] = str((relocated / name).resolve())
        moved['inputs'][str(relocated / name)] = row
    builder.check_compliance_lock(moved)
    relocated_payload = repo / 'relocated-payload'; (relocated_payload / 'assets').mkdir(parents=True)
    (relocated_payload / 'assets/app.js').write_text('fixture app\n')
    (relocated_payload / 'assets/alias').symlink_to('app.js')
    relocated_out = repo / 'relocated-out'; relocated_out.mkdir()
    check('RelocatedCandidateRetainsSourceRoot', builder.package_compliance(relocated_payload, relocated, moved, relocated_out)['ok'])
    old = copy.deepcopy(manifest); old['sources'].remove(builder.COMPLIANCE_CATALOGS[0])
    check('OldLockRefused', refused(lambda: builder.check_compliance_lock(old), 'lacks compliance catalog'))
    notice.write_text('changed notice\n')
    manifest.update(schema=1, environment={key: os.environ.get(key) for key in builder.ENV_KEYS},
                    tools={}, flags=[], hostDependencies=[])
    previous_deps = builder.native_dependencies
    builder.native_dependencies = lambda *args: []
    try:
        check('ChangedNoticeRefused', refused(lambda: builder.verify(manifest), 'Locked input changed'))
    finally:
        builder.native_dependencies = previous_deps
    notice.write_text('fixture notice\n')
    def payload(name):
        root = repo / name; (root / 'assets').mkdir(parents=True)
        (root / 'assets/app.js').write_text('fixture app\n')
        (root / 'assets/alias').symlink_to('app.js')
        return root
    first = payload('first'); out1 = repo / 'out1'; out1.mkdir()
    result = builder.package_compliance(first, candidate, manifest, out1)
    check('ReviewMetadataAndNoticesPackaged', result['ok'] and all((first / name).is_file() for name in result['metadata']) and (first / 'release/notices/example.txt').is_file())
    archive = repo / 'fixture.tar'
    def transport(root):
        package_manifest = {'files': {str(p.relative_to(root)): {'sha256': builder.sha(p),
            'symlink': os.readlink(p) if p.is_symlink() else None}
            for p in sorted(root.rglob('*')) if p.is_file() and p.relative_to(root).as_posix() != 'MANIFEST.json'}}
        (root / 'MANIFEST.json').write_text(json.dumps(package_manifest))
        with tarfile.open(archive, 'w') as stream:
            for path in sorted(root.rglob('*')):
                stream.add(path, arcname='warlock/' + str(path.relative_to(root)), recursive=False)
        return package_manifest
    receipt = result['receipt']
    package_manifest = transport(first)
    builder.audit_archive(archive, first, package_manifest, receipt)
    check('ActualArchiveMatchesManifest', True)
    check('ReceiptRequired', refused(lambda: builder.audit_archive(archive, first, package_manifest), 'receipt required'))
    check('IncompleteReceiptRefused', refused(lambda: builder.audit_archive(archive, first, package_manifest,
        builder.ComplianceReceipt(receipt.inventory, receipt.metadata[:-1])), 'Invalid compliance receipt'))
    app = first / 'assets/app.js'; app.write_text('changed after review')
    package_manifest = transport(first)
    check('ReviewedAssetMutationRefusedWithMatchingTransport', refused(lambda: builder.audit_archive(archive, first, package_manifest, receipt), 'Payload changed after compliance review'))
    app.write_text('fixture app\n')
    metadata = first / 'release/compliance/review.json'; before = metadata.read_bytes()
    metadata.write_text('{}\n'); package_manifest = transport(first)
    check('MetadataRewriteRefusedWithMatchingTransport', refused(lambda: builder.audit_archive(archive, first, package_manifest, receipt), 'Compliance metadata changed'))
    metadata.write_bytes(before)
    packaged_notice = first / 'release/notices/example.txt'; packaged_notice.write_text('altered notice\n')
    package_manifest = transport(first)
    check('NoticeMutationRefusedWithMatchingTransport', refused(lambda: builder.audit_archive(archive, first, package_manifest, receipt), 'Payload changed after compliance review'))
    packaged_notice.write_text('fixture notice\n')
    alias = first / 'assets/alias'; alias.unlink(); alias.symlink_to('../release/notices/example.txt')
    package_manifest = transport(first)
    check('LinkRetargetRefusedWithMatchingTransport', refused(lambda: builder.audit_archive(archive, first, package_manifest, receipt), 'Payload changed after compliance review'))
    alias.unlink(); alias.symlink_to(provenance)
    package_manifest = transport(first)
    check('EscapingLinkRefusedWithMatchingTransport', refused(lambda: builder.audit_archive(archive, first, package_manifest, receipt), 'Unsafe payload inventory'))
    check('StandaloneEscapingLinkRefused', refused(lambda: builder.audit_archive(archive, first, package_manifest), 'Unsafe payload inventory'))
    alias.unlink(); alias.symlink_to('app.js')
    package_manifest = transport(first)
    builder.audit_archive(archive, first, package_manifest, receipt)
    check('RestoredPayloadPasses', True)
    second = payload('second'); out2 = repo / 'out2'; out2.mkdir()
    builder.package_compliance(second, candidate, manifest, out2)
    check('MetadataDeterministic', all(builder.sha(first / name) == builder.sha(second / name) for name in result['metadata']))
    missing = payload('missing'); (missing / 'unowned').write_text('unowned')
    out3 = repo / 'out3'; out3.mkdir()
    check('UnownedPayloadBlocks', refused(lambda: builder.package_compliance(missing, candidate, manifest, out3), 'Redistribution review blocked') and not (missing / 'release/compliance').exists() and 'unaccounted' in (out3 / 'compliance-report.json').read_text())
    components[-1]['disposition']['status'] = 'unknown'
    (candidate / builder.COMPLIANCE_CATALOGS[1]).write_text(json.dumps({'schema': 1, 'components': components[2:]}))
    check('ChangedCatalogRefused', refused(lambda: builder.check_compliance_lock(manifest), 'catalog changed'))
    unknown = payload('unknown'); out4 = repo / 'out4'; out4.mkdir()
    check('UnknownDispositionBlocks', refused(lambda: builder.package_compliance(unknown, candidate, manifest, out4), 'Redistribution review blocked') and 'disposition incomplete' in (out4 / 'compliance-report.json').read_text())
    print(json.dumps({'passed': True, 'checks': checks, 'scope': 'Synthetic fixture only; no release or legal acceptance.'}))
