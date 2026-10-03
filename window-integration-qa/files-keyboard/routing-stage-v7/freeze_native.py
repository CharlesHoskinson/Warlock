#!/usr/bin/env python3
"""Prepare the review4 source lock only. Never launch native fixtures or replace a lock."""
from pathlib import Path
import hashlib
import json

B = Path(__file__).resolve().parent
R = B / 'native-review4'
V = B.parent / 'editable-stage-v6'
destination = R / 'frozen-inputs.json'
assert not destination.exists(), 'Preserve every reviewed lock; use a fresh runner revision'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

old = json.loads((V / 'native-review3/frozen-inputs.json').read_text())
paths = set()
for entry in old['files']:
    path = Path(entry['path'])
    if not path.is_relative_to(V):
        assert path.is_file() and digest(path) == entry['sha256'], 'External reviewed input changed: ' + str(path)
        paths.add(path)

for folder in ['app', 'native-source', 'WindowAccessibilityV6', 'native-review4/qa-app',
               'native-review4/reader-profile', 'native-review4/home', 'native-review4/state', 'native-review4/bin']:
    paths.update(p for p in (B / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
for name in ['contract.md', 'REPORT.md', 'MODEL.md', 'keyboard_focus.qnt', 'keyboard_focus_test.qnt',
             'text_authority.qnt', 'text_authority_test.qnt', 'source-hashes.json', 'guard.patch',
             'freeze.py', 'freeze_native.py', 'prepare_deployment.py', 'offscreen-keys-report.json',
             'routing-report.json', 'model-named.log', 'model-seeded.log', 'deployment-prepared/plan.json']:
    paths.add(B / name)
paths.update(p for p in R.iterdir() if p.is_file() and p.suffix in ['.py', '.json'])
files = [{'path': str(p), 'sha256': digest(p)} for p in sorted(paths)]
manifest = {
    'scope': 'Fresh V7 QML routing plus exact V6 guarded native interfaces; actual silent Orca broad runner, root GUI grant required.',
    'command': ['python3', str(R / 'run_native.py'), '--attempt', str(R / 'attempt-1')],
    'productSourceManifestSHA256': digest(B / 'source-hashes.json'),
    'nativeModuleSHA256': digest(B / 'WindowAccessibilityV6/libwindowaccessibility.so'),
    'deploymentPlanSHA256': digest(B / 'deployment-prepared/plan.json'),
    'input': 'wtype Wayland virtual-keyboard protocol; physical hardware not claimed',
    'catalogs': 'Natural four-second settling only; immediate/final comparisons retained; no writes',
    'clientComparison': 'Every captured stable compositor field strictly equal; private raw before/after snapshots and app-owned title hashes observed separately. Prior strict-title failure remains immutable.',
    'output': 'Exclusive attempt-1 mode0700; files0600. No retries without a new root grant.',
    'files': files,
}
with destination.open('x') as stream:
    stream.write(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'files': len(files), 'manifestSHA256': digest(destination), 'command': manifest['command']}))
