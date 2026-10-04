"""Execute actual GTK02 body with wrapped endpoint DTOs and mocked native state."""
import ast,copy,hashlib,json,resource,sys,time
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from driver import Refused,remaining
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'qa'/('geometry-reply-'+str(time.time_ns()));out.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=(ROOT/'qa/driver.py').read_text()
def method(text):
 tree=ast.parse(text);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Driver');fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='GTK02')
 namespace={'remaining':remaining};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<actual-GTK02>','exec'),namespace);return namespace['GTK02']
def execute(fn):
 state={'max':False,'ack':1};checks=[];captures=[]
 ordinary=dict(incarnation='23',geometry=[40,90,320,180],workspace='1',monitor='0',minimized=False,shouldRenderAny=True,shouldRenderOwnMonitor=True,acceptsInput=True)
 def binding(role,*unused):
  assert role=='A'
  return {'identity':{'instance':1,'mapGeneration':1,'surfaceId':42},'gtk':{'observedMaximized':state['max']},'native':{'at':[0,0] if state['max'] else [40,90],'size':[800,600] if state['max'] else [320,180],'workspace':{'id':1},'monitor':0},'wire':{'ack':{'serial':state['ack']}}}
 def send(op,role):assert role=='A' and op in ('maximize','unmaximize');state.update(max=op=='maximize',ack=state['ack']+1)
 def facts(request):
  target={'incarnation':'23','capabilities':{'maximize':False},'nativeMode':'maximized' if state['max'] else 'normal','clientMode':'maximized' if state['max'] else 'normal'}
  return {'kind':'geometry-facts','requestId':request,'facts':{'windows':[{'incarnation':'999','capabilities':{'maximize':False},'nativeMode':'normal','clientMode':'normal'},target]}}
 def checked(name,value,**unused):assert value,name;checks.append(name)
 def wait(fn):value=fn();assert value,'mock native transition not observed';return value
 def refuse(before,target,op,deadline):assert target=='23' and op=='maximize' and deadline>time.monotonic()
 s=SimpleNamespace(fact=lambda role:copy.deepcopy(ordinary),binding=binding,read_id=0,endpoint=SimpleNamespace(geometry_facts=facts),deadline=time.monotonic()+1,report={'openGates':[]},shell=SimpleNamespace(refuse_unavailable=refuse,journal=lambda:[]),check=checked,send=send,wait=wait,stable_capture=lambda *args:captures.append(args),drafts=lambda *args:None)
 fn(s)
 assert len(checks)==3 and len(captures)==2 and len(s.report['openGates'])==1 and s.report['geometryOrdinary']['incarnation']=='23'
 return {'checks':checks,'captures':len(captures),'openPositiveGatesRetained':len(s.report['openGates'])}
report={'passed':False,'nativeAcceptance':False,'mockedNativeState':True,'controls':[]}
try:
 report['actualBody']=execute(method(source))
 for name,changed in [('first-reply-top-level',source.replace("g['facts']['windows']","g['windows']")),('second-reply-top-level',source.replace("geo['facts']['windows']","geo['windows']")),('wrong-first-incarnation',source.replace("next(w for w in geo['facts']['windows'] if w['incarnation']==ordinary['incarnation'])","geo['facts']['windows'][0]"))]:
  try:execute(method(changed))
  except (KeyError,AssertionError):report['controls'].append({'name':name,'refused':True})
  else:raise AssertionError('unsafe geometry boundary accepted '+name)
  (out/(name+'.py')).write_text(changed)
 report.update(passed=True,sourceSHA256=sha(ROOT/'qa/driver.py'))
finally:
 (out/'driver.py').write_text(source);(out/'test.py').write_bytes(Path(__file__).read_bytes());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
