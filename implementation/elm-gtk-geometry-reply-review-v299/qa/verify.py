import hashlib,json,os,resource,stat,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];owner=r.parent/'elm-gtk-full-driver-geometry-reply-v297'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
assert sha(owner/'component-manifest.json')=='22d96729b370944e62a7d92688f8c6548646dc8718a4ec4be8b7d1a5d2607861'
m=json.loads((owner/'component-manifest.json').read_text());count=0
for section,base in [('files',owner),('externalFiles',None)]:
 for name,row in m[section].items():
  p=base/name if base else Path(name)
  if base:assert not p.is_symlink(),str(p)
  assert sha(p)==row['sha256'],str(p)
  assert p.stat().st_size==row['size'],str(p)
  assert oct(stat.S_IMODE(p.stat().st_mode))==row['mode'],str(p)
  count+=1
for name,target in m['symlinks'].items():
 p=owner/name;assert p.is_symlink() and os.readlink(p)==target,name
a=json.loads((owner/'adoption.json').read_text());base=owner.parent/'elm-gtk-privileged-helper-drain-v282';old=owner.parent/'elm-gtk-full-driver-v260'
assert len(a['adoptedModules'])==9
for name,digest in a['adoptedModules'].items():assert sha(owner/'qa/helpers'/name)==sha(base/'qa'/name)==digest,name
for name in ['shell.py','popup.py','keyboard.py','native.py','fault-native.py','observer_endpoint.py','client_evidence.py']:assert (owner/'qa'/name).read_bytes()==(old/'qa'/name).read_bytes(),name
parent=owner.parent/'elm-gtk-full-driver-cleanup-adoption-v290'
oldDriver=(parent/'qa/driver.py').read_text();newDriver=(owner/'qa/driver.py').read_text()
assert oldDriver.count("g['windows']")==1 and oldDriver.count("geo['windows']")==1
assert newDriver==oldDriver.replace("g['windows']","g['facts']['windows']").replace("geo['windows']","geo['facts']['windows']")
g=json.loads((owner/'qa/geometry-reply-1791150857004316463/report.json').read_text());assert g['passed'] and g['mockedNativeState'] and g['sourceSHA256']==sha(owner/'qa/driver.py')
assert len(g['controls'])==3 and all(x['refused'] for x in g['controls']);assert g['actualBody']['openPositiveGatesRetained']==1 and len(g['actualBody']['checks'])==3
reports=[]
for name in m['reports']:
 j=json.loads((owner/name).read_text());assert j['passed'],name
 reports.append({'path':name,'sha256':sha(owner/name),'checks':len(j.get('checks',[]))})
 for key,digest in j.get('inputs',{}).items():
  if not isinstance(digest,str) or key.endswith('#symlink'):continue
  p=Path(key);p=p if p.is_absolute() else owner/p
  assert sha(p)==digest,key
closure=json.loads((owner/'qa/closure-1791150981946350108/report.json').read_text());assert len(closure['checks'])==19 and all(x['passed'] for x in closure['checks'])
acq=json.loads((owner/'qa/acquisition-test-1791150927084547154/report.json').read_text());assert len(acq['checks'])==8
assert not m['nativeAcceptance'] and not m['fullCampaignPassed']
report={'passed':True,'sourceReviewPassed':True,'nativeAcceptance':False,'fullCampaignPassed':False,'rows':count,'symlinks':len(m['symlinks']),'reports':reports,'ownerManifestSHA256':sha(owner/'component-manifest.json'),'blocker':None}
out=r/'qa'/('verify-'+str(time.time_ns()));out.mkdir();(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
files={str(p.relative_to(r)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(r.rglob('*')) if p.is_file()}
(r/'component-manifest.json').write_text(json.dumps({'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'sourceReviewPassed':True,'nativeAcceptance':False,'fullCampaignPassed':False,'ownerManifestSHA256':report['ownerManifestSHA256'],'files':files,'verificationReport':str((out/'report.json').relative_to(r))},indent=2)+'\n')
print(json.dumps({'rows':count,'symlinks':len(m['symlinks']),'manifestSHA256':sha(r/'component-manifest.json')}))
