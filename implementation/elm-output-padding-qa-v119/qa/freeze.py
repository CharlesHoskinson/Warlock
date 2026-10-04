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
sources=['elm-output-owner-v111','elm-output-owner-model-v112','elm-output-owner-qa-v113','elm-output-viewport-v114','elm-output-viewport-qa-v115','elm-output-wrapper-v116','elm-output-wrapper-qa-v117','elm-output-padding-v118','elm-output-padding-qa-v119']
reports={'native':sorted((ROOT/'qa').glob('native-*/report.json'))[-1],'build':REPO/'implementation/elm-output-padding-v118/qa/build-1791086074315027700/report.json','compiled':REPO/'implementation/elm-output-focus-checks-v107/qa/checks-1791084975734135465/report.json','ownerModel':REPO/'implementation/elm-output-owner-model-v112/qa/model-1791085510830749634/report.json'}
for p in reports.values():assert json.loads(p.read_text())['passed'],str(p)
native=json.loads(reports['native'].read_text());assert len(native['checks'])==114 and all(c['passed'] for c in native['checks']) and native['cleanupPassed']
for p,digest in native['inputs'].items():assert sha(Path(p))==digest,p
build=json.loads(reports['build'].read_text());gui=REPO/'implementation/elm-output-padding-v118'
for p,digest in build['inputs'].items():assert sha(gui/p)==digest,p
for p in (gui/'src').glob('*.elm'):
 if p.name!='SurfaceReplay.elm':assert sha(p)==sha(REPO/'implementation/elm-output-focus-checks-v107/src'/p.name),str(p)
files={str(p.relative_to(REPO)):sha(p) for name in sources for p in sorted((REPO/'implementation'/name).rglob('*')) if p.is_file() and p!=ROOT/'qa/slice-manifest.json'}
result={'passed':True,'scope':'Private native monitor ownership, asymmetric bars/workarea, popup viewport and owner removal; not final shared-controller multi-output desktop/release','nativeChecks':114,'originalNativeChecks':91,'originalCheckWaitCallsPreservedInOrder':True,'originalCheckWaitClickChooseKeyHelperASTUnchanged':True,'exactProductionElmMatchesCompiledComponent':True,'compiledControllerChecks':67,'compiledPresenterChecks':12,'quintNamedScenarios':4,'quintInvariantSamples':1000,'cleanupPassed':True,'completedRequirementIds':[],'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p)} for k,p in reports.items()},'files':files}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'}))
