import hashlib,importlib.util,json,resource,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=Path('/home/hoskinson/omarchy-windows-parity');stage=Path(__file__).resolve().parents[1];records={}
def verify(p,expected=None):
 p=Path(p);data=p.read_bytes();sha=hashlib.sha256(data).hexdigest();assert expected is None or sha==expected,str(p);records[str(p)]={'sha256':sha,'size':len(data)};return sha
def load(p):return json.loads(Path(p).read_text())
manifest=root/'implementation/elm-shared-keyboard-integrated-v439/qa/slice-manifest.json';verify(manifest);d=load(manifest)
verify(d['parentManifest'],d['parentManifestSHA256'])
for row in d['files']:verify(root/row['path'],row['sha256'])
for row in d['reports']:verify(root/row['path'],row['sha256'])
runtime=root/'implementation/elm-shared-keyboard-runtime-v435';pair=load(runtime/'qa/build-pair-manifest.json')['nativePair']
for row in pair.values():verify(row['path'],row['sha256'])
assert (runtime/'candidate_host.py').read_bytes()==(root/'implementation/elm-geometry-producer-runtime-v185/candidate_host.py').read_bytes()
executions=[]
for version,count,stamp in [(436,69,'1791129876229558916'),(437,161,'1791129949035016177'),(438,57,'1791129983827890886')]:
 lane=next((root/'implementation').glob(f'*v{version}'));p=lane/'qa'/f'native-{stamp}'/'report.json';verify(p);r=load(p)
 assert r['passed'] and r['cleanupPassed'] and len(r['checks'])==count and all(x['passed'] for x in r['checks'])
 assert r['pair']==pair
 host=r['privateHost'];aq=host['privateAquamarine'];assert aq['mappedVerified'] and aq['mappedFiles']=={pair['aquamarine']['path']:pair['aquamarine']['sha256']}
 assert pair['aquamarine']['path'] in host['hyprlandMaps']['maps']
 assert host['runtimeGone'] and not host['cleanupErrors'] and not host['remainingDescendants'] and not host['xwaylandEnabled'] and host['qaScope']['coreLimit']==1
 executions.append({'report':str(p),'checks':count,'actualAquamarineMapsVerified':True})
old=root/'implementation/elm-parent-transport-retirement-v105/candidate/include';new=root/'implementation/elm-keyboard-focus-cancellation-v155/candidate/include'
headers=sorted(p.relative_to(old) for p in old.rglob('*') if p.is_file());assert headers==sorted(p.relative_to(new) for p in new.rglob('*') if p.is_file()) and len(headers)==19
for relative in headers:assert verify(old/relative)==verify(new/relative)
previous=load(root/'implementation/elm-geometry-bounds-runtime-v420/aq-tuple.json');symbols=[]
for p in [previous['library'],pair['aquamarine']['path']]:
 verify(p);result=subprocess.run(['/usr/bin/nm','-D','--defined-only',p],capture_output=True,text=True,timeout=10);assert result.returncode==0;symbols.append({line.split()[-1] for line in result.stdout.splitlines() if line.split()})
assert len(symbols[0])==1786 and not symbols[0]-symbols[1]
spec=importlib.util.spec_from_file_location('reviewed435',runtime/'candidate_host.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.verify_inputs();descriptor,lib=module.aq_tuple();assert str(lib)==pair['aquamarine']['path'] and descriptor['librarySHA256']==pair['aquamarine']['sha256']
failed=root/'implementation/elm-shared-keyboard-loss-failure-v443/HANDOFF.md';verify(failed)
out=stage/'qa'/('review-'+str(time.time_ns()));out.mkdir();report={'passed':True,'evidenceIntegrityPassed':True,'files':records,'runtime':str(runtime),'nativePair':pair,'reviewedNativeExecutions':executions,'headersIdentical':len(headers),'oldExportsPreserved':len(symbols[0]),'actualHostInputGuardsPassed':True,'nativeRerun':False,'forcedCapabilityRecoveryAccepted':False,'fullGeometryAccepted':False,'fullRoadmapAccepted':False,'releaseAccepted':False};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'verifiedFiles':len(records),'checksReviewed':sum(x['checks'] for x in executions)}))
