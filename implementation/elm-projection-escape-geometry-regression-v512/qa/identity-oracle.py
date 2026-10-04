import ast,copy,json,resource,sys,time
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];tree=ast.parse((ROOT/'qa/native.py').read_text())
call=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='check' and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='retirementNeverTargetsSameTitleReplacement')
code=compile(ast.Expression(call.args[1]),'<actual native lifetime assertion>','eval')
base={'client':SimpleNamespace(pid=2),'retired_pid':1,'replacement':{'stableId':'new','fullscreen':0,'fullscreenClient':0,'address':'same'},'report':{'fixtureIdentity':{'stableId':'old','address':'same'}},'replacement_fact':{'incarnation':'2','minimized':False},'identity':'1','count':0,'effectRows':[],'view':{'menu':None}}
def evaluate(v):return eval(code,{'__builtins__':{}},dict(v,effects=lambda:v['effectRows'],coherent=lambda:v['view'],len=len))
checks=[{'name':'same address new actual lifetime accepted','passed':evaluate(base)}]
changes=[('old PID',lambda v:setattr(v['client'],'pid',1)),('old stableId',lambda v:v['replacement'].update(stableId='old')),('old incarnation',lambda v:v['replacement_fact'].update(incarnation='1')),('native maximize',lambda v:v['replacement'].update(fullscreen=1)),('client maximize',lambda v:v['replacement'].update(fullscreenClient=1)),('minimized',lambda v:v['replacement_fact'].update(minimized=True)),('effect replay',lambda v:v['effectRows'].append({})),('stale menu',lambda v:v['view'].update(menu={}))]
for name,change in changes:
 v=copy.deepcopy(base);change(v);checks.append({'name':name+' rejected','passed':not evaluate(v)})
assert all(c['passed'] for c in checks)
out=ROOT/'qa'/('identity-'+str(time.time_ns()));out.mkdir();(out/'report.json').write_text(json.dumps({'passed':True,'scope':'Actual432 retirement assertion evaluated with independent lifetime/replay/mode mutants; no native acceptance','checks':checks},indent=2)+'\n');print(str(out/'report.json'))
