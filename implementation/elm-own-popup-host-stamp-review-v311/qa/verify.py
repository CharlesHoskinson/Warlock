import hashlib,json,resource,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];owner=r.parent/'elm-own-popup-host-surface-stamp-v310'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as stream:
  for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
assert sha(owner/'component-manifest.json')=='6e292615cf0edf1cb9b86dd39bfa7e66478c1b65c1f041832bd0581a26229776'
m=json.loads((owner/'component-manifest.json').read_text());count=0
for name,row in m['files'].items():
 p=owner/name;assert not p.is_symlink();assert sha(p)==row['sha256'] and p.stat().st_size==row['size'],name;count+=1
for name,digest in m['external'].items():assert sha(name)==digest,name;count+=1
b=json.loads(Path(m['buildReport']).read_text())
assert sha(m['buildReport'])==m['buildReportSHA256']
assert b['passed'] and len(b['commands'])==14 and all(c['exitCode']==0 for c in b['commands'])
for name,digest in b['artifacts'].items():assert sha(Path(m['buildReport']).parent/name)==digest,name
for name,digest in b['inputs'].items():assert sha(owner/name)==digest,name
w=json.loads((r/'qa/dedup-1791153746791159689/report.json').read_text());assert w['passed'] and w['unsafeHistoricalDedupWitness']
assert sha(r/'qa/preliminary/first-build-popup-native-stamp.h')==w['sourceSHA256']
assert not m['nativeAcceptance'] and not m['installed']
report={'passed':True,'sourceReviewPassed':True,'nativeAcceptance':False,'ownBlockerGrantQualified':False,'rows':count,'ownerManifestSHA256':sha(owner/'component-manifest.json'),'blocker':None,'productionGrantBlocker':'Exact host connection/root/lease/full-binding and blocker-cause authentication unavailable'}
out=r/'qa'/('verify-'+str(time.time_ns()));out.mkdir();(out/'report.json').write_text(json.dumps(report,indent=2))
files={str(p.relative_to(r)):{'sha256':sha(p),'size':p.stat().st_size} for p in r.rglob('*') if p.is_file()}
p=r/'component-manifest.json';p.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'sourceReviewPassed':True,'nativeAcceptance':False,'ownBlockerGrantQualified':False,'ownerManifestSHA256':report['ownerManifestSHA256'],'files':files,'verificationReport':str((out/'report.json').relative_to(r))},indent=2));print(json.dumps({'rows':count,'manifestSHA256':sha(p)}))
