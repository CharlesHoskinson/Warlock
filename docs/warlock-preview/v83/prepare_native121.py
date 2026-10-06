"""Preserve120 failure; fix only new118 comparison of conditional allocator trials."""
import ast, hashlib, json, pathlib, resource, shutil, stat, sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
parent=repo/'implementation/warlock-client-provider-native-v120'
target=repo/'implementation/warlock-client-provider-native-v121'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
failure=next(parent.glob('qa/native-*/report.json'));proof=json.loads(failure.read_text())
assert not proof['passed'] and proof['cleanupPassed'] and all(row['exitCode']==0 for row in proof['ownedExitCodes'])
assert [row['name'] for row in proof['checks'] if not row['passed']]==['allPriorNative118StableOrderedAssertionsRetained']
for name,value in proof['artifacts'].items():assert sha(failure.parent/name)==value,name
assert proof['nativeIncarnationRetirementObservationBoundedQualified']
assert not target.exists()
manifest=parent/'component-manifest.json';assert not manifest.exists()
files={str(path.relative_to(parent)):{'kind':'file','sha256':sha(path),'size':path.stat().st_size,'mode':oct(stat.S_IMODE(path.stat().st_mode))} for path in sorted(parent.rglob('*')) if path.is_file() and '__pycache__' not in path.parts}
manifest.write_text(json.dumps({'sourceHeld':True,'passed':False,'evidenceIntegrityPassed':True,'files':files,
 'nativeReport':str(failure),'nativeAcceptance':False,'fullReleaseAccepted':False,
 'failure':'Actual native incarnation retirement, all original116 fixed controls and cleanup passed. New118 audit misclassified conditional allocation reuse trial rows as fixed identities:118 took9 trials and120 took1 under the unchanged original frame expiry. Fresh121 validates every real trial/clock/normal exit and compares unchanged fixed ordered gates; no original oracle, deadline or attempt limit changed.'},indent=2)+'\n')
def ignore(path,names):return [name for name in names if name in {'component-manifest.json','preflight.json','ANCESTRY.json','__pycache__'} or (pathlib.Path(path)==parent/'qa' and name.startswith(('native-','prepare-')))]
shutil.copytree(parent,target,ignore=ignore)
shutil.copy2(repo/'docs/warlock-preview/v83/reuse_comparison.py',target/'qa/reuse_comparison.py')
path=target/'qa/native.py';text=path.read_text()
old=" prior118=json.loads(pathlib.Path(pre['retainedNative118Report']).read_text());prior118Stable=stableNames(prior118['checks']);prior118Names=set(prior118Stable)\n check('allPriorNative118StableOrderedAssertionsRetained',len(prior118['checks'])==2467 and [name for name in stableNames(r['checks']) if name in prior118Names]==prior118Stable,stableControls=len(prior118Stable),priorRawControls=2467)"
new=" prior118=json.loads(pathlib.Path(pre['retainedNative118Report']).read_text())\n from reuse_comparison import compare\n comparison=compare(prior118,r,stableNames);r['addressReuseComparisonEvidence']=comparison\n check('allPriorNative118FixedOrderedAndActualRetryAssertionsRetained',len(prior118['checks'])==2467 and comparison['passed'],evidence=comparison)"
assert text.count(old)==1;text=text.replace(old,new);ast.parse(text);path.write_text(text)
path=target/'qa/prepare.py';text=path.read_text();marker=' assert all(sha(p)==h for p,h in inputs.items());';assert text.count(marker)==1
extra=" failed120=REPO/'"+str(failure.relative_to(repo))+"';proof120=json.loads(failed120.read_text());assert not proof120['passed'] and proof120['cleanupPassed'] and [row['name'] for row in proof120['checks'] if not row['passed']]==['allPriorNative118StableOrderedAssertionsRetained'] and all(row['exitCode']==0 for row in proof120['ownedExitCodes']);inputs[str(failed120)]=sha(failed120);pre['retainedConditionalReuseComparisonFailure']=str(failed120)\n"
text=text.replace(marker,extra+marker);ast.parse(text);path.write_text(text)
(target/'ANCESTRY.json').write_text(json.dumps({'owner':'f6779148-8f5d-4bdf-8a0f-044184e486f2','parent':str(parent),'parentManifestSHA256':sha(manifest),
 'purpose':'Unchanged core16/plugin18/GUI81 and original full118 runtime predicates. Fix only new cross-run118 fixture treatment of conditional allocator retries; retain each actual ordinal native incarnation/clock/normal exit, exact12-attempt maximum and original frame expiry. Preserve120 complete failed evidence.',
 'nativeAcceptance':False,'fullReleaseAccepted':False},indent=2)+'\n')
sys.path.insert(0,str(repo/'implementation/elm-build-loop-v1'));import loop
print(loop.write_checkpoint(repo,'f6779148-8f5d-4bdf-8a0f-044184e486f2',str(target.relative_to(repo)),
 ['PROGRESS native120 actual authenticated Active/Future/minimizedActive/Retired/liveNeighbor and original116 controls passed with276 normal exits; failed only new118 fixed-retry audit (118 nine trials versus120 one). Source/evidence120 held. Fresh121 fixes new audit only, validates all actual retry oracles/normal exits/original frame expiry and exact fixed ordered gates; full objective preserved. Next audit mutations/preflight/serial native.'],
 'progress',[str(manifest.relative_to(repo)),str((target/'ANCESTRY.json').relative_to(repo))]))
