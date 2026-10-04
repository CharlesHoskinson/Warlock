"""Preserve source closure and original regression oracle audit; protected QA only."""
import ast,hashlib,json,resource
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1]; REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def calls(p,name):
 tree=ast.parse(p.read_text())
 return [ast.dump(n,include_attributes=False) for n in sorted(ast.walk(tree),key=lambda x:(getattr(x,'lineno',0),getattr(x,'col_offset',0))) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==name]
original=REPO/'implementation/elm-launcher-keyboard-v60/qa/regression.py';current=ROOT/'qa/regression.py'
a=calls(original,'check');b=calls(current,'check');extra=[x for x in b if 'focusedMinimizeStillRefusesActivePopupGrab' in x];assert len(extra)==1;assert a==[x for x in b if x not in extra]
assert calls(original,'wait')==calls(current,'wait')
reports={
'native':ROOT/'qa/native-1791083985715685668/report.json',
'elm':REPO/'implementation/elm-popup-choice-barrier-v87/qa/checks-1791083450858131226/report.json',
'build':REPO/'implementation/elm-popup-choice-barrier-v87/qa/build-1791083797888605998/report.json',
'grabModel':REPO/'implementation/elm-grab-safe-background-v89/qa/model-1791083671200862275/report.json',
'choiceModel':REPO/'implementation/elm-choice-model-v95/qa/model-1791084222169195095/report.json'}
for p in reports.values():assert json.loads(p.read_text())['passed'],str(p)
native=json.loads(reports['native'].read_text());assert len(native['checks'])==92 and all(x['passed'] for x in native['checks']) and native['cleanupPassed']
for path,digest in native['inputs'].items():assert sha(Path(path))==digest,path
pair=REPO/'implementation/elm-grab-safe-background-v89/qa/build-pair-manifest.json'
for path,digest in json.loads(pair.read_text())['files'].items():assert sha(pair.parents[1]/path)==digest,path
sources=['elm-surface-inspection-v83','elm-surface-regression-qa-v84','elm-surface-inspection-v85','elm-surface-regression-qa-v86','elm-popup-choice-barrier-v87','elm-surface-regression-qa-v88','elm-grab-safe-background-v89','elm-surface-regression-qa-v90','elm-surface-regression-qa-v91','elm-surface-regression-qa-v92','elm-surface-regression-qa-v93','elm-choice-model-v94','elm-choice-model-v95']
files={str(p.relative_to(REPO)):sha(p) for name in sources for p in sorted((REPO/'implementation'/name).rglob('*')) if p.is_file() and p!=ROOT/'qa/slice-manifest.json'}
result={'passed':True,'scope':'Bounded private primary Elm bar/presentation-only popup regression; no full desktop, hardware/AT/IME/output or release acceptance','nativeChecks':92,'originalNativeChecks':91,'additionalNativeChecks':1,'originalCheckCallASTOrderAndArgumentsPreserved':True,'originalWaitCallASTOrderAndArgumentsPreserved':True,'cleanupPassed':True,'completedRequirementIds':[],'evidence':{k:{'path':str(p.relative_to(REPO)),'sha256':sha(p)} for k,p in reports.items()},'files':files,'remaining':['Pending-choice timeout and user feedback','Full scene/output/workarea/fullscreen/lock semantics','Actual AT/IME/human usability and hardware cadence','WebGPU qualification and C00 feasibility','Representative compatibility and coherent release tuple']}
(ROOT/'qa/slice-manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'}))
