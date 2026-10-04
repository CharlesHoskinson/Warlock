import hashlib,json,resource,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];owner=r.parent/'elm-gtk-full-driver-cleanup-adoption-v290';p=owner/'qa/native-1791150399602402045'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
j=json.loads((p/'report.json').read_text());assert sha(p/'report.json')=='f799c85ef385abdddd544e15cdbff714c731a935f33ffc0b0c247f64994588da'
count=0
for name,digest in j['artifacts'].items():assert sha(p/name)==digest,name;count+=1
for name,digest in j['inputs'].items():
 if isinstance(digest,str) and not name.endswith('#symlink'):assert sha(Path(name))==digest,name;count+=1
assert not j['passed'] and j['error']=="KeyError('windows')" and 'driver.py\", line 126' in j['traceback']
assert len(j['checks'])==5 and all(x['passed'] for x in j['checks'])
d=json.loads((p/'native-evidence/full-driver/report.json').read_text());assert len(d['checks'])==11 and all(x['passed'] for x in d['checks']);assert d['phases'][0]['name']=='GTK01' and d['phases'][0]['passed'];assert d['phases'][1]['name']=='GTK02' and not d['phases'][1]['passed']
assert j['cleanupPassed'] and j['cleanup']['privateActivationCleanupPassed'] and j['cleanup']['runtimeGone'] and not j['cleanup']['remainingDescendants']
report={'passed':True,'actualCampaignPassed':False,'nativeAcceptance':False,'rows':count,'actualGTK01Checks':11,'actualError':j['error'],'cleanupPassed':True,'ownerReportSHA256':sha(p/'report.json')}
out=r/'qa'/('verify-'+str(time.time_ns()));out.mkdir();(out/'report.json').write_text(json.dumps(report,indent=2))
files={str(q.relative_to(r)):{'sha256':sha(q),'size':q.stat().st_size} for q in r.rglob('*') if q.is_file()}
manifest=r/'component-manifest.json';manifest.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'Actual290 partial GTK01 evidence and preserved GTK02 DTO failure','files':files,'ownerReportSHA256':report['ownerReportSHA256'],'verificationReport':str((out/'report.json').relative_to(r))},indent=2));print(json.dumps({'rows':count,'manifestSHA256':sha(manifest)}))
