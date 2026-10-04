#!/usr/bin/env python3
"""Read-only current-source closure audit; does not establish native acceptance."""
import hashlib
import json
import time
from pathlib import Path

ROOT = Path('/home/hoskinson/omarchy-windows-parity')
HERE = Path(__file__).resolve().parent
OUT = HERE / ('review-' + str(time.time_ns()))
OUT.mkdir()
checks = []

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def check(name, passed, **details):
    checks.append(dict(name=name, passed=bool(passed), **details))

try:
    manifest_path = ROOT / 'implementation/elm-shared-registration-eof-acceptance-v145/component-manifest.json'
    check('exactFinalCPUManifest', sha(manifest_path) == '65d6252dcd0d4b90ece6d67982e88b31bc010796b44c66483b0398ecc9d42fd8')
    manifest = json.loads(manifest_path.read_text())
    for group in ('files', 'externalClosure'):
        for entry in manifest[group]:
            p = Path(entry['path'])
            check('frozen:' + entry['path'], p.is_file() and p.stat().st_size == entry['size'] and sha(p) == entry['sha256'] and ('resolved' not in entry or str(p.resolve()) == entry['resolved']))
    source = ROOT / 'implementation/elm-shared-registration-eof-integration-v144'
    merged = ROOT / 'implementation/elm-shared-registration-shutdown-merge-v380'
    origin_path = merged / 'origin.json'
    origin = json.loads(origin_path.read_text())
    newer = ROOT / origin['ours']
    check('incomingBuildPinned', sha(ROOT / origin['otherBuildReport']) == origin['otherBuildReportSHA256'])
    check('newerDismissalParentPinned', sha(ROOT / origin['oursFrozenManifest']) == origin['oursFrozenManifestSHA256'])
    rows = json.loads((source / 'qa/merge-origins.json').read_text())['files']
    for row in rows:
        rel = row['path']
        check('incomingSource:' + rel, sha(source / rel) == row['mergedSHA256'])
        if rel in origin['reviewedChanges']:
            expected = origin['reviewedChanges'][rel]
            check('incomingDelta:' + rel, sha(source / rel) == expected and sha(merged / rel) == expected)
        else:
            check('newerParentRetained:' + rel, sha(merged / rel) == sha(newer / rel))
    check('nativeNotTransferredFromCPU', manifest['nativeAcceptance'] is False and manifest['releaseAcceptance'] is False)
    result = dict(passed=all(c['passed'] for c in checks), checks=checks, scope='Read-only frozen CPU closure and combined380 production merge provenance; no new native execution or release acceptance', manifestSHA256=sha(manifest_path), mergeOriginSHA256=sha(origin_path))
except Exception as exc:
    result = dict(passed=False, checks=checks, error=repr(exc), scope='Incomplete read-only closure audit')
(OUT / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(dict(passed=result['passed'], checks=len(checks), failures=[c['name'] for c in checks if not c['passed']], report=str(OUT / 'report.json'), error=result.get('error'))))
raise SystemExit(0 if result['passed'] else 1)
