"""Protected CPU-only exact tuple and unchanged scenario/deadline checks; never run()."""
import ast,copy,hashlib,importlib.util,json,resource,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];PARENT=REPO/'implementation/elm-geometry-menu-native-v67'
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
OUT=ROOT/'qa'/('preflight-'+str(time.time_ns()));OUT.mkdir();INPUT=OUT/'inputs';INPUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[ROOT/'core_host.py',ROOT/'candidate_host.py',ROOT/'aq-tuple.json',ROOT/'native-build-report.json',ROOT/'upstream.json',ROOT/'qa/native.py',ROOT/'qa/client_evidence.py',Path(__file__)]
rows={str(p.relative_to(ROOT)):sha(p) for p in files}
for p in files:
 dest=INPUT/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
checks=[];report={'passed':False,'scope':'Native runner source/deadline and actual owning tuple preflight only; no GUI, physical operation or native acceptance','inputs':rows,'checks':checks}
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def tree(p):return ast.parse(p.read_text())
def find(t,name):return next(x for x in ast.walk(t) if isinstance(x,(ast.FunctionDef,ast.ClassDef)) and x.name==name)
def dump(x):return ast.dump(x,include_attributes=False)
try:
 before=tree(PARENT/'qa/native.py');after=tree(ROOT/'qa/native.py')
 for name in ['check','wait','frames','projection','incoming','effects','geometry','geometry_row','coherent','row','parent_pointer','open_menu','action','settle_menu']:
  check('unchanged original function '+name,dump(find(before,name))==dump(find(after,name)))
 def normalized(t):
  run=copy.deepcopy(find(t,'run'))
  class Normalize(ast.NodeTransformer):
   def visit_Assign(self,node):
    if any(isinstance(x,ast.Name) and x.id=='paths' for x in node.targets):return None
    if any(isinstance(x,ast.Subscript) and isinstance(x.value,ast.Name) and x.value.id=='report' and isinstance(x.slice,ast.Constant) and x.slice.value=='partialScenarios' for x in node.targets):return None
    return self.generic_visit(node)
   def visit_Expr(self,node):
    c=node.value
    if isinstance(c,ast.Call) and isinstance(c.func,ast.Name) and c.func.id=='settle_menu' and any(k.arg=='held' and isinstance(k.value,ast.Constant) and k.value.value is True for k in c.keywords):return None
    return self.generic_visit(node)
  return dump(Normalize().visit(run))
 check('run scenario assertions preserved except source capture and deferred partial09',normalized(before)==normalized(after))
 check('client evidence byte exact ancestral helper',sha(ROOT/'qa/client_evidence.py')==sha(PARENT/'qa/client_evidence.py'))
 u=json.loads((ROOT/'upstream.json').read_text())
 check('exact original runner source retained',sha(Path(u['parentRunner']))==u['parentRunnerSHA256'])
 check('scenario09 explicitly deferred not accepted',u['scope09'].startswith('unexecuted/unqualified'))
 hostbefore=tree(Path(u['originalCoreHost']));hostafter=tree(ROOT/'core_host.py')
 for name in ['aq_tuple','verify_inputs','launch','wait_socket','__init__','__enter__']:
  check('private host protection unchanged '+name,dump(find(hostbefore,name))==dump(find(hostafter,name)))
 spec=importlib.util.spec_from_file_location('v77_native_preflight',ROOT/'qa/native.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
 build,pair,pointer,fixture=runner.preflight()
 check('actual V74 staged CPU build passed',build['passed'] is True and build['postCloseChecks']['checks']==59)
 check('fresh exact V73 core selected',pair['nativePair']['core']['sha256']=='f1430c86174efa5682c40545daa3c7d823e29943ef07f8c992da59a0641617ad')
 check('fresh exact V75 plugin selected',pair['nativePair']['plugin']['sha256']=='c0bf07547a943e48d5493bc2df490a27c91c2e8def6060150fb59237ade5e20c')
 aq,lib=runner.host.base.aq_tuple();check('exact private V30 AQ selected',sha(lib)=='1763ba3b38832b67ed70d9470661cdc18073ca0924f1ef962ffcbf61cf754ff5')
 module,client,probe=runner.host.input_tuple();check('fixed V14 module/client qualification retained',probe['nativeChecks']==105 and Path(pointer)==client)
 runner.host.base.verify_inputs();check('original Weston/AQ compatibility inputs unchanged',True)
 report['selectedTuple']={'core':pair['nativePair']['core'],'plugin':pair['nativePair']['plugin'],'aq':aq,'fixedParentInputManifest':runner.host.EXPECTED_INPUT_MANIFEST,'stagedBuild':str(runner.BUILD),'stagedBuildSHA256':runner.BUILD_HASH}
 for rel,digest in rows.items():check('source held during preflight '+rel,sha(ROOT/rel)==digest)
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])
