from pathlib import Path
import ast,hashlib,json,os,re,stat
OUT=Path(__file__).resolve().parent;B=Path('/home/hoskinson/window-integration-qa/family-preparation-thumbnail-v7');QA=B.parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
PROOF=QA/'thumbnail-v7-full-proof-v3/report.json';proof=json.loads(PROOF.read_text());baseinfo=json.loads((B/'inherited-v5-copy-v1.json').read_text());BASE=Path(baseinfo['base']);sources=proof['sources'];checks=[]
for name,w in sources.items():assert sha(name)==w['sha256']and stat.S_IMODE(Path(name).stat().st_mode)==w['mode'],name
assert (proof['result'],proof['pythonTests'],proof['quintNamedScenarios'],proof['quintModels'],proof['sourceUnchangedDuringProof'])==('pass',120,109,10,True)
assert len(proof['checks'])==31 and all(c['exitCode']==0 and sha(c['log'])==c['sha256']for c in proof['checks'])
changed={};unchanged=0
for name,w in baseinfo['copiedFiles'].items():
 p=BASE/name;q=B/name;assert sha(p)==w['sha256']and stat.S_IMODE(p.stat().st_mode)==w['mode'],name
 assert stat.S_IMODE(q.stat().st_mode)==w['mode'],name
 if sha(q)!=w['sha256']:changed[name]=dict(before=w['sha256'],after=sha(q))
 else:unchanged+=1
assert len(baseinfo['copiedFiles'])==416 and unchanged==408
expected={'actual_service_binding.qnt','actual_service_binding_test.qnt','native_integration.py','service_recovery_observer.py','native_faults.py','test_freezer_v2.py','module_binding.py','test_actual_binding.py'};assert set(changed)==expected
rootcons=json.loads((QA/'thumbnail-v7-root-source-conservation-v1.json').read_text())
for name,w in changed.items():assert rootcons['changed'][name]['beforeSHA256']==w['before']and (name=='module_binding.py'or rootcons['changed'][name]['afterSHA256']==w['after'])
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
assert accepted==0
assert sum(len(json.loads((OUT/n).read_text())['cases'])for n in ('initial-callback-counterexample.json','initial-callback-owner-counterexample.json'))==7
for n in ('initial-callback-counterexample.json','initial-callback-owner-counterexample.json'):
 for case in json.loads((OUT/n).read_text())['cases']:
  assert case['raw']['errors']and case['raw']['usable']is False
  symbol=case['symbol'];guard='finisherOwner'if symbol=='desktop.finish_capture_previews'else 'batchCallback.'+symbol.removeprefix('batch.')
  assert case['raw']['relations'][guard]is False and all(v for k,v in case['raw']['relations'].items()if k!=guard),case

output=(OUT/'focused.py.stderr.log').read_text();m=re.search(r'Ran (\d+) tests',output);assert m and int(m[1])==31 and re.search(r'\nOK\s*$',output)

# Exact correction scope relative to the retained failed source epoch.
prior=json.loads((QA/'thumbnail-v7-full-proof-v2/report.json').read_text());delta=[p for p,w in prior['sources'].items()if proof['sources'].get(p)!=w]
assert set(Path(p).name for p in delta)=={'module_binding.py','test_batch_binding.py','run_collector_v7_proof.py'}
new=set(proof['sources'])-set(prior['sources']);assert {Path(p).name for p in new}=={'BATCH_CALLBACK_IDENTITY_CONTRACT.md','batch_callback_identity.qnt','batch_callback_identity_test.qnt'}
epoch=QA/'thumbnail-v7-callback-source-epoch-v1';saved=json.loads((epoch/'epoch.json').read_text())
for n,w in saved['sources'].items():assert sha(epoch/n)==w['sha256']and stat.S_IMODE((epoch/n).stat().st_mode)==w['mode']
oldtree=ast.parse((epoch/'module_binding.py').read_text());newtree=ast.parse((B/'module_binding.py').read_text())
oldnodes={getattr(n,'name',str(i)):n for i,n in enumerate(oldtree.body)};newnodes={getattr(n,'name',str(i)):n for i,n in enumerate(newtree.body)}
assert oldnodes.keys()==newnodes.keys();assert [n for n in oldnodes if D(oldnodes[n])!=D(newnodes[n])]==['batch_relations']
oldtest=ast.parse((epoch/'test_batch_binding.py').read_text());newtest=ast.parse((B/'test_batch_binding.py').read_text())
klass=lambda tree:next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='BatchBindingKernelTests')
originalmethods={n.name:n for n in klass(oldtest).body if isinstance(n,ast.FunctionDef)};currentmethods={n.name:n for n in klass(newtest).body if isinstance(n,ast.FunctionDef)}
assert all(D(n)==D(currentmethods[name])for name,n in originalmethods.items());assert set(currentmethods)-set(originalmethods)=={'test_initial_genuine_wrong_batch_method_role_refuses','test_initial_genuine_expected_function_bound_to_foreign_owner_refuses'}
assert (B/'run_collector_v7_proof.py').read_text().replace(",'batch_callback_identity'",'')==(epoch/'run_collector_v7_proof.py').read_text()
formal_path=QA/'thumbnail-v7-callback-formal-before-runtime-v2/report.json';formal=json.loads(formal_path.read_text())
assert formal['result']=='pass'and formal['named']==21 and formal['samples']==2000 and formal['steps']==100 and formal['beforeCollectorRuntimeCorrection']
assert formal['moduleBindingBeforeSHA256']==sha(epoch/'module_binding.py')
for n,h in formal['modelSHA256'].items():assert sha(B/n)==h
assert all(c['exitCode']==0 and sha(c['log'])==c['sha256']for c in formal['checks'])
for n in ('initial_callback_probe.py','initial_callback_owner_probe_v2.py','focused.py'):assert sha(OUT/n)==sha(OUT.with_name('thumbnail-v7-agent-review-v1')/n)

row=dict(result='pass',classification='all seven retained wrong-function/foreign-owner operations refused before usable, genuine positive bindings accepted',sourceAndExistingTests='pass',collector=str(B),proof=str(PROOF),proofSHA256=sha(PROOF),fullProof=dict(python=120,named=109,models=10,commands=31,sourceWitnesses=len(sources)),focused=dict(pythonTests=31,stdoutSHA256=sha(OUT/'focused.py.stdout.log'),stderrSHA256=sha(OUT/'focused.py.stderr.log')),sourceConservation=dict(inherited=416,unchanged=408,declaredChanges=changed,originalCheckCallASTsExact=counts,completeBaselineAndFaultMainInverseExact=True,actualCaptureRetirementObserverByteExact=True),candidateManifest=str(manifest),candidateManifestSHA256=sha(manifest),candidateClosure=dict(inputs=15238,modes=15238,links=158,fullBytesModesLinksExact=True),counterexamples=counterpaths,acceptedWrongInitialBindings=accepted,correctedCallbackIdentityReviewed=True,formalBeforeRuntime=dict(path=str(formal_path),sha256=sha(formal_path),named=21),retainedV1ReviewSHA256=sha(OUT.with_name('thumbnail-v7-agent-review-v1')/'review.json'),exactRetainedProbeSourcesReplayed=True,soleRuntimeCorrectionFunction='batch_relations',originalPositiveTestASTsRetained=True,guiPairingSourceReady=True,nativeLaunch=False,candidateEdited=False,original38Accepted=False,original34FaultsAccepted=False)
with os.fdopen(os.open(OUT/'review.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in row.items()if k not in('sourceConservation','counterexamples')}));print('reviewSHA256',sha(OUT/'review.json'))
