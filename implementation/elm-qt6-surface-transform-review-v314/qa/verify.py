import hashlib,json,resource,time,shutil
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OUT=ROOT/'qa'/('verify-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={'passed':False,'nativeAcceptance':False,'scope':'Independent held308/309 source inventory and actual selected CPU/build evidence; no native transform correspondence','components':[]}
pins={}
try:
 r['sourceInputs']={str(p):sha(p) for p in [Path(__file__),ROOT/'REVIEW.md']}
 for p in r['sourceInputs']:
  dest=OUT/'inputs'/Path(p).name;dest.parent.mkdir(exist_ok=True);shutil.copy2(p,dest)
 for name,digest in [('elm-qt6-surface-transform-fixture-v308','2b1bd8a8f572253773be6bcddc1c04e2c9ed4d00447cb9c755caa519fd72903c'),('elm-qt6-surface-transform-consumer-v309','670c778b82d5ffe514ccb677b6e219c3dc21be29d28ce5f196f16b2fcedf9d30')]:
  base=REPO/'implementation'/name;mp=base/'component-manifest.json';assert sha(mp)==digest
  m=json.loads(mp.read_text());assert m['sourceHeld'] and m['evidenceIntegrityPassed'] and not m['nativeAcceptance']
  pins[str(mp)]=digest
  for rel,row in m['files'].items():
   p=base/rel;assert sha(p)==row['sha256'],str(p);pins[str(p)]=row['sha256']
  for path,row in m['externalFiles'].items():
   assert sha(path)==row['sha256'],path;pins[path]=row['sha256']
  for rel,row in m['selectedEvidence'].items():
   p=base/rel;assert sha(p)==row['sha256'];report=json.loads(p.read_text());assert report['passed']==row['passed']
  statuses={rel:row['passed'] for rel,row in m['selectedEvidence'].items()}
  if name.endswith('v308'):
   assert statuses['qa/build-1791153257944841921/report.json'] is True
   assert statuses['qa/build-1791153219354230166/report.json'] is False
   assert sum(statuses.values())==5 and len(statuses)==6
  else:assert statuses=={'qa/test-1791153370599135866/report.json':True}
  r['components'].append({'component':name,'manifestSHA256':digest,'own':len(m['files']),'external':len(m['externalFiles']),'selected':len(statuses),'passedReports':sum(statuses.values()),'retainedFailures':len(statuses)-sum(statuses.values())})
 for p,digest in r['sourceInputs'].items():assert sha(p)==digest and sha(OUT/'inputs'/Path(p).name)==digest
 r['passed']=True
except Exception as e:r['error']=repr(e)
(OUT/'pins.json').write_text(json.dumps(pins,indent=2)+'\n');r['pinsSHA256']=sha(OUT/'pins.json')
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'components':r['components'],'error':r.get('error')}))
raise SystemExit(not r['passed'])
