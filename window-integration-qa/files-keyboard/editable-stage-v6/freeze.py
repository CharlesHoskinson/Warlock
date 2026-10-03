#!/usr/bin/env python3
"""Freeze staged sources only. Does not install, reload or signal original Files."""
from pathlib import Path
import difflib,hashlib,json
B=Path(__file__).resolve().parent;LIVE=Path.home()/'.local/share/omarchy-files'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
qml=[];patch=[]
for p in sorted((B/'app').rglob('*.qml')):
 rel=p.relative_to(B/'app');old=LIVE/rel
 if p.read_bytes()!=old.read_bytes():
  qml.append({'path':str(rel),'baselineSha256':sha(old),'candidateSha256':sha(p)})
  patch.extend(difflib.unified_diff(old.read_text().splitlines(True),p.read_text().splitlines(True),fromfile='live/'+str(rel),tofile='candidate/'+str(rel)))
operations=[]
for rel in sorted([p.relative_to(LIVE) for p in (LIVE/'scripts').iterdir() if p.is_file()]+[Path('spec/fileops.qnt')]):
 assert (B/'app'/rel).read_bytes()==(LIVE/rel).read_bytes(),rel
 operations.append({'path':str(rel),'sha256':sha(LIVE/rel)})
native=[{'path':str(p.relative_to(B)),'sha256':sha(p)} for p in sorted((B/'native-source').iterdir()) if p.is_file()]
native+=[{'path':str(p.relative_to(B)),'sha256':sha(p)} for p in sorted((B/'WindowAccessibilityV6').iterdir()) if p.is_file()]
native+=[{'path':str(B/n),'sha256':sha(B/n)} for n in ['text_authority.qnt','text_authority_test.qnt']]
manifest={'changedQml':qml,'unchangedOperationsAndSpec':operations,'native':native,'formal':[{'path':'../'+n,'sha256':sha(B.parent/n)} for n in ['keyboard_focus.qnt','keyboard_focus_test.qnt']]}
(B/'source-hashes.json').write_text(json.dumps(manifest,indent=2)+'\n');(B/'guard.patch').write_text(''.join(patch))
print(json.dumps({'changedQml':len(qml),'unchangedOperationsAndSpec':len(operations),'manifestSha256':sha(B/'source-hashes.json')}))
