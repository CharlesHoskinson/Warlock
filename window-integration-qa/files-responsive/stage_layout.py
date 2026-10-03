#!/usr/bin/env python3
"""Recreate the tested candidate in a NEW directory; never edits the live app."""
from pathlib import Path
import argparse, hashlib, json, shutil

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--baseline', type=Path, default=Path.home()/'.local/share/omarchy-files')
parser.add_argument('--output', type=Path, required=True)
a=parser.parse_args(); b=Path(__file__).resolve().parent
a.baseline=a.baseline.resolve(); a.output=a.output.resolve()
assert not a.output.exists(), 'Output must be a new directory'
assert a.baseline.is_dir() and a.output != a.baseline
m=json.loads((b/'source-hashes.json').read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
for i in m['changedQml']:
    assert sha(a.baseline/i['path'])==i['originalSha256'], i['path']
    assert sha(b/'app'/i['path'])==i['candidateSha256'], i['path']
for i in m['unchangedOperationsAndFileopsSpec']:
    assert sha(a.baseline/i['path'])==i['sha256'], i['path']
shutil.copytree(a.baseline,a.output)
for i in m['changedQml']:
    shutil.copy2(b/'app'/i['path'],a.output/i['path'])
assert all(sha(a.output/i['path'])==i['candidateSha256'] for i in m['changedQml'])
assert all(sha(a.output/i['path'])==i['sha256'] for i in m['unchangedOperationsAndFileopsSpec'])
print(json.dumps({'output':str(a.output),'changedQml':len(m['changedQml']),'result':'pass'}))
