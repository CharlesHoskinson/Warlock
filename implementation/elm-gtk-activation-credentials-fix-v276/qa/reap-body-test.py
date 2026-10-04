"""Compile the actual nested production reap body with hostile kernel boundary doubles."""
import ast,copy,hashlib,json,os,resource,sys,time
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;source=ROOT/'activation-supervisor.py';tree=ast.parse(source.read_text());node=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='reap');code=compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec');OUT=ROOT/('reap-body-'+str(time.time_ns()));OUT.mkdir();checks=[];report={'passed':False,'nativeAcceptance':False,'actualProductionBodyKernelDoubles':True,'checks':checks}
try:
 for name in ('correct','new-adopted','wrong-pid','wrong-start','wrong-uid','wrong-parent','wrong-waitpid','wrong-status'):
  original={'pid':200,'start':'123','pgid':100,'ppid':100,'uid':os.getuid()};row=copy.deepcopy(original);pending=SimpleNamespace(si_pid=200,si_uid=os.getuid(),si_code=os.CLD_EXITED,si_status=0)
  if name=='wrong-pid':row['pid']=201
  if name=='wrong-start':row['start']='124'
  if name=='wrong-uid':pending.si_uid+=1
  if name=='wrong-parent':row['ppid']=99
  if name=='wrong-status':pending.si_status=7
  events=[];calls=[];queue=[pending,None];statuses={};known={} if name=='new-adopted' else {(200,'123'):original}
  boundary=SimpleNamespace(P_ALL=os.P_ALL,WEXITED=os.WEXITED,WNOHANG=os.WNOHANG,WNOWAIT=os.WNOWAIT,CLD_EXITED=os.CLD_EXITED,CLD_KILLED=os.CLD_KILLED,CLD_DUMPED=os.CLD_DUMPED,
   waitid=lambda *_:queue.pop(0),waitpid=lambda pid,flags:(calls.append((pid,flags)) or (201 if name=='wrong-waitpid' else 200,0)),waitstatus_to_exitcode=os.waitstatus_to_exitcode)
  scope={'os':boundary,'identity':lambda _:row,'own':{'pid':100},'key':lambda r:(r['pid'],r['start']),'known':known,'statuses':statuses,'emit':lambda kind,**fields:events.append({'kind':kind,**fields}),'child':SimpleNamespace(pid=200,returncode=None)}
  exec(code,scope);refused=False
  try:scope['reap']()
  except RuntimeError:refused=True
  assert refused is (name not in ('correct','new-adopted')),name
  if name in ('wrong-pid','wrong-start','wrong-uid','wrong-parent'):assert calls==[],name
  if name=='wrong-status':assert statuses[(200,'123')]==0 and events[-1]['waitStatus']==0,name
  if name=='new-adopted':assert [r['kind'] for r in events]==['owned-child','kernel-child-acquired','child-exit'],name
  checks.append({'name':name,'passed':True,'consumed':calls,'events':events})
 report['passed']=True
finally:
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),source]};report['productionBodyAST']=ast.dump(node,include_attributes=False);(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
