import hashlib,json,time
from pathlib import Path
ROOT=Path('/home/hoskinson/omarchy-windows-parity')
OWN=ROOT/'implementation/elm-geometry-effective-policy-evidence-v172'
NAMES=['elm-geometry-authority-protocol-review-v168','elm-geometry-effective-fixed-prototype-v169','elm-geometry-size-policy-wire-characterization-v170','elm-geometry-effective-fixed-review-v171']
out=OWN/'qa'/('verify-'+str(time.time_ns()));out.mkdir()
records={}
def record(p,expected=None):
 p=Path(p); data=p.read_bytes(); row={'sha256':hashlib.sha256(data).hexdigest(),'size':len(data)}
 if expected:
  assert row['sha256']==expected['sha256'],str(p)
  if 'size' in expected: assert row['size']==expected['size'],str(p)
 records[str(p)]=row
for name in NAMES:
 base=ROOT/'implementation'/name
 for p in base.rglob('*'):
  if p.is_file(): record(p)
 for filename in ['component-manifest.json','reviewed-inputs.json']:
  p=base/filename
  if not p.exists():continue
  obj=json.loads(p.read_text())
  for key in ['files','externalClosure','upstream']:
   for path,expected in obj.get(key,{}).items():
    if isinstance(expected,dict) and 'sha256' in expected:record(Path(path) if path.startswith('/') else base/path,expected)
report={'evidenceIntegrityPassed':True,'verifiedFiles':len(records),'files':records,'nativeAcceptance':False,'policyAcceptance':False,'modelAcceptance':False,'releaseAcceptance':False,'scope':'Independent manifest/source integrity closure; no behavioral rerun'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'report':str(out/'report.json'),'verifiedFiles':len(records),'evidenceIntegrityPassed':True}))
