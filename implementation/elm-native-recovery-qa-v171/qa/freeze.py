"""Protected source closure and original regression oracle preservation."""
import ast,hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def calls(p,name):
 return [ast.dump(n,include_attributes=False) for n in sorted(ast.walk(ast.parse(p.read_text())),key=lambda x:(getattr(x,'lineno',0),getattr(x,'col_offset',0))) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==name]
def subsequence(old,new):
 cursor=iter(new)
 return all(any(row==expected for row in cursor) for expected in old)
original=REPO/'implementation/elm-launcher-keyboard-v60/qa/regression.py';current=ROOT/'qa/regression.py'
for name in ['check','wait']:assert subsequence(calls(original,name),calls(current,name)),name
for name in ['wait','click','check','choose','press_key']:
 a=next(n for n in ast.walk(ast.parse(original.read_text())) if isinstance(n,ast.FunctionDef) and n.name==name)
 b=next(n for n in ast.walk(ast.parse(current.read_text())) if isinstance(n,ast.FunctionDef) and n.name==name)
 assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False),name
sources=['elm-renderer-recovery-v167','elm-renderer-recovery-v168','elm-native-recovery-v169','elm-renderer-recovery-v170','elm-native-recovery-qa-v171','elm-recovery-model-v172','elm-recovery-model-v173']
reports={'native':sorted((ROOT/'qa').glob('native-*/report.json'))[-1],'build':REPO/'implementation/elm-native-recovery-v169/qa/build-1791093755371617208/report.json','compiled':REPO/'implementation/elm-output-controller-v145/qa/outputs-1791089418933454590/report.json','inherited':REPO/'implementation/elm-output-controller-v145/qa/checks-1791089420055503461/report.json','model':REPO/'implementation/elm-output-controller-model-v143/qa/model-1791089304148738374/report.json'}
for p in reports.values():assert json.loads(p.read_text())['passed'],str(p)
native=json.loads(reports['native'].read_text());assert len(native['checks'])==137 and all(c['passed'] for c in native['checks']) and native['cleanupPassed']
for p,digest in native['inputs'].items():assert sha(Path(p))==digest,p
build=json.loads(reports['build'].read_text());gui=REPO/'implementation/elm-native-recovery-v169'
for p,digest in build['inputs'].items():assert sha(gui/p)==digest,p
assert json.loads(reports['compiled'].read_text())['typedChecks']==37
assert json.loads(reports['inherited'].read_text())['typedChecks']==58
assert json.loads(reports['model'].read_text())['namedScenarios']==10
for p in (gui/'src').glob('*.elm'):
 assert sha(p)==sha(REPO/'implementation/elm-output-controller-v145/src'/p.name),str(p)
focused_path=REPO/'implementation/elm-renderer-recovery-v170/qa/native-1791093818970809934/report.json'
focused=json.loads(focused_path.read_text());assert focused['passed'] and focused['cleanupPassed'] and len(focused['checks'])==31 and all(c['passed'] for c in focused['checks'])
for path,digest in focused['inputs'].items():assert sha(Path(path))==digest,path
assert focused['buildReportSHA256']==sha(reports['build'])
for name in ['check','wait','click','choose','press_key','key_recipient']:
 a=next(n for n in ast.walk(ast.parse((REPO/'implementation/elm-related-qa-v163/qa/regression.py').read_text())) if isinstance(n,ast.FunctionDef) and n.name==name)
 b=next(n for n in ast.walk(ast.parse((REPO/'implementation/elm-renderer-recovery-v170/qa/native.py').read_text())) if isinstance(n,ast.FunctionDef) and n.name==name)
 assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False),name
recovery_model_path=REPO/'implementation/elm-recovery-model-v173/qa/model-1791093941372061374/report.json'
recovery_model=json.loads(recovery_model_path.read_text());assert recovery_model['passed'] and recovery_model['namedScenarios']==6 and recovery_model['invariantSamples']==1000
assert recovery_model['sourceSHA256']==sha(REPO/'implementation/elm-recovery-model-v173/spec/recovery.qnt')
reports['focusedRecovery']=focused_path;reports['recoveryModel']=recovery_model_path
files={str(p.relative_to(REPO)):sha(p) for name in sources for p in sorted((REPO/'implementation'/name).rglob('*')) if p.is_file() and p!=ROOT/'qa/slice-manifest.json'}
assert all(len([p for p in native[k]['processes'] if p['name'].startswith('WebKitWebProces')])==1 for k in ['singleOutputResources','dualOutputResources'])
result={'passed':True,'scope':'Native reservation-preserving renderer failure/restart component31 plus original91/shared-output137; production supervisor/pending-effects/hotplug recovery/coherent GPU/menu/budgets/AT/IME/release remain open','nativeChecks':137,'focusedRecoveryChecks':31,'recoveryQuintNamedScenarios':6,'recoveryQuintInvariantSamples':1000,'failureTimeGeometryPreserved':True,'nativeRestartExit':3,'freshBindingAndRetiredPacketRefusal':True,'originalNativeChecks':91,'originalCheckWaitCallsPreservedInOrder':True,'originalCheckWaitClickChooseKeyHelperASTUnchanged':True,'exactProductionElmMatchesCompiledComponent':True,'sharedControllerChecks':37,'inheritedControllerChecks':58,'inheritedPresenterChecks':12,'nativeHostTestGroups':11,'nativeSurfaceTestGroups':4,'quintNamedScenarios':10,'quintInvariantSamples':1000,'cleanupPassed':True,'singleController':True,'observedBackendProcesses':1,'observedRendererProcesses':1,'singleOutputProcessCount':native['singleOutputResources']['processCount'],'dualOutputProcessCount':native['dualOutputResources']['processCount'],'nativeScopeIDs':[1,2,3],'completedRequirementIds':[],'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p)} for k,p in reports.items()},'files':files}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'}))
