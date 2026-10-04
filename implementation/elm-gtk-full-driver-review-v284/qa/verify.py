import hashlib,json,resource,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];o=r.parent/'elm-gtk-full-driver-v260';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
snapshot=o/'qa/review-snapshot-1791149033708515431/snapshot.json';assert sha(snapshot)=='08166ee5104763e04338fd3a00508b37e2c02deaff5ad90a2470d93502ee4129';m=json.loads(snapshot.read_text());count=0
for name,row in m['files'].items():
 p=o/name;assert sha(p)==row['sha256'] and p.stat().st_size==row['size'],name;count+=1
assert sha(o/'qa/driver.py')=='83f6c55b6280add0e289808c32aef6d8eaa6e55947343a98ace9217973739827'
old=o/'qa/review-snapshot-1791148790643019677/snapshot.json';oldm=json.loads(old.read_text());assert sha(old)=='6c8dfc35229b81ea90e569c5722ab3d364a51bee390d0d89d0488951e4339a88'
changed=[name for name,row in oldm['files'].items() if name in m['files'] and row['sha256']!=m['files'][name]['sha256']];assert changed==['qa/driver.py']
witness=o/'qa/close-deadline-1791148945814107722/report.json';fixed=o/'qa/close-deadline-1791148964814847341/report.json';w=json.loads(witness.read_text());f=json.loads(fixed.read_text());assert w['passed'] and w['correctionAccepted'] is False and not w['current']['refused'];assert f['passed'] and f['correctionAccepted'] is True and f['current']['refused'] and not f['current']['report']['phases'][0]['passed']
inputs={str(p):sha(p) for p in [snapshot,old,witness,fixed]}
report={'passed':True,'sourceReviewPassed':True,'nativeAcceptance':False,'wholeSourceHeld':False,'verifiedSnapshotRows':count,'deadlineCorrectionVerified':True,'readinessPrerequisite':m['readinessPrerequisite'],'scope':'Stable reviewed source snapshot; cleanup282 adoption/full source closure/native qualification still required','inputs':inputs}
out=r/'qa'/('verify-'+str(time.time_ns()));out.mkdir();(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');files={str(p.relative_to(r)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(r.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
(r/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'sourceReviewPassed':True,'nativeAcceptance':False,'scope':report['scope'],'files':files,'externalFiles':inputs,'verificationReport':str((out/'report.json').relative_to(r))},indent=2)+'\n');print(json.dumps({'rows':count,'manifestSHA256':sha(r/'component-manifest.json')}))
