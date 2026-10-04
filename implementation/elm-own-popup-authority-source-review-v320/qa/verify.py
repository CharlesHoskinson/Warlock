import hashlib,json,resource,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];owner=r.parent/'elm-own-popup-owning-authority-v319'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as stream:
  for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
assert sha(owner/'component-manifest.json')=='b67d280ecf9ce823e3cd4bb782ecb2b563a5643cf7ea902859fa03f48c607031'
m=json.loads((owner/'component-manifest.json').read_text());count=0
for name,row in m['files'].items():
 p=owner/name;assert not p.is_symlink();assert sha(p)==row['sha256'] and p.stat().st_size==row['size'],name;count+=1
for name,digest in m['external'].items():assert sha(name)==digest,name;count+=1
b=json.loads(Path(m['buildReport']).read_text());assert b['passed'] and not b['missingSymbols'] and len(b['owningHeaders'])==694 and b['strongUndefinedCount']==160
assert sha(m['buildReport'])==m['buildReportSHA256']
assert sha(b['binary'])==b['binarySHA256']
c=json.loads(Path(b['core']['buildReport']).read_text());assert c['passed'] and sha(b['core']['buildReport'])==b['core']['buildReportSHA256']
assert sha(b['core']['path'])==b['core']['sha256']==c['binarySHA256']
assert b['owningHeaders']==c['owningHeaders']
origin=json.loads((owner/'origin.json').read_text());assert len(origin['sourcePins'])==11
assert sha(origin['descriptor'])==origin['descriptorSHA256'] and sha(origin['buildReport'])==origin['buildReportSHA256']
parent=json.loads(Path(origin['buildReport']).read_text());assert parent['passed']
for name,digest in origin['sourcePins'].items():assert sha(owner/name)==sha(Path(origin['ancestor'])/name)==parent['inputs'][name]==digest,name
base=Path(m['buildReport']).parent
for name,digest in b['owningHeaders'].items():assert sha(base/'owning-headers'/name)==digest,name
for name,digest in b['artifacts'].items():assert sha(base/name)==digest,name
link=base/'include/hyprland';assert link.is_symlink() and str(link.readlink())==str(base/'owning-headers')
assert not m['nativeAcceptance'] and not m['installed']
report={'passed':True,'sourceReviewPassed':True,'nativeAcceptance':False,'ownBlockerGrantQualified':False,'rows':count,'ownerManifestSHA256':sha(owner/'component-manifest.json'),'blocker':None,'includeSymlink':{'path':str(link),'target':str(link.readlink())}}
out=r/'qa'/('verify-'+str(time.time_ns()));out.mkdir();(out/'report.json').write_text(json.dumps(report,indent=2))
files={str(p.relative_to(r)):{'sha256':sha(p),'size':p.stat().st_size} for p in r.rglob('*') if p.is_file()}
p=r/'component-manifest.json';p.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'sourceReviewPassed':True,'nativeAcceptance':False,'ownBlockerGrantQualified':False,'ownerManifestSHA256':report['ownerManifestSHA256'],'files':files,'verificationReport':str((out/'report.json').relative_to(r))},indent=2));print(json.dumps({'rows':count,'manifestSHA256':sha(p)}))
