import hashlib,json,os,resource,stat,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];owner=r.parent/'elm-own-popup-native-tuple-plan-v321'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
assert sha(owner/'component-manifest.json')=='e78b5f154e0a7cc7f6f214a6eb59cf040f62e9bfcc24056946ceb4bc08b68ffc'
m=json.loads((owner/'component-manifest.json').read_text());count=0;links=0
for section,base in [('files',owner),('externalFiles',None)]:
 for name,row in m[section].items():
  p=base/name if base else Path(name)
  if 'symlink' in row:assert p.is_symlink() and os.readlink(p)==row['symlink'];links+=1;continue
  assert sha(p)==row['sha256'] and p.stat().st_size==row['size'],name
  if 'mode' in row:assert oct(stat.S_IMODE(p.stat().st_mode))==row['mode'],name
  count+=1
for name,row in m['symlinks'].items():assert os.readlink(owner/name)==row['symlink'];links+=1
assert not m['nativeAcceptance'] and not m['nativeReadiness'] and not m['liveProcessMapsProven'] and not m['hostControllerScopeProven'] and not m['historicalAcceptanceTransferred']
d=json.loads((owner/'runtime/native-build-report.json').read_text());assert sha(owner/'runtime/native-build-report.json')=='c36b32d7f621239cd9e4ba205fa5a4eda91daf8466a4c1fec03a7b0f5e3ce439'
c=json.loads(Path(d['buildReport']).read_text());a=json.loads(Path(d['pluginBuildReport']).read_text());o=json.loads(Path(d['observer']['buildReport']).read_text());assert c['owningHeaders']==a['owningHeaders']==o['owningHeaders'] and len(c['owningHeaders'])==694
assert sha(d['binary'])==d['sha256']==c['binarySHA256'];assert sha(d['plugin']['path'])==d['plugin']['sha256']==a['binarySHA256'];assert sha(d['observer']['path'])==d['observer']['sha256']==o['binarySHA256']
closure=json.loads(Path(d['linkClosureReport']).read_text());assert sha(d['linkClosureReport'])==d['linkClosureReportSHA256'];assert closure['passed'] and len(closure['libraries'])==171 and all(not x for x in closure['missingSymbols'].values())
assert {k:len(v) for k,v in closure['strongUndefined'].items()}=={'authority319':160,'observer315':128}
assert sha('/etc/ld.so.cache')==closure['currentLinkerCache']['sha256']
for name,row in m['selectedCPUReports'].items():assert sha(owner/name)==row['sha256'];assert json.loads((owner/name).read_text())['passed']
old=r.parent/'elm-gtk-full-driver-geometry-reply-v297/runtime/candidate_host.py';assert (owner/'runtime/candidate_host.py').read_bytes()==old.read_bytes()
report={'passed':True,'sourceReviewPassed':True,'nativeReadiness':False,'nativeAcceptance':False,'regularRows':count,'symlinkRows':links,'ownerManifestSHA256':sha(owner/'component-manifest.json'),'blocker':None}
out=r/'qa'/('verify-'+str(time.time_ns()));out.mkdir();(out/'report.json').write_text(json.dumps(report,indent=2))
files={str(p.relative_to(r)):{'sha256':sha(p),'size':p.stat().st_size} for p in r.rglob('*') if p.is_file()}
p=r/'component-manifest.json';p.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'sourceReviewPassed':True,'nativeReadiness':False,'nativeAcceptance':False,'ownerManifestSHA256':report['ownerManifestSHA256'],'files':files,'verificationReport':str((out/'report.json').relative_to(r))},indent=2));print(json.dumps({'regularRows':count,'symlinks':links,'manifestSHA256':sha(p)}))
