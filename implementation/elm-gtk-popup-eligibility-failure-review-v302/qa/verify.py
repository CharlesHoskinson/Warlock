import hashlib,json,resource,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path(__file__).resolve().parents[1];owner=r.parent/'elm-gtk-full-driver-geometry-reply-v297';p=owner/'qa/native-1791151297849540332'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
j=json.loads((p/'report.json').read_text());ownerReportDigest=sha(p/'report.json')
count=0
for name,digest in j['artifacts'].items():assert sha(p/name)==digest,name;count+=1
for name,digest in j['inputs'].items():
 if isinstance(digest,str) and not name.endswith('#symlink'):assert sha(Path(name))==digest,name;count+=1
assert not j['passed'] and 'Original absolute six-second stage deadline' in j['error'] and 'shell.py' in j['traceback']
assert len(j['checks'])==5 and all(x['passed'] for x in j['checks'])
d=json.loads((p/'native-evidence/full-driver/report.json').read_text());assert len(d['checks'])==11 and all(x['passed'] for x in d['checks']);assert d['phases'][0]['name']=='GTK01' and d['phases'][0]['passed'];assert d['phases'][1]['name']=='GTK02' and not d['phases'][1]['passed']
assert j['cleanupPassed'] and j['cleanup']['privateActivationCleanupPassed'] and j['cleanup']['runtimeGone'] and not j['cleanup']['remainingDescendants']
lines=(p/'native-evidence/elm-webview.log').read_text().splitlines()
records=[]
for index,line in enumerate(lines):
 for prefix in ['backend-frame: ','surface-inspection: ']:
  if line.startswith(prefix):records.append((index,json.loads(line[len(prefix):])))
opened=next((i,v) for i,v in records if v.get('kind')=='surface-inspection' and v['publication']=='22')
assert opened[1]['body']['mode']=='menu' and opened[1]['body']['menu']['incarnation']=='2'
assert any(a['label']=='Maximize' and a['enabled'] is True for a in opened[1]['body']['menu']['actions'])
blocked=next((i,v) for i,v in records if v.get('kind')=='geometry-facts' and v['requestId']=='20')
f=blocked[1]['facts'];a=next(w for w in f['windows'] if w['incarnation']=='2')
assert f['inputBlocked'] is True and a['geometryEligible'] is False and a['capabilities']['maximize'] is False and a['visualGeometry']==[40,90,320,180]
closed=next((i,v) for i,v in records if v.get('kind')=='surface-inspection' and v['publication']=='25')
assert opened[0]<blocked[0]<closed[0] and closed[1]['body']['mode']=='closed'
assert any('surface-context-admitted:' in line for line in lines)
assert not any(v.get('kind')=='window-effect' for _,v in records)
assert not any(line.startswith('frontend-request: ') and json.loads(line[18:]).get('kind')=='window-effect' for line in lines)
helpers=list((p/'native-evidence').glob('shell-pointer-*'));assert len(helpers)==2
for helper in helpers:assert json.loads((helper/'record.json').read_text())['exit']==0
assert not list((p/'native-evidence').glob('shell-keyboard-*'))
report={'passed':True,'actualCampaignPassed':False,'nativeAcceptance':False,'rows':count,'actualGTK01Checks':11,'actualError':j['error'],'cleanupPassed':True,'ownerReportSHA256':sha(p/'report.json')}
out=r/'qa'/('verify-'+str(time.time_ns()));out.mkdir();(out/'report.json').write_text(json.dumps(report,indent=2))
files={str(q.relative_to(r)):{'sha256':sha(q),'size':q.stat().st_size} for q in r.rglob('*') if q.is_file()}
manifest=r/'component-manifest.json';manifest.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'Actual297 partial GTK01 and own-popup eligibility retirement failure','files':files,'ownerReportSHA256':report['ownerReportSHA256'],'verificationReport':str((out/'report.json').relative_to(r))},indent=2));print(json.dumps({'rows':count,'manifestSHA256':sha(manifest)}))
