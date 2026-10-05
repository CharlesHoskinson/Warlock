"""Verify actual replay evidence and raw source identity before freezing."""
import hashlib,json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
native=ROOT/'qa/native-1791237123393481021/report.json'
r=json.loads(native.read_text());assert r['passed'] and r['cleanupPassed']
assert len(r['checks'])==681 and all(x['passed'] for x in r['checks'])
assert len(r['cacheTraceReplay'])==5 and sum(t['statesCompared'] for t in r['cacheTraceReplay'])==46
assert len(r['ownedExitCodes'])==62 and all(x['exitCode']==0 for x in r['ownedExitCodes'])
original=json.loads((REPO/'implementation/warlock-client-child-native-v2/qa/native-1791235916575327729/report.json').read_text())
assert {x['name'] for x in original['checks']} <= {x['name'] for x in r['checks']}
pre=json.loads((ROOT/'qa/preflight.json').read_text())
for path,digest in pre['inputs'].items():assert sha(path)==digest,path
for t in r['cacheTraceReplay']:assert sha(t['trace'])==t['sha256'] and t['statesCompared']==len(t['steps'])
for root in [REPO/'implementation/warlock-client-child-fixture-v2',ROOT]:
 assert not (root/'component-manifest.json').exists()
 files={str(p.relative_to(root)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(root.rglob('*')) if p.is_file() and not p.is_symlink()}
 packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullReleaseAccepted':False,'boundedNativeCacheQualification':True,'nativeReport':str(native),'nativeReportSHA256':sha(native),'files':files}
 (root/'component-manifest.json').write_text(json.dumps(packet,indent=2)+'\n')
print(json.dumps({'passed':True,'nativeControls':681,'selectedQuintScenarios':5,'nativeComparedStates':46,'normalExits':62}))
