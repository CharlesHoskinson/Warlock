"""Actual broker handler/main routing with real strict decoders, fake native transport."""
import copy,hashlib,importlib.util,json,resource,shutil,sys,time,traceback
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('routing-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
files=[*sorted((ROOT/'adapter').glob('*.py')),ROOT/'source-lineage.json',ROOT/'SCOPE.md',Path(__file__)]
inputs={str(p.relative_to(ROOT)):sha(p) for p in files}
for p in files:
 dest=OUT/'inputs'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
sys.path.insert(0,str(ROOT/'adapter'))
spec=importlib.util.spec_from_file_location('actual_geometry_daemon',ROOT/'adapter/daemon.py');daemon=importlib.util.module_from_spec(spec);spec.loader.exec_module(daemon)
from endpoint import Refused
from geometry_endpoint import GeometryEndpoint
frames=[];daemon.send=lambda frame:frames.append(copy.deepcopy(frame))
B={'lifetime':'7','session':'8','frontend':'9'}
CAPS={'observe':True,'effects':True,'effectProtocol':2,'operations':['maximize','restore-geometry'],'placementCapacity':256,'canonicalScene':False}
class Fake(GeometryEndpoint):
 def __init__(self):
  self.bound=copy.deepcopy(B);self.geometry_binding=None;self.geometry_capabilities=None;self.calls=[];self.failure=None;self.status='Committed';self.incoherent=False;self.scene_calls=0;self.pid=99;self.instance='private-unit';self.bad_response=False
 def verify_process(self):
  pass  # Synthetic process identity; authentication is explicitly outside this CPU evidence.
 def request(self,payload):
  self.calls.append(copy.deepcopy(payload))
  if self.failure:raise self.failure
  kind=payload['kind']
  if kind=='hello':
   self.bound=None
   return {'protocolVersion':3,'kind':'attached','binding':copy.deepcopy(B),'compositor':{'pid':99,'instance':'private-unit','coreHash':'frozen-fixture'},'capabilities':{'observe':True,'effects':True,'minimizedState':True,'effectProtocol':1,'operations':['minimize','restore','activate'],'canonicalScene':False,'taskbarProjectionProtocol':1,'effectInvalidationProtocol':1}}
  if kind=='geometry-attach':return {'protocolVersion':3,'kind':'geometry-attached','geometryProtocol':1,'binding':copy.deepcopy(self.bound),'requestId':payload['requestId'],'capabilities':copy.deepcopy(CAPS)}
  if kind=='geometry-facts-request':return {'protocolVersion':3,'kind':'geometry-facts','geometryProtocol':1,'binding':copy.deepcopy(self.bound),'requestId':payload['requestId'],'sequence':'12','revision':'13','outputGeneration':'14','facts':{'focused':None,'inputBlocked':False,'windows':[]}}
  if kind=='window-effect':
   receipt={'protocolVersion':3,'kind':'effect-outcome','effectProtocol':payload['effectProtocol'],'binding':copy.deepcopy(self.bound),'intent':copy.deepcopy(payload['intent']),'status':self.status,'reason':'applied' if self.status=='Committed' else 'effect-unproven','revision':'13','outputGeneration':'14'}
   if self.bad_response:receipt['intent']['generation']='999'
   return receipt
  if kind=='snapshot-request':return {'protocolVersion':3,'kind':'snapshot','binding':copy.deepcopy(self.bound),'requestId':payload['requestId'],'sequence':'20','revision':'1','windows':[]}
  if kind=='scene-facts-request':
   self.scene_calls+=1
   return {'protocolVersion':3,'kind':'scene-facts','binding':copy.deepcopy(self.bound),'requestId':payload['requestId'],'sequence':'20','revision':'13' if not self.incoherent or self.scene_calls%2 else '14','outputGeneration':'14','facts':{'focused':None,'windows':[]}}
  raise AssertionError(kind)
class Catalog:
 def __init__(self,*args):self.calls=[]
 def handle(self,request):self.calls.append(copy.deepcopy(request));return {'kind':'catalog-fake-receipt'}
def invoke(client,request):
 before=len(frames);daemon.handle_request(client,Catalog(),copy.deepcopy(request));return frames[before:]
def attach_request(**extra):return {'protocolVersion':3,'kind':'geometry-attach','geometryProtocol':1,'binding':copy.deepcopy(B),'requestId':'1',**extra}
def facts_request(**extra):return {'protocolVersion':3,'kind':'geometry-facts-request','geometryProtocol':1,'binding':copy.deepcopy(B),'requestId':'2','minimumWatermark':'0',**extra}
def effect(version=2,operation='maximize'):
 return {'protocolVersion':3,'kind':'window-effect','effectProtocol':version,'binding':copy.deepcopy(B),'intent':{'request':'18446744073709551615','generation':'18446744073709551615','incarnation':'11','operation':operation,'context':{'lifetime':'7','epoch':'9','output':'14','revision':'13'}}}
checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def rejection(name,request,attached=True):
 client=Fake()
 if attached:client.geometry_binding=copy.deepcopy(B);client.geometry_capabilities=copy.deepcopy(CAPS)
 before=len(frames)
 try:invoke(client,request)
 except (Refused,TypeError,ValueError):pass
 else:raise AssertionError(name+': unexpectedly accepted')
 check(name,len(client.calls)==0 and len(frames)==before)
report={'passed':False,'nativeAcceptance':False,'scope':'Actual imported broker handler/main and copied strict endpoint validators with synthetic transport; no process/socket identity, native mutation, compositor event authentication, configure/pixels or Elm end-to-end acceptance','qaScope':scope,'inputs':inputs,'checks':checks}
try:
 client=Fake();reply=invoke(client,attach_request())
 check('explicit attach forwards exact caller request and receipt once',len(client.calls)==1 and client.calls[0]==attach_request() and reply[0]['kind']=='geometry-attached' and client.geometry_binding==B)
 reply=invoke(client,facts_request());check('zero watermark accepted and caller requestId preserved',client.calls[-1]==facts_request() and reply[0]['requestId']=='2')
 for version,operations in [(1,['minimize','restore','activate']),(2,['maximize','restore-geometry'])]:
  for operation in operations:
   request=effect(version,operation);before=len(client.calls);reply=invoke(client,request)
   check('effect '+str(version)+' '+operation+' preserves full caller IDs and version exactly once',len(client.calls)==before+1 and client.calls[-1]==request and len(reply)==1 and reply[0]['intent']==request['intent'] and reply[0]['effectProtocol']==version)
 client.status='Unknown';reply=invoke(client,effect());check('actual Unknown receipt forwarded without changing to refusal',reply[0]['status']=='Unknown')
 for request in [effect(),{'protocolVersion':3,'kind':'projection-request','binding':copy.deepcopy(B),'requestId':'4'},facts_request()]:
  client.failure=Refused('synthetic transport failure');before=len(client.calls);nframes=len(frames)
  try:invoke(client,request)
  except Refused:pass
  else:raise AssertionError('transport failure accepted')
  check('failure no retry no invented outcome '+request['kind'],len(client.calls)==before+1 and len(frames)==nframes)
 client.failure=None;client.bad_response=True;before=len(client.calls);nframes=len(frames)
 try:invoke(client,effect())
 except Refused:pass
 else:raise AssertionError('uncorrelated outcome accepted')
 check('bad full receipt rejected after one send without fabricated outcome',len(client.calls)==before+1 and len(frames)==nframes)
 # Broker envelopes and actual delegated endpoint intent validators.
 rejection('effect before attach refused without native send',effect(),False)
 bad=effect();bad['effectProtocol']=True;rejection('bool effect version refuses',bad)
 for v in [0,3,'2',None]:bad=effect();bad['effectProtocol']=v;rejection('unknown effect version '+repr(v),bad)
 for request in [attach_request(),facts_request(),effect(),{'protocolVersion':3,'kind':'projection-request','binding':copy.deepcopy(B),'requestId':'3'}]:
  bad=copy.deepcopy(request);bad['protocolVersion']=True;rejection('bool native version '+request['kind'],bad)
  bad=copy.deepcopy(request);bad['binding']['frontend']='10';rejection('stale full binding '+request['kind'],bad)
  bad=copy.deepcopy(request);bad['extra']=0;rejection('extra exact field '+request['kind'],bad)
  bad=copy.deepcopy(request);del bad['binding'];rejection('missing exact field '+request['kind'],bad)
 for request in [attach_request(),facts_request()]:
  for version in [True,0,2,'1']:bad=copy.deepcopy(request);bad['geometryProtocol']=version;rejection('bad geometry version '+request['kind']+repr(version),bad)
  for value in ['0','01','-1','18446744073709551616',1,True]:bad=copy.deepcopy(request);bad['requestId']=value;rejection('requestId canonical positive '+request['kind']+repr(value),bad)
 for value in ['00','-1','18446744073709551616',0,True]:bad=facts_request();bad['minimumWatermark']=value;rejection('watermark allows canonical string zero only '+repr(value),bad)
 for field in ['request','generation','incarnation']:
  for value in ['0','01','-1','18446744073709551616',True]:bad=effect();bad['intent'][field]=value;rejection('strict full effect counter '+field+repr(value),bad)
 for field in ['lifetime','epoch','output','revision']:
  bad=effect();bad['intent']['context'][field]='0';rejection('zero effect context '+field,bad)
 bad=effect();bad['intent']['extra']='x';rejection('extra intent field refuses',bad)
 bad=effect();bad['intent']['context']['extra']='x';rejection('extra full context field refuses',bad)
 bad=effect();bad['intent']['context']['epoch']='10';rejection('stale geometry intent epoch refuses locally',bad)
 for version,operation in [(1,'maximize'),(1,'restore-geometry'),(2,'restore'),(2,'minimize'),(2,'close'),(2,True)]:rejection('unsupported closed operation '+str(version)+repr(operation),effect(version,operation))
 client=Fake();reply=invoke(client,{'protocolVersion':3,'kind':'projection-request','binding':copy.deepcopy(B),'requestId':'7'})
 check('projection uses exact caller requestId in three coherent observations',len(client.calls)==3 and [x['kind'] for x in client.calls]==['scene-facts-request','snapshot-request','scene-facts-request'] and all(x['requestId']=='7' for x in client.calls) and reply[0]['kind']=='action-projection' and reply[0]['requestId']=='7')
 client=Fake();client.incoherent=True;reply=invoke(client,{'protocolVersion':3,'kind':'projection-request','binding':copy.deepcopy(B),'requestId':'7'})
 check('incoherent bracket sends refresh hint only without fabricated facts',reply==[{'protocolVersion':3,'kind':'host-refresh'}])
 rejection('unsupported hello cannot reset authority through broker',{'protocolVersion':3,'kind':'hello'})
 rejection('unsupported native route refuses without send',{'kind':'unknown'})
 # Execute actual framing/main loop with mocked IO and transport, no OS processes.
 class Events:
  def __init__(self,chunks):self.chunks=list(chunks)
  def __enter__(self):return self
  def __exit__(self,*args):return False
  def recv(self,n):return self.chunks.pop(0)
 class Key:
  def __init__(self,data):self.data=data
 class Selector:
  def __init__(self,steps):self.steps=list(steps)
  def __enter__(self):return self
  def __exit__(self,*args):return False
  def register(self,*args):pass
  def select(self,timeout):return [(Key(x),1) for x in self.steps.pop(0)]
 def main_case(name,chunks,steps,event_chunks=None,expect_error=False):
  config=OUT/(name+'.json');config.write_text('{}');saved=(daemon.Endpoint,daemon.CatalogTransport,daemon.event_socket,daemon.selectors.DefaultSelector,daemon.os.read,sys.argv)
  c=Fake();e=Events(event_chunks or []);sel=Selector(steps);data=list(chunks);before=len(frames)
  daemon.Endpoint=lambda **kwargs:c;daemon.CatalogTransport=Catalog;daemon.event_socket=lambda _:e;daemon.selectors.DefaultSelector=lambda:sel;daemon.os.read=lambda fd,n:data.pop(0);sys.argv=['daemon',str(config)]
  error=None
  try:result=daemon.main()
  except Exception as failure:error=failure;result=None
  finally:daemon.Endpoint,daemon.CatalogTransport,daemon.event_socket,daemon.selectors.DefaultSelector,daemon.os.read,sys.argv=saved
  check(name+' error expectation',bool(error)==expect_error)
  emitted=frames[before:];check(name+' authenticated hello precedes geometry prompt',emitted[0]['kind']=='attached' and emitted[1]=={'protocolVersion':3,'kind':'host-geometry-negotiate'})
  return c,emitted,error
 encoded=json.dumps(attach_request()).encode()+b'\n'
 c,out,error=main_case('partial framing waits newline',[encoded[:30],encoded[30:],b''],[['stdin'],['stdin'],['stdin']]);check('partial newline dispatches exactly one attach',len(c.calls)==2 and out[-1]['kind']=='geometry-attached')
 c,out,error=main_case('two complete lines routed once',[encoded+json.dumps(facts_request()).encode()+b'\n',b''],[['stdin'],['stdin']]);check('coalesced lines preserve attach then facts order',[x['kind'] for x in c.calls]==['hello','geometry-attach','geometry-facts-request'])
 c,out,error=main_case('input bound rejects before effect',[b'x'*4097],[['stdin']],expect_error=True);check('input overflow emits no effect or guessed receipt',len(c.calls)==1 and len(out)==2)
 c,out,error=main_case('duplicate JSON key rejects',[b'{"kind":"geometry-attach","kind":"geometry-facts-request"}\n'],[['stdin']],expect_error=True);check('duplicate JSON members reject before native request',len(c.calls)==1)
 projection=json.dumps({'protocolVersion':3,'kind':'projection-request','binding':B,'requestId':'3'}).encode()+b'\n'
 c,out,error=main_case('trusted event produces refresh hint',[projection,b''],[['stdin'],['events'],['stdin']],[b'elmwindowstate>>7\n']);check('event hint never makes geometry facts',[x['kind'] for x in out]==['attached','host-geometry-negotiate','action-projection','host-refresh'] and len(c.calls)==4)
 c,out,error=main_case('event EOF retires transport',[projection],[['stdin'],['events']],[b''],True);check('event loss fabricates no effect receipt',all(x['kind']!='effect-outcome' for x in out))
 for rel,w in inputs.items():assert sha(ROOT/rel)==w,'source changed after capture: '+rel
 report['passed']=all(x['passed'] for x in checks)
except Exception as error:report.update(error=repr(error),traceback=traceback.format_exc())
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(checks),'report':str(OUT/'report.json'),'error':report.get('error')}),flush=True)
raise SystemExit(not report['passed'])
