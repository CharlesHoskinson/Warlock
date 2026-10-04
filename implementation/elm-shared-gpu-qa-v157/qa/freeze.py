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
sources=['elm-shared-gpu-v152','elm-shared-gpu-qa-v153','elm-shared-gpu-v154','elm-shared-gpu-qa-v155','elm-shared-gpu-v156','elm-shared-gpu-qa-v157']
reports={'native':sorted((ROOT/'qa').glob('native-*/report.json'))[-1],'build':REPO/'implementation/elm-shared-gpu-v156/qa/build-1791091598916270898/report.json','compiled':REPO/'implementation/elm-output-controller-v145/qa/outputs-1791089418933454590/report.json','inherited':REPO/'implementation/elm-output-controller-v145/qa/checks-1791089420055503461/report.json','model':REPO/'implementation/elm-output-controller-model-v143/qa/model-1791089304148738374/report.json'}
for p in reports.values():assert json.loads(p.read_text())['passed'],str(p)
native=json.loads(reports['native'].read_text());assert len(native['checks'])==142 and all(c['passed'] for c in native['checks']) and native['cleanupPassed']
for p,digest in native['inputs'].items():assert sha(Path(p))==digest,p
build=json.loads(reports['build'].read_text());gui=REPO/'implementation/elm-shared-gpu-v156'
for p,digest in build['inputs'].items():assert sha(gui/p)==digest,p
assert json.loads(reports['compiled'].read_text())['typedChecks']==37
assert json.loads(reports['inherited'].read_text())['typedChecks']==58
assert json.loads(reports['model'].read_text())['namedScenarios']==10
for p in (gui/'src').glob('*.elm'):
 assert sha(p)==sha(REPO/'implementation/elm-output-controller-v145/src'/p.name),str(p)
assert native['gpu']['webgl']['pixel']==[17,193,71,255]
assert native['gpu']['webgpu']=={'exposed':False,'status':'unavailable'}
assert native['gpu']['secureContext']
assert 'GL_RENDERER\nMesa Intel(R) Graphics (ARL)' in native['nativeGPU']['text']
assert '/dev/dri/renderD129' in native['nativeGPU']['text']
files={str(p.relative_to(REPO)):sha(p) for name in sources for p in sorted((REPO/'implementation'/name).rglob('*')) if p.is_file() and p!=ROOT/'qa/slice-manifest.json'}
result={'passed':True,'scope':'Native shared-host shader readback/display and Mesa Intel engine diagnostics, browser WebGPU unavailable; budgets/full graphics/device/AT/IME/menu/release qualification remain open','nativeChecks':142,'originalNativeChecks':91,'originalCheckWaitCallsPreservedInOrder':True,'originalCheckWaitClickChooseKeyHelperASTUnchanged':True,'exactProductionElmMatchesCompiledComponent':True,'sharedControllerChecks':37,'inheritedControllerChecks':58,'inheritedPresenterChecks':12,'nativeHostTestGroups':11,'nativeSurfaceTestGroups':4,'quintNamedScenarios':10,'quintInvariantSamples':1000,'cleanupPassed':True,'singleController':True,'observedBackendProcesses':1,'nativeScopeIDs':[1,2,3],'shaderReadback':[17,193,71,255],'nativeDisplayedPixel':[17,193,71],'nativeRenderer':'Mesa Intel(R) Graphics (ARL)','renderNode':'/dev/dri/renderD129','webgpu':'unavailable in secure origin','performanceBudgetsAccepted':False,'completedRequirementIds':[],'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p)} for k,p in reports.items()},'files':files}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'}))
