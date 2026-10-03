"""Reconstruct complete reviewed V10 originals from explicit diagnostic-only hunks."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent
OLD=B.parent/'toolkit-held-matrix-v10'
def reconstructed(name,data=None):
 rows=json.loads((B/'source-delta-v11.json').read_text());row=rows[name]
 old=(OLD/name).read_bytes()
 if hashlib.sha256(old).hexdigest()!=row['oldSHA256']:raise RuntimeError('Immutable original source changed')
 source=old.decode();lines=source.splitlines(keepends=True);expected=[];cursor=0
 for hunk in row['hunks']:
  first,last=hunk['oldRange']
  if first<cursor or ''.join(lines[first:last])!=hunk['old']:raise RuntimeError('Exact diagnostic source hunk differs')
  expected.append(''.join(lines[cursor:first]));expected.append(hunk['new']);cursor=last
 expected.append(''.join(lines[cursor:]));expected=''.join(expected).encode()
 actual=(B/name).read_bytes() if data is None else data
 if actual!=expected:raise RuntimeError('Source differs beyond exact diagnostic-only hunks: '+name)
 return old
