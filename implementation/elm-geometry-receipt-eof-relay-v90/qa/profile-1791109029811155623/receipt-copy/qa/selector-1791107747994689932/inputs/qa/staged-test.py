"""Actual frozen V64 selector + V78 CLI with synthetic transport, no native claims."""
import copy,hashlib,importlib.util,json,os,resource,shutil,sys,time,traceback
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('staged-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
files=[ROOT/'qa/wrapper.py',ROOT/'qa/broker-entrypoint.py',Path(__file__),ROOT/'upstream.json']
inputs={str(p.relative_to(ROOT)):sha(p) for p in files}
for p in files:
 q=OUT/'inputs'/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
sys.path.insert(0,str(OUT/'inputs/qa'))
import wrapper as w
spec=importlib.util.spec_from_file_location('actual_entrypoint',OUT/'inputs/qa/broker-entrypoint.py');entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(entry)
checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def refused(fn):
 try:fn()
 except (w.HoldFailure,OSError,ValueError):return True
 return False
seq=0
def control():
 global seq
 seq+=1;p=OUT/('control'+str(seq));p.mkdir(mode=0o700);(p/'gate.json').write_text('{"action":"hold"}');(p/'gate.json').chmod(0o600);return p
B={'lifetime':'11','session':'12','frontend':'13'}
I={'request':'14','generation':'15','incarnation':'16','operation':'restore-geometry','context':{'lifetime':'11','epoch':'13','output':'17','revision':'18'}}
R={'protocolVersion':3,'kind':'effect-outcome','effectProtocol':2,'binding':B,'intent':I,'status':'Committed','reason':'applied','revision':'19','outputGeneration':'17'}
report={'passed':False,'checks':checks,'inputs':inputs,'qaScope':scope,'nativeAcceptance':False,'scope':'Actual held broker selector/strict endpoint decoders and wrapper CLI with synthetic native transport, never real execution or facts/pixels acceptance'}
try:
 backend=w.load_backend();check('captured wrapper resolves same exact V74/V64 backend',callable(backend.main))
 originalCached=sys.modules.get('endpoint')
 fake=type('WrongModule',(),{'__file__':str(OUT/'foreign.py')})()
 with patch.dict(sys.modules,{'endpoint':fake}):check('foreign cached endpoint refuses before native transport',refused(w.load_backend))
 p=control();sent=[];h=w.ReceiptHold(p,'16',sent.append,operation='restore-geometry')
 for frame in [dict(R['intent']),{'protocolVersion':3,'kind':'geometry-facts','requestId':'9'}, {'protocolVersion':3,'kind':'action-projection','requestId':'8'}, {'protocolVersion':3,'kind':'host-refresh'}]:h.intercept(frame)
 check('postclose observations and notifications pass before selected operation receipt',len(sent)==4 and not h.seen)
 maximum=copy.deepcopy(R);maximum['intent']['operation']='maximize';h.intercept(maximum);check('other geometry operation passes unchanged',sent[-1]==maximum and not h.seen)
 h.intercept(R);check('explicit RestoreGeometry Committed is held without delivery',h.seen and R not in sent)
 facts={'protocolVersion':3,'kind':'geometry-facts','requestId':'10'};h.intercept(facts);check('facts are not deferred during delivery hold',sent[-1]==facts)
 w.write_release(p);h.poll_gate();h.poll_gate();check('restore geometry exact original receipt released once',sum(x==R for x in sent)==1);h.close()
 for operation in ['restore','minimize',True,None,'RestoreGeometry']:
  check('selector closed operation '+repr(operation),refused(lambda:w.ReceiptHold(control(),'16',lambda _:None,operation=operation)))
 for reason in ['x'*257,'\ud800','bad\n','bad\u0085']:
  h=w.ReceiptHold(control(),'16',lambda _:None,operation='restore-geometry');r=copy.deepcopy(R);r['reason']=reason
  check('strict receipt reason '+repr(reason[:10]),refused(lambda:h.intercept(r)) and not h.seen)
 # Host-compatible private wrapperconfig and entrypoint argument routing.
 p=control();authority=OUT/'authority.json';authority.write_text('{}');authority.chmod(0o600)
 config=OUT/'wrapper.json';value={'authorityConfig':str(authority),'controlDirectory':str(p),'incarnation':'16','effectOperation':'restore-geometry'}
 config.write_text(json.dumps(value));config.chmod(0o600)
 check('strict private host-compatible wrapper configuration',entry.configuration(config)==value)
 captured=[]
 def capture_main():captured.append(list(sys.argv));return 0
 with patch.object(entry,'wrapper_main',capture_main),patch.object(sys,'argv',['broker-entrypoint',str(config)]):check('entrypoint preserves config and explicit operation argv',entry.main()==0 and captured==[['receipt-wrapper','run','--control-directory',str(p),'--incarnation','16','--config',str(authority),'--effect-operation','restore-geometry']])
 for name,change in [('extra',{'extra':1}),('operation',{'effectOperation':'minimize'}),('counter',{'incarnation':'016'}),('missingpath',{'authorityConfig':str(OUT/'missing')}),('pathType',{'controlDirectory':1})]:
  config.write_text(json.dumps(dict(value,**change)));check('private wrapperconfig invalid '+name,refused(lambda:entry.configuration(config)))
 config.write_text(json.dumps(value));config.chmod(0o644);check('public wrapperconfig refused',refused(lambda:entry.configuration(config)));config.chmod(0o600)
 link=OUT/'wrapper-link';link.symlink_to(config);check('symlink wrapperconfig refused',refused(lambda:entry.configuration(link)))
 # Actual backend.main produces observations BEFORE operation; event socket stays
 # live AFTER actual synthetic transport returns its unchanged committed frame.
 class Fake(backend.Endpoint):
  def __init__(self,**kw):self.bound=None;self.pid=99;self.instance='CPU_FIXTURE';self.calls=[]
  def verify_process(self):pass
  def request(self,payload):
   self.calls.append(copy.deepcopy(payload));kind=payload['kind']
   if kind=='hello':return {'protocolVersion':3,'kind':'attached','binding':B,'compositor':{'pid':99,'instance':'CPU_FIXTURE','coreHash':'synthetic'},'capabilities':{'observe':True,'effects':True,'minimizedState':True,'effectProtocol':1,'operations':['minimize','restore','activate'],'canonicalScene':False,'taskbarProjectionProtocol':1,'effectInvalidationProtocol':1}}
   if kind=='geometry-attach':return {'protocolVersion':3,'kind':'geometry-attached','geometryProtocol':1,'binding':B,'requestId':payload['requestId'],'capabilities':{'observe':True,'effects':True,'effectProtocol':2,'operations':['maximize','restore-geometry'],'placementCapacity':256,'canonicalScene':False}}
   if kind=='geometry-facts-request':return {'protocolVersion':3,'kind':'geometry-facts','geometryProtocol':1,'binding':B,'requestId':payload['requestId'],'sequence':'20','revision':'18','outputGeneration':'17','facts':{'focused':None,'inputBlocked':False,'windows':[]}}
   if kind=='scene-facts-request':return {'protocolVersion':3,'kind':'scene-facts','binding':B,'requestId':payload['requestId'],'sequence':'20','revision':'18','outputGeneration':'17','facts':{'focused':None,'windows':[]}}
   if kind=='snapshot-request':return {'protocolVersion':3,'kind':'snapshot','binding':B,'requestId':payload['requestId'],'sequence':'20','revision':'18','windows':[]}
   if kind=='window-effect':return copy.deepcopy(R)
   raise AssertionError(kind)
 class Events:
  def __enter__(self):return self
  def __exit__(self,*a):return False
  def recv(self,n):return b'elmwindowstate>>11\n'
 class Key:
  def __init__(self,data):self.data=data
 class Selector:
  def __enter__(self):return self
  def __exit__(self,*a):return False
  def register(self,*a):pass
  def select(self,timeout):
   tag=steps.pop(0)
   if tag=='release':
    check('actual selector continues observation and refresh while real-shaped receipt held',holder[0].seen and not holder[0].released and any(x['kind']=='host-refresh' for x in sent) and len([x for x in sent if x['kind']=='geometry-facts'])==2 and not any(x['kind']=='effect-outcome' for x in sent))
    w.write_release(p);holder[0].poll_gate();tag='stdin'
   return [(Key(tag),1)]
 requests=[{'protocolVersion':3,'kind':'geometry-attach','geometryProtocol':1,'binding':B,'requestId':'1'}, {'protocolVersion':3,'kind':'projection-request','binding':B,'requestId':'2'}, {'protocolVersion':3,'kind':'geometry-facts-request','geometryProtocol':1,'binding':B,'requestId':'3','minimumWatermark':'0'}, {'protocolVersion':3,'kind':'window-effect','effectProtocol':2,'binding':B,'intent':I}, {'protocolVersion':3,'kind':'geometry-facts-request','geometryProtocol':1,'binding':B,'requestId':'4','minimumWatermark':'0'}]
 chunks=[json.dumps(r).encode()+b'\n' for r in requests]+[b''];steps=['stdin','stdin','stdin','stdin','events','stdin','release'];sent=[];p=control();holder=[];client=Fake();actual_holder=w.ReceiptHold;actual_read=os.read
 def make_holder(*a,**kw):h=actual_holder(*a,**kw);holder.append(h);return h
 with patch.object(backend,'Endpoint',lambda **kw:client),patch.object(backend,'CatalogTransport',lambda *a:None),patch.object(backend,'event_socket',lambda c:Events()),patch.object(backend.selectors,'DefaultSelector',Selector),patch.object(backend.os,'read',lambda fd,n:chunks.pop(0) if fd==0 else actual_read(fd,n)),patch.object(backend,'send',lambda f:sent.append(copy.deepcopy(f))),patch.object(w,'load_backend',lambda:backend),patch.object(w,'ReceiptHold',make_holder),patch.object(sys,'argv',['wrapper','run','--control-directory',str(p),'--incarnation','16','--config',str(authority),'--effect-operation','restore-geometry']):
  check('actual wrapper run CLI supervises exact held backend main normally',w.main()==0)
 check('native effect submitted exactly once after both postclose observations',sum(r['kind']=='window-effect' for r in client.calls)==1 and [r['kind'] for r in client.calls][:6]==['hello','geometry-attach','scene-facts-request','snapshot-request','scene-facts-request','geometry-facts-request'])
 check('actual released receipt byte fields unchanged and delivered exactly once',sum(x==R for x in sent)==1 and not any(x['kind']=='host-disconnected' for x in sent))
 check('actual supervisor watchdog terminated normally',not holder[0].thread.is_alive())
 report['actualMainTransportCalls']=client.calls;report['actualMainForwardedFrames']=sent
 for row in json.loads((ROOT/'upstream.json').read_text()):assert sha(ROOT.parents[1]/row['path'])==row['sha256']
 for rel,digest in inputs.items():assert sha(ROOT/rel)==digest
 report['passed']=True
except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(checks),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
