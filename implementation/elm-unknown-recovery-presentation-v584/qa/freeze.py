#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
REPORT=ROOT/'qa/replay-1791144967661843289/report.json'
d=json.loads(REPORT.read_text());OUT=REPORT.parent
assert d['passed'] and len(d['checks'])==11 and all(x['passed'] for x in d['checks'])
for name,digest in d['artifacts'].items():assert sha(OUT/name)==digest,name
source=ROOT.parents[1]/'implementation/elm-pending-observation-join-v567'
for name,digest in d['sourceFiles'].items():assert sha(source/name)==digest,name
lines=(OUT/'captured573.log').read_text().splitlines(); published=[]
for i,line in enumerate(lines):
 if line.startswith('qa-bridge-input: origin=controller ') and ' json=' in line:
  frame=json.loads(line.split(' json=',1)[1]); packet=frame.get('projection',{}).get('frame',{})
  if packet.get('publication') in ['123','124']:
   published.append({'line':i+1,'rawLine':line,'frame':frame})
assert len(published)==2
assert all(next(c for c in x['frame']['projection']['frame']['bar'] if c['id']=='bar:group:application:GTK Application')['enabled'] for x in published)
(ROOT/'qa/native-published-witness.json').write_text(json.dumps(published,indent=2)+'\n')
attempts=[]
for p in sorted((ROOT/'qa').glob('replay-*')):
 attempts.append({'path':str(p.relative_to(ROOT)),'accepted':(p/'report.json').exists(),'compileExitEvidence':str((p/'compile.stderr').relative_to(ROOT)),'outputRowsPresent':(p/'rows.json').exists()})
(ROOT/'qa/attempt-history.json').write_text(json.dumps({'scope':'Retained failed harness attempts, not failed production repairs','attempts':attempts},indent=2)+'\n')
files={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and p.name!='component-manifest.json'}
(ROOT/'component-manifest.json').write_text(json.dumps({'schema':1,'passed':True,'sourceHeld':True,'nativeAcceptance':False,'scope':'Compiled public GUI567 Unknown reservation versus enabled action witness only; minimal presentation contract documented, not implemented','report':str(REPORT),'reportSHA256':sha(REPORT),'checks':11,'nativePublishedWitnessCount':len(published),'files':files,'limitations':d['limitations']},indent=2)+'\n')
print(json.dumps({'passed':True,'heldFiles':len(files),'checks':11,'nativePublishedWitnesses':len(published)}))
