from pathlib import Path
import ast,hashlib,json,os,re,stat
OUT=Path(__file__).resolve().parent;B=Path('/home/hoskinson/window-integration-qa/family-preparation-thumbnail-v7');QA=B.parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
PROOF=QA/'thumbnail-v7-full-proof-v2/report.json';proof=json.loads(PROOF.read_text());baseinfo=json.loads((B/'inherited-v5-copy-v1.json').read_text());BASE=Path(baseinfo['base']);sources=proof['sources'];checks=[]
for name,w in sources.items():assert sha(name)==w['sha256']and stat.S_IMODE(Path(name).stat().st_mode)==w['mode'],name
assert (proof['result'],proof['pythonTests'],proof['quintNamedScenarios'],proof['quintModels'],proof['sourceUnchangedDuringProof'])==('pass',118,88,9,True)
assert len(proof['checks'])==28 and all(c['exitCode']==0 and sha(c['log'])==c['sha256']for c in proof['checks'])
changed={};unchanged=0
for name,w in baseinfo['copiedFiles'].items():
 p=BASE/name;q=B/name;assert sha(p)==w['sha256']and stat.S_IMODE(p.stat().st_mode)==w['mode'],name
 assert stat.S_IMODE(q.stat().st_mode)==w['mode'],name
 if sha(q)!=w['sha256']:changed[name]=dict(before=w['sha256'],after=sha(q))
 else:unchanged+=1
assert len(baseinfo['copiedFiles'])==416 and unchanged==408
expected={'actual_service_binding.qnt','actual_service_binding_test.qnt','native_integration.py','service_recovery_observer.py','native_faults.py','test_freezer_v2.py','module_binding.py','test_actual_binding.py'};assert set(changed)==expected
rootcons=json.loads((QA/'thumbnail-v7-root-source-conservation-v1.json').read_text())
for name,w in changed.items():assert rootcons['changed'][name]['beforeSHA256']==w['before']and rootcons['changed'][name]['afterSHA256']==w['after']
for name,target in baseinfo['copiedLinks'].items():assert (B/name).is_symlink()and os.readlink(B/name)==target
D=lambda n:ast.dump(n,include_attributes=False)
def function(tree,name):return next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))and n.name==name)
counts={}
for name,expected_count in [('native_integration.py',30),('native_faults.py',34)]:
 old=ast.parse((BASE/name).read_text());source=(B/name).read_text();new=ast.parse(source)
 calls=lambda t:[D(n)for n in ast.walk(t)if isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='check']
 assert calls(old)==calls(new)and len(calls(new))==expected_count;counts[name]=expected_count
 if name=='native_integration.py':source=source.replace("report['actualServiceBinding']","report['actualV20Binding']")
 else:
  source=source.replace('service-family-preparation-v23','service-readonly-ipc-v20').replace('Same frozen packet actual V23 baseline binding required','Same frozen packet actual V20 baseline binding required').replace('actualServiceRecoveryBinding','actualV20RecoveryBinding').replace('oldActualServiceBinding','oldActualV20Binding').replace('actualServiceBinding','actualV20Binding')
 assert D(function(old,'main'))==D(function(ast.parse(source),'main')),name
assert (B/'service_observer.py').read_bytes()==(BASE/'service_observer.py').read_bytes()
manifest=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-family-preparation-v23/manifest-family-preparation-v23.json');assert sha(manifest)=='0d2b7b231eaa26c6618783b1cb2305c2a989586b3a7cb371716e2d67603c82e2';packet=json.loads(manifest.read_text())
assert len(packet['inputs'])==len(packet['inputModes'])==15238 and len(packet['links'])==158
for name,h in packet['inputs'].items():assert sha(name)==h and stat.S_IMODE(Path(name).stat().st_mode)==packet['inputModes'][name],name
for name,target in packet['links'].items():assert Path(name).is_symlink()and os.readlink(name)==target,name
errors=[];counterpaths=[];accepted=0
for name in ('initial-callback-counterexample.json','initial-callback-owner-counterexample.json'):
 p=OUT/name;r=json.loads(p.read_text());assert r['sourceSHA256']==sha(B/'module_binding.py')and r['candidateEdited']is False and r['nativeLaunch']is False
 accepted+=sum(case['accepted']for case in r['cases']);counterpaths.append(dict(path=str(p),sha256=sha(p)))
assert accepted==7
output=(OUT/'focused.stderr.log').read_text();m=re.search(r'Ran (\d+) tests',output);assert m and int(m[1])==29 and re.search(r'\nOK\s*$',output)
row=dict(result='fail',classification='concrete missing initial callback function/owner identity guards',sourceAndExistingTests='pass',collector=str(B),proof=str(PROOF),proofSHA256=sha(PROOF),fullProof=dict(python=118,named=88,models=9,commands=28,sourceWitnesses=len(sources)),focused=dict(pythonTests=29,stdoutSHA256=sha(OUT/'focused.stdout.log'),stderrSHA256=sha(OUT/'focused.stderr.log')),sourceConservation=dict(inherited=416,unchanged=408,declaredChanges=changed,originalCheckCallASTsExact=counts,completeBaselineAndFaultMainInverseExact=True,actualCaptureRetirementObserverByteExact=True),candidateManifest=str(manifest),candidateManifestSHA256=sha(manifest),candidateClosure=dict(inputs=15238,modes=15238,links=158,fullBytesModesLinksExact=True),counterexamples=counterpaths,acceptedWrongInitialBindings=accepted,neededCorrection='Formal-before-source expected __func__ and __self__ for five BatchPreviews callbacks and finisher at initial/postdisk/terminal observations; original oracles unchanged',guiPairingReady=False,nativeLaunch=False,candidateEdited=False,original38Accepted=False,original34FaultsAccepted=False)
with os.fdopen(os.open(OUT/'review.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in row.items()if k not in('sourceConservation','counterexamples')}));print('reviewSHA256',sha(OUT/'review.json'))
