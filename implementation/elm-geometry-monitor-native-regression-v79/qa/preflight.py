"""Run the actual runner's preflight AST, stopping before any private host launch."""
import ast,hashlib,json,sys,time,traceback
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
RUNNER=Path(__file__).with_name('native.py');OUT=RUNNER.parent/('preflight-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
source=RUNNER.read_bytes();tree=ast.parse(source);nodes=[]
for node in tree.body:
    if isinstance(node,ast.Try):
        for child in node.body:
            if isinstance(child,ast.With):break
            nodes.append(child)
        break
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='OUT' for t in node.targets):continue
    if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and isinstance(node.value.func.value,ast.Name) and node.value.func.value.id=='OUT':continue
    nodes.append(node)
program=ast.Module(body=nodes,type_ignores=[])
r={'passed':False,'nativeAcceptance':False,'scope':'Actual native runner source/build preflight only; no GUI','runner':str(RUNNER),'runnerSHA256':hashlib.sha256(source).hexdigest()}
namespace={'__file__':str(RUNNER),'__name__':'protected_geometry_preflight','OUT':OUT}
try:
    exec(compile(program,str(RUNNER),'exec'),namespace)
    assert RUNNER.read_bytes()==source
    r['passed']=True;r['selectedInputs']=namespace['report']['inputs'];r['pluginSHA256']=namespace['report']['pluginSHA256'];r['coreBuild']=namespace['report']['coreBuild']
except Exception as error:r.update(error=repr(error),traceback=traceback.format_exc())
r['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file()}
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}),flush=True)
raise SystemExit(not r['passed'])
