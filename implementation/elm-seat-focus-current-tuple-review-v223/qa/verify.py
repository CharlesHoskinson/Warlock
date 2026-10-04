import hashlib,importlib.util,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=Path('/home/hoskinson/omarchy-windows-parity');s=Path(__file__).resolve().parents[1];records={}
def verify(p,expected=None):
 p=Path(p);data=p.read_bytes();sha=hashlib.sha256(data).hexdigest();assert expected is None or sha==expected,str(p);records[str(p)]={'sha256':sha,'size':len(data)};return sha
def load(p):return json.loads(Path(p).read_text())
packets=[]
for lane in ['elm-seat-focus-bounded-acceptance-v458','elm-seat-focus-bounds-qualified-v460']:
 p=r/'implementation'/lane/'qa/slice-manifest.json';verify(p);d=load(p);assert d['passed'] and not d['fullReleaseAccepted'];verify(d['parentManifest'],d['parentManifestSHA256'])
 for row in d['files']:verify(r/row['path'],row['sha256'])
 for row in d['symlinks']:
  f=r/row['path'];assert f.is_symlink() and str(f.readlink())==row['target']
 for row in d['reports']:verify(r/row['path'],row['sha256']);assert load(r/row['path'])['passed']==row['passed']
 packets.append(d)
runtime=r/'implementation/elm-seat-focus-restored-runtime-v453';pair=load(runtime/'qa/build-pair-manifest.json')['nativePair'];assert pair==packets[0]['nativePair']==packets[1]['nativePair']
for row in pair.values():verify(row['path'],row['sha256'])
shared=[]
for row in packets[0]['reports']:
 if '/qa/native-' not in row['path']:continue
 d=load(r/row['path']);assert d['passed'] and d['cleanupPassed'] and all(c['passed'] for c in d['checks']) and d['pair']==pair
 host=d['privateHost'];assert host['privateAquamarine']['mappedFiles']=={pair['aquamarine']['path']:pair['aquamarine']['sha256']} and host['hyprlandMaps']['files'][pair['core']['path']]==pair['core']['sha256'];assert host['runtimeGone'] and not host['cleanupErrors']
 shared.append({'path':row['path'],'checks':len(d['checks'])})
assert sorted(x['checks'] for x in shared)==[57,89,161]
profiles=set();bounds=[]
for row in packets[1]['nativeEvidence']:
 d=load(r/row['path']);assert d['passed'] and d['cleanupPassed'] and len(d['checks'])==row['checks'] and all(c['passed'] for c in d['checks']) and not d['profileCleanupErrors'] and not d['finalCleanupErrors'];host=d['cleanup'];assert host['hyprlandMaps']['files'][pair['core']['path']]==pair['core']['sha256'];assert host['privateAquamarine']['mappedFiles']=={pair['aquamarine']['path']:pair['aquamarine']['sha256']};assert d['pluginMaps']['files'][pair['plugin']['path']]==pair['plugin']['sha256']
 actual={p['name'] for p in d['profiles']};assert actual==set(row['profiles']) and not profiles&actual;profiles|=actual;assert d['requestedOutput']=={'physicalMode':row['physicalMode'],'monitorScale':row['monitorScale']};bounds.append({'path':row['path'],'checks':row['checks'],'profiles':row['profiles']})
assert len(profiles)==22 and sum(x['checks'] for x in bounds)==604
spec=importlib.util.spec_from_file_location('reviewed453',runtime/'candidate_host.py');host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host);host.verify_inputs();descriptor,library=host.aq_tuple();assert str(library)==pair['aquamarine']['path']
old=r/'implementation/elm-shared-keyboard-runtime-v435';assert (runtime/'candidate_host.py').read_bytes()==(old/'candidate_host.py').read_bytes();oldprobe=verify(old/'parent-probe-build.json');newprobe=verify(runtime/'parent-probe-build.json');assert oldprobe!=newprobe
out=s/'qa'/('review-'+str(time.time_ns()));out.mkdir();report={'passed':True,'evidenceIntegrityPassed':True,'nativeChecksReviewed':911,'sharedReports':shared,'boundsReports':bounds,'nativePair':pair,'files':records,'actual453HostInputGuardsPassed':True,'parentProbeDescriptorChanged':True,'219BaselineInputEvidenceTransferred':False,'rendererCandidateQualified':False,'fullGeometryAccepted':False,'fullRoadmapAccepted':False,'releaseAccepted':False};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');files={str(p.relative_to(s)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size} for p in sorted(s.rglob('*')) if p.is_file() and p.name!='component-manifest.json'};(s/'component-manifest.json').write_text(json.dumps({'passed':True,'sourceHeld':True,'fullReleaseAccepted':False,'files':files,'externalFiles':records},indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'verifiedFiles':len(records),'nativeChecksReviewed':911}))
