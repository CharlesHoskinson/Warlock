import ast,hashlib,importlib.util,json,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OLD=REPO/'implementation/elm-responsive-geometry-v288'
OUT=ROOT/'qa'/('preflight-'+str(time.time_ns()));OUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n):return ast.dump(n,include_attributes=False)
a=ast.parse((OLD/'qa/native.py').read_text());b=ast.parse((ROOT/'qa/native.py').read_text())
def checks(t):return [dump(n) for n in ast.walk(t) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='check']
def corrected(n):
 if isinstance(n,ast.Subscript) and isinstance(n.value,ast.Name) and n.value.id=='replacement' and isinstance(n.slice,ast.Constant) and n.slice.value=='address':n.slice.value='stableId'
 if isinstance(n,ast.Subscript) and isinstance(n.value,ast.Subscript) and isinstance(n.value.value,ast.Name) and n.value.value.id=='report' and isinstance(n.value.slice,ast.Constant) and n.value.slice.value=='fixtureIdentity' and isinstance(n.slice,ast.Constant) and n.slice.value=='address':n.slice.value='stableId'
 return n
class Correction(ast.NodeTransformer):
 def visit_Call(self,n):
  if isinstance(n.func,ast.Name) and n.func.id=='check' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='retirementNeverTargetsSameTitleReplacement':
   for x in ast.walk(n):corrected(x)
  return n
Correction().visit(a)
assert checks(a)==checks(b),'Original288 assertions changed'
assert (ROOT/'IDENTITY-CONTRACT.md').is_file()
def find(t,name):return next(n for n in ast.walk(t) if isinstance(n,ast.FunctionDef) and n.name==name)
for name in ['wait','parent_pointer','open_menu','settle_menu','geometry_row']:assert dump(find(a,name))==dump(find(b,name)),name
assert sha(OLD/'qa/client_evidence.py')==sha(ROOT/'qa/client_evidence.py')
assert sha(OLD/'qa/observer_endpoint.py')==sha(ROOT/'qa/observer_endpoint.py')
r={'passed':False,'scope':'Exact original100 assertion/deadline/ACK/RGB AST and actual coherent tuple source closure only; no native acceptance','inputs':{str(p):sha(p) for p in [ROOT/'qa/native.py',ROOT/'qa/client_evidence.py',ROOT/'qa/observer_endpoint.py',ROOT/'qa/relay-manifest.json',Path(__file__).resolve()]}}
try:
 spec=importlib.util.spec_from_file_location('current_joint_preflight',ROOT/'qa/native.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 build,pair,pointer,fixture=module.preflight()
 src=module.BUILD.parent/'inputs/adapter/endpoint.py';o=find(ast.parse(src.read_text()),'request');c=find(ast.parse((ROOT/'qa/observer_endpoint.py').read_text()),'request');c.body[0]=o.body[0];assert dump(c)==dump(o),'Observer transport drift'
 from closure import verify_profiles
 profiles=verify_profiles(ROOT)
 r['inputs'].update(module.CURRENT_INPUTS);r['inputs'].update(profiles['profileConfigSHA256'])
 r.update(passed=True,pair=pair['nativePair'],originalAssertions=len(checks(a)),pointer=str(pointer),observerTransportOriginSHA256=sha(src),profiles=profiles)
except Exception as error:r['error']=repr(error)
(ROOT/'qa/preflight-result.json').write_text(json.dumps({'report':str(OUT/'report.json')})+'\n')
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
