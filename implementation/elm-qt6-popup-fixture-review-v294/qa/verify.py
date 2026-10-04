import hashlib,json,resource,stat,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];owner=r.parent/'elm-qt6-popup-landmark-fixture-v289'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(owner/'component-manifest.json')=='6a46eecfee38e000cee511671ba9c505531e2989b5a8291819cf90c9341e06fd'
m=json.loads((owner/'component-manifest.json').read_text());count=0
for name,row in m['files'].items():
 p=owner/name;assert not p.is_symlink();assert sha(p)==row['sha256'];assert p.stat().st_size==row['size'];assert stat.S_IMODE(p.stat().st_mode)==row['mode'];count+=1
for name,digest in m['externalFiles'].items():assert sha(Path(name))==digest;count+=1
assert len(m['unchangedFunctions'])==14
assert m['popupMarkerRGB']==[255,0,255] and m['popupMarkerRectangle']==[4,4,8,8]
assert not m['nativeAcceptance'] and not m['qt06Accepted']
reports=[]
for name in m['selectedReports']:
 p=owner/'qa'/name/'report.json';j=json.loads(p.read_text());assert j['passed'] and not j['nativeAcceptance'];reports.append({'path':str(p),'sha256':sha(p)})
report={'passed':True,'sourceReviewPassed':True,'nativeAcceptance':False,'qt06Accepted':False,'rows':count,'ownerManifestSHA256':sha(owner/'component-manifest.json'),'reports':reports,'blocker':None}
out=r/'qa'/('verify-'+str(time.time_ns()));out.mkdir();(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
files={str(p.relative_to(r)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(r.rglob('*')) if p.is_file()}
packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'sourceReviewPassed':True,'nativeAcceptance':False,'qt06Accepted':False,'ownerManifestSHA256':report['ownerManifestSHA256'],'files':files,'verificationReport':str((out/'report.json').relative_to(r))}
manifest=r/'component-manifest.json'
manifest.write_text(json.dumps(packet,indent=2))
print(json.dumps({'rows':count,'manifestSHA256':sha(manifest)}))
