import hashlib,json,resource,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];owner=r.parent/'elm-own-popup-native-census-v305'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as stream:
  for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
assert sha(owner/'component-manifest.json')=='5bf4159e022e538ccfa840e5e9f829b25e0e9cb6a7d70e603eb02397d5a89e15'
m=json.loads((owner/'component-manifest.json').read_text());count=0
for name,row in m['files'].items():
 p=owner/name;assert not p.is_symlink();assert sha(p)==row['sha256'] and p.stat().st_size==row['size'],name;count+=1
for name,digest in m['external'].items():assert sha(name)==digest,name;count+=1
b=json.loads(Path(m['buildReport']).read_text());t=json.loads(Path(m['testReport']).read_text())
assert sha(m['buildReport'])==m['buildReportSHA256'] and sha(m['testReport'])==m['testReportSHA256']
assert b['passed'] and t['passed'] and len(b['owningHeaders'])==694 and not b['missingSymbols']
assert b['core']['sha256']=='bda6ce0094961c285673589afa2b61fe2b97321a1d86b248823b482122fec0f5'
assert len(t['mutants'])==4 and all(x['killed'] and x['exitCode']!=0 for x in t['mutants'])
for packet,base in [(b,Path(m['buildReport']).parent),(t,Path(m['testReport']).parent)]:
 for name,digest in packet['artifacts'].items():assert sha(base/name)==digest,name
assert not m['nativeAcceptance'] and not m['installed']
report={'passed':True,'sourceReviewPassed':True,'nativeAcceptance':False,'ownBlockerGrantQualified':False,'rows':count,'ownerManifestSHA256':sha(owner/'component-manifest.json'),'blocker':None,'productionGrantBlocker':'Exact host connection/root/lease/full-binding and blocker-cause authentication unavailable'}
out=r/'qa'/('verify-'+str(time.time_ns()));out.mkdir();(out/'report.json').write_text(json.dumps(report,indent=2))
files={str(p.relative_to(r)):{'sha256':sha(p),'size':p.stat().st_size} for p in r.rglob('*') if p.is_file()}
p=r/'component-manifest.json';p.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'sourceReviewPassed':True,'nativeAcceptance':False,'ownBlockerGrantQualified':False,'ownerManifestSHA256':report['ownerManifestSHA256'],'files':files,'verificationReport':str((out/'report.json').relative_to(r))},indent=2));print(json.dumps({'rows':count,'manifestSHA256':sha(p)}))
