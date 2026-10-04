import hashlib,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path('/home/hoskinson/omarchy-windows-parity');s=Path(__file__).resolve().parents[1];parent=r/'implementation/elm-geometry-feasible-bounds-native-v204';records={}
def verify(p,expected=None):
 p=Path(p);data=p.read_bytes();sha=hashlib.sha256(data).hexdigest();assert expected is None or expected==sha,str(p);records[str(p)]={'sha256':sha,'size':len(data)};return sha
def load(p):return json.loads(Path(p).read_text())
manifest=parent/'component-manifest.json';verify(manifest,'909dbbf0c2b0b12c80829e205942fa5412063fbd7802ff857d49735f36299cd3')
for name,row in load(manifest)['files'].items():verify(parent/name,row['sha256'])
source=parent/'qa/native.py';source_sha=verify(source,'ca4b37efeaba17152b834c3faa8913c6cfaba1f5775fe9dfdf55adb4c06d8c2a')
plan=load(parent/'profiles.json')['profiles'];seen=set();reports=[]
for stamp,count,mode,scale,n in [('1791132013131553507',372,[800,600],1,14),('1791132020652033678',186,[1600,1200],2,6),('1791132027391240978',46,[800,600],2,2)]:
 p=parent/'qa'/('native-'+stamp)/'report.json';sha=verify(p);d=load(p)
 assert d['passed'] and d['cleanupPassed'] and len(d['checks'])==count and all(x['passed'] for x in d['checks'])
 assert d['inputs'][str(source)]==source_sha and not d['profileCleanupErrors'] and not d['finalCleanupErrors']
 assert d['requestedOutput']=={'physicalMode':mode,'monitorScale':scale}
 expected={x['id'] for x in plan if x['physicalMode']==mode and x['monitorScale']==scale};actual={x['name'] for x in d['profiles']};assert actual==expected and len(actual)==n and not seen&actual;seen|=actual
 for path,digest in d['inputs'].items():verify(path,digest)
 for name,digest in d['artifacts'].items():verify(p.parent/name,digest)
 host=d['cleanup'];aq=host['privateAquamarine'];assert aq['mappedVerified'] and aq['mappedFiles']=={aq['path']:aq['sha256']}
 verify(aq['path'],aq['sha256']);assert host['runtimeGone'] and not host['cleanupErrors'] and not host['remainingDescendants'] and not host['xwaylandEnabled']
 gates=[x for x in d['checks'] if x['name'].endswith(':actualOutputScaleAndWorkareaBeforeIntent')];assert {x['name'].split(':')[0] for x in gates}==expected
 reports.append({'path':str(p),'sha256':sha,'checks':count,'profiles':sorted(actual),'physicalMode':mode,'monitorScale':scale})
assert seen=={x['id'] for x in plan} and len(seen)==22
out=s/'qa'/('verify-'+str(time.time_ns()));out.mkdir();report={'passed':True,'evidenceIntegrityPassed':True,'nativeCampaignExecuted':True,'nativeChecks':604,'profiles':sorted(seen),'reports':reports,'files':records,'sourceSHA256':source_sha,'scope':'Actual root204 controlled22 XDG constraint/display-scale/buffer-scale profiles only','nativePixelsAccepted':False,'physicalPointerAccepted':False,'gtkAccepted':False,'keyboardCapabilityRecoveryAccepted':False,'fullGeometryAccepted':False,'fullRoadmapAccepted':False,'releaseAccepted':False};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
files={str(p.relative_to(s)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size} for p in sorted(s.rglob('*')) if p.is_file() and p.name!='acceptance-manifest.json'}
(s/'acceptance-manifest.json').write_text(json.dumps({'passed':True,'boundedNativeAcceptance':True,'nativeChecks':604,'profileCount':22,'releaseAccepted':False,'files':files,'externalFiles':records},indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'verifiedFiles':len(records),'nativeChecks':604,'profiles':22}))
