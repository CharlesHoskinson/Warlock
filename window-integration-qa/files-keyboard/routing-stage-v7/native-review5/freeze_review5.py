#!/usr/bin/env python3
"""Lock this fresh reviewed fixture without native execution or changing old evidence."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parent
old_root = R.parent / 'native-review4'
old_path = old_root / 'frozen-inputs.json'
destination = R / 'frozen-inputs.json'
assert not destination.exists(), 'Never replace reviewed manifests'
old = json.loads(old_path.read_text())
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
paths = {old_path}
for entry in old['files']:
    path = Path(entry['path'])
    assert path.is_file() and digest(path) == entry['sha256'], 'Old frozen input changed: ' + str(path)
    if not path.is_relative_to(old_root):
        paths.add(path)
paths.update(p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and not any(part.startswith('attempt-') for part in p.parts))
manifest = {k: v for k, v in old.items() if k != 'files'}
manifest.update({
    'scope': 'Exact frozen V7 product/V6 guarded interfaces, fresh actual reader fixture compares bus/path after each navigation command with no-progress/revisit bound. Root GUI grant required.',
    'command': ['python3', str(R / 'run_native.py'), '--attempt', str(R / 'attempt-1')],
    'retainedReview4ManifestSHA256': digest(old_path),
    'files': [{'path': str(p), 'sha256': digest(p)} for p in sorted(paths)],
})
with destination.open('x') as stream:
    stream.write(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'files': len(paths), 'manifestSHA256': digest(destination), 'runnerSHA256': digest(R / 'run_native.py'), 'command': manifest['command']}))
