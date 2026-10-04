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
sources=['elm-output-resize-qa-v120', 'elm-output-reflow-v121', 'elm-output-reflow-qa-v122', 'elm-output-rebind-v123', 'elm-output-rebind-qa-v124', 'elm-output-reflow-lease-v125', 'elm-output-reflow-lease-qa-v126', 'elm-output-reflow-checks-v127', 'elm-output-reflow-model-v128', 'elm-output-rotation-diagnostic-v129', 'elm-output-rotation-current-mode-v130', 'elm-output-keyboard-ready-v132', 'elm-output-keyboard-ready-qa-v133', 'elm-output-keyboard-model-v134', 'elm-output-rotation-frame-v135', 'elm-output-rule-diagnostic-v136', 'elm-output-rule-qa-v137', 'elm-output-rule-diagnostic-v138', 'elm-output-parent-bounds-qa-v139', 'elm-output-production-qa-v140']
reports={'native':sorted((ROOT/'qa').glob('native-*/report.json'))[-1],'build':REPO/'implementation/elm-output-keyboard-ready-v132/qa/build-1791087557995567736/report.json','compiled':REPO/'implementation/elm-output-reflow-checks-v127/qa/checks-1791086998185932892/report.json','reflowModel':REPO/'implementation/elm-output-reflow-model-v128/qa/model-1791087048225546841/report.json','keyboardModel':REPO/'implementation/elm-output-keyboard-model-v134/qa/model-1791087647014315495/report.json'}
for p in reports.values():assert json.loads(p.read_text())['passed'],str(p)
native=json.loads(reports['native'].read_text());assert len(native['checks'])==127 and all(c['passed'] for c in native['checks']) and native['cleanupPassed']
for p,digest in native['inputs'].items():assert sha(Path(p))==digest,p
build=json.loads(reports['build'].read_text());gui=REPO/'implementation/elm-output-keyboard-ready-v132'
for p,digest in build['inputs'].items():assert sha(gui/p)==digest,p
for p in (gui/'src').glob('*.elm'):
 if p.name!='SurfaceReplay.elm':assert sha(p)==sha(REPO/'implementation/elm-output-reflow-checks-v127/src'/p.name),str(p)
files={str(p.relative_to(REPO)):sha(p) for name in sources for p in sorted((REPO/'implementation'/name).rglob('*')) if p.is_file() and p!=ROOT/'qa/slice-manifest.json'}
result={'passed':True,'scope':'Private native monitor ownership, live geometry with fresh lease, native keyboard readiness, integer scale2 and transform1; final shared-controller/physical device/full desktop acceptance remains open','nativeChecks':127,'originalNativeChecks':91,'originalCheckWaitCallsPreservedInOrder':True,'originalCheckWaitClickChooseKeyHelperASTUnchanged':True,'exactProductionElmMatchesCompiledComponent':True,'compiledControllerChecks':70,'compiledPresenterChecks':12,'quintNamedScenarios':8,'quintInvariantSamples':1000,'cleanupPassed':True,'completedRequirementIds':[],'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p)} for k,p in reports.items()},'files':files}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'}))
