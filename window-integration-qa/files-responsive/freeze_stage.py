#!/usr/bin/env python3
"""Verify the reviewed source, record exact hashes, and generate its diff."""
from pathlib import Path
import difflib, hashlib, json, subprocess

B = Path(__file__).resolve().parent
LIVE = Path.home() / '.local/share/omarchy-files'
APP = B / 'app'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

changed, patches, parsed = [], [], []
for p in sorted(APP.rglob('*.qml')):
    rel = p.relative_to(APP)
    old = LIVE / rel
    assert old.is_file(), rel
    result = subprocess.run(['/usr/lib/qt6/bin/qmlformat', '--ignore-settings', str(p)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    parsed.append({'file':str(rel), 'exit':result.returncode, 'diagnostic':result.stderr})
    if p.read_bytes() != old.read_bytes():
        changed.append({'path':str(rel), 'originalSha256':sha(old), 'candidateSha256':sha(p)})
        patches.extend(difflib.unified_diff(old.read_text().splitlines(True), p.read_text().splitlines(True),
                                          fromfile='a/'+str(rel), tofile='b/'+str(rel)))
assert len(changed) == 11, changed
assert all(p['exit'] == 0 for p in parsed), parsed
unchanged = []
for old in sorted((LIVE / 'scripts').glob('*')) + [LIVE / 'spec/fileops.qnt']:
    if not old.is_file(): continue
    rel = old.relative_to(LIVE)
    assert sha(old) == sha(APP / rel), rel
    unchanged.append({'path':str(rel), 'sha256':sha(old), 'matchesLive':True})
manifest = {'changedQml':changed, 'unchangedOperationsAndFileopsSpec':unchanged,
            'originalExplorerTouched':False, 'samePidReloadRequiresExplicitMigration':True}
(B / 'source-hashes.json').write_text(json.dumps(manifest, indent=2)+'\n')
(B / 'responsive.patch').write_text(''.join(patches))
(B / 'parse-check.json').write_text(json.dumps(parsed, indent=2)+'\n')
print(json.dumps({'changedQml':len(changed), 'parsedQml':len(parsed), 'unchangedScriptsAndSpec':len(unchanged),
                  'manifestSha256':sha(B/'source-hashes.json'), 'patchSha256':sha(B/'responsive.patch')}, indent=2))
