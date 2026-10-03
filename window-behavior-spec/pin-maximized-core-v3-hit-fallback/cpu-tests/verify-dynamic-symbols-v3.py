"""Read-only dynamic symbol availability against the actual linked closure."""
from pathlib import Path
import hashlib,json,subprocess
B=Path(__file__).resolve().parents[1];O=B/'final-review'
closure=json.loads((O/'compiler-and-linked-library-closure.json').read_text())
def lines(path,*flags):return subprocess.check_output(['nm','-D',*flags,str(path)],text=True).splitlines()
def normalize(name):return name.replace('@@','@')
exports={}
for path in closure['libraries']:
 for line in lines(path,'--defined-only'):
  pieces=line.split()
  if len(pieces)<3:continue
  name=pieces[-1];exports.setdefault(normalize(name),[]).append(path)
  if '@@'in name:exports.setdefault(name.split('@@')[0],[]).append(path)
records=[]
for path in [B/'plugin/hyprbars-native-max-core-v2-candidate.so',Path('/home/hoskinson/window-behavior-spec/pin-maximized-collector-v1-proposal/readonly-probe/libqt-modal-probe.so')]:
 required=[p[-1]for line in lines(path,'--undefined-only')if len(p:=line.split())==2 and p[0]=='U']
 missing=[name for name in required if normalize(name)not in exports]
 records.append(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),strongUndefined=len(required),missing=missing,resolution={name:exports[normalize(name)]for name in required if normalize(name)in exports}))
 assert not missing,missing
row=dict(nativeLoaded=False,coreExecuted=False,method='Actual version-sensitive nm -D strong U names; exports from actual core and recursively captured DT_NEEDED system libraries. This is source/build compatibility evidence, not native relocation/lifecycle proof.',closureSHA256=hashlib.sha256((O/'compiler-and-linked-library-closure.json').read_bytes()).hexdigest(),objects=records)
(O/'dynamic-symbol-availability-v3.json').write_text(json.dumps(row,indent=2)+'\n')
print(json.dumps([dict(path=r['path'],strongUndefined=r['strongUndefined'],missing=r['missing'])for r in records],indent=2))
