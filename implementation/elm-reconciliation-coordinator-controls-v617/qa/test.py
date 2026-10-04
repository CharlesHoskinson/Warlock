import copy,hashlib,json,os,pathlib,resource,shlex,subprocess,sys,time
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
import daemon
from reconciliation import Reconciliation
from recovery_store import RecoveryStore
from admission_ledger import storage_key
from durable_ledger import encoded
from endpoint import Refused, Endpoint as NativeEndpoint, start_time

OLD={'lifetime':'19','session':'1','frontend':'1'};NOW={'lifetime':'19','session':'10','frontend':'1'}
def record(bound=OLD,target='2',number='12'):
 return {'schema':2,'effectProtocol':1,'binding':copy.deepcopy(bound),'status':'Unknown','intent':{'request':number,'generation':number,'incarnation':target,'operation':'minimize','context':{'lifetime':'19','epoch':'1','output':'7','revision':'21'}}}
OUT=ROOT/'qa'/('tests-'+str(time.time_ns()));OUT.mkdir();checks=[];builds=[]
def check(name,value):
 checks.append({'name':name,'passed':bool(value)})
 if not value:raise AssertionError(name)
def denied(name,fn):
 try:fn()
 except (Refused,OSError):check(name,True)
 else:check(name,False)
def run(name,args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=90);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
 builds.append({'name':name,'exitCode':p.returncode});check(name,p.returncode==0);return p.stdout
try:
 flags=shlex.split(run('flags',['pkg-config','--cflags','--libs','gtk+-3.0','webkit2gtk-4.1','gtk-layer-shell-0','json-glib-1.0','gio-unix-2.0']))
 for source,name in [('admission-test.c','admission-test'),('geometry-carrier-test.c','geometry-carrier'),('reconciliation-carrier-test.c','reconciliation-carrier'),('shared-host.c','elm-host')]:
  run(name+'-compile',['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-deprecated-declarations',*(['-Wno-unused-function'] if name=='admission-test' else []),str(ROOT/'native'/source),'-o',str(OUT/name),*flags])
  if name=='elm-host':run(name+'-self-tests',[str(OUT/name),'--self-test'])
  elif name!='admission-test':run(name+'-tests',[str(OUT/name)])

 class Client(daemon.Endpoint):
  def __init__(self):
   self.bound=copy.deepcopy(NOW);self._grant_watermarks={};self.sequence=50;self.requests=[];self.action_output='7';self.geometry_output='7';self.scene_changed=False
   self.geometry_binding=copy.deepcopy(NOW);self.geometry_protocol=2;self.geometry_capabilities={'effects':True,'operations':['maximize','restore-geometry']}
  def request(self,request):
   self.requests.append(copy.deepcopy(request));self.sequence+=1
   assert request['kind']=='binding-retire-request'
   return {'protocolVersion':3,'kind':'binding-retirement','retirementProtocol':1,'operation':'retire','binding':copy.deepcopy(self.bound),'queriedBinding':copy.deepcopy(request['queriedBinding']),'requestId':request['requestId'],'sequence':str(self.sequence),'grantState':'Retired'}
  def scene_facts(self,request_id):
   return {'protocolVersion':3,'kind':'scene-facts','binding':copy.deepcopy(self.bound),'requestId':request_id,'revision':'23' if self.scene_changed and len(self.requests)%2 else '22','outputGeneration':self.action_output,'facts':{'focused':None,'windows':[]}}
  def snapshot(self,request_id):return {'windows':[]}
  def geometry_facts(self,request_id,minimum):
   return {'protocolVersion':3,'kind':'geometry-facts','geometryProtocol':2,'binding':copy.deepcopy(self.bound),'requestId':request_id,'sequence':'57','revision':'29','outputGeneration':self.geometry_output,'facts':{'focused':None,'inputBlocked':False,'windows':[]}}

 def setup(name,records=None,client_factory=Client,announce=True):
  runtime=OUT/name;runtime.mkdir(mode=0o700);config=runtime/'config.json';config.write_bytes(encoded({'runtime':str(runtime),'instance':'Test'}));config.chmod(0o600)
  for r in records or [record()]:
   request={'protocolVersion':3,'kind':'window-effect','effectProtocol':r['effectProtocol'],'binding':r['binding'],'intent':r['intent']}
   run(name+'-admit-'+r['intent']['incarnation'],[str(OUT/'admission-test'),str(config),json.dumps([request]),json.dumps(r['binding'])])
  store=RecoveryStore(str(runtime),'Test','19');client=client_factory();events=[]
  def send(frame):events.append(copy.deepcopy(frame))
  coordinator=Reconciliation(client,store.ledger,send)
  if announce:coordinator.announce()
  return runtime,store,client,events,coordinator,send
 def ready(coordinator):
  proof=coordinator.active
  return {'protocolVersion':3,'kind':'reconciliation-ready','binding':copy.deepcopy(NOW),'proofRequestId':proof.request_id,'queriedBinding':proof.queried_binding.as_dict()}
 def read(client,store,coordinator,send,domain,request_id):
  request={'protocolVersion':3,'kind':'projection-request' if domain=='action' else 'geometry-facts-request','binding':copy.deepcopy(NOW),'requestId':request_id}
  if domain=='geometry':request.update(geometryProtocol=2,minimumWatermark='0')
  with patch.object(daemon,'send',send):daemon.handle_request(client,None,request,store,coordinator)
 def releases(events):return [f for f in events if f['kind']=='host-reservation-released']
 runtime,store,client,events,c,send=setup('startup')
 check('full old origin preserved before exact proof',events[0]['kind']=='host-reservation-unknown' and events[0]['record']==record() and events[1]['kind']=='binding-retirement')
 check('strict inherited599 consumer supplies typed proof',client.requests[0]['queriedBinding']==OLD and c.active.as_dict()==events[1])
 read(client,store,c,send,'action','1');read(client,store,c,send,'geometry','2')
 check('queued pre-ack reads cannot release',not releases(events) and store.ledger.blocked('19','2'))
 with patch.object(daemon,'send',send):daemon.handle_request(client,None,ready(c),store,c)
 read(client,store,c,send,'action','91')
 check('one fresh domain cannot release',not releases(events) and store.ledger.blocked('19','2'))
 read(client,store,c,send,'geometry','37')
 release=releases(events)[0]
 check('fresh replies precede release frame',events[-3]['kind']=='action-projection' and events[-2]['kind']=='geometry-facts' and events[-1]['kind']=='host-reservation-released')
 check('read IDs and revision domains independent',release['release']['observation']=={'actionRequestId':'91','geometryRequestId':'37','actionContext':{'lifetime':'19','epoch':'1','output':'7','revision':'22'},'geometryContext':{'lifetime':'19','epoch':'1','output':'7','revision':'29'}})
 state=store.ledger.snapshot();check('wire follows durable Released',state['releases'][0]['phase']=='Released' and release['record']==state['releases'][0]['record'] and release['release']['id']==state['releases'][0]['id'])
 check('no host replay or read allocations',all(r['kind']=='binding-retire-request' for r in client.requests) and state['watermarks'][0]['request']=='12')
 check('exact admission retired before frontend release',not (store.path/'admissions-v1'/(storage_key(record())+'.json')).exists())
 check('current recovery restores no archived reservation',store.recovery_frames(NOW)==[{'protocolVersion':3,'kind':'host-recovery-watermarks','binding':NOW,'request':'12','generation':'12'}]);store.close()

 runtime,store,client,events,c,send=setup('retry')
 c.proof_ready(ready(c));read(client,store,c,send,'action','91')
 client.geometry_output='8';read(client,store,c,send,'geometry','37')
 check('different current output generations remain reserved',not releases(events) and store.ledger.blocked('19','2'))
 client.action_output='8';read(client,store,c,send,'action','92')
 check('new matched output read releases without forged revisions',releases(events)[0]['release']['observation']['actionRequestId']=='92');store.close()

 runtime,store,client,events,c,send=setup('invalid-ready')
 for field,value in [('proofRequestId','2'),('proofRequestId','0'),('proofRequestId',True),('protocolVersion',True),('queriedBinding',NOW),('binding',OLD)]:
  r=ready(c);r[field]=value;denied('ready rejects '+field+' '+str(value),lambda r=r:c.proof_ready(r))
 c.proof_ready(ready(c));c.requested_read('action','91');c.delivered_read('action','90',{'lifetime':'19','epoch':'1','output':'7','revision':'22'})
 check('mismatched delivered ID cannot qualify',c.accepted=={})
 c.proof_ready(ready(c));check('ready duplicates do not allocate reads',c.requested=={'action':'91'})
 client.bound['frontend']='2';denied('frontend change invalidates reads',lambda:c.requested_read('geometry','37'));store.close()

 old2={'lifetime':'19','session':'3','frontend':'1'}
 runtime,store,client,events,c,send=setup('scopes',[record(),record(old2,'3','13')])
 check('all Unknown before serial first proof',len(events)==3 and [f['kind'] for f in events]==['host-reservation-unknown','host-reservation-unknown','binding-retirement'])
 c.proof_ready(ready(c));read(client,store,c,send,'geometry','37');read(client,store,c,send,'action','91')
 check('first proof cannot release unannounced scope',len(releases(events))==1 and store.ledger.blocked('19','3') and events[-1]['kind']=='binding-retirement')
 read(client,store,c,send,'geometry','38');read(client,store,c,send,'action','92')
 check('next scope needs its own ready/read barrier',len(releases(events))==1)
 c.proof_ready(ready(c));read(client,store,c,send,'geometry','39');read(client,store,c,send,'action','93')
 check('serial next scope releases with fresh independent IDs',len(releases(events))==2 and releases(events)[1]['release']['observation']['actionRequestId']=='93' and not store.ledger.blocked('19','3'));store.close()

 for failure in ['read-output','storage-release','release-output']:
  runtime,store,client,events,c,send=setup(failure);c.proof_ready(ready(c));read(client,store,c,send,'action','91')
  def failing_send(frame):
   if frame['kind']==('geometry-facts' if failure=='read-output' else 'host-reservation-released'):raise daemon.OutputFailure('injected delivery failure')
   send(frame)
  original=store.ledger.release
  def failing_release(join):raise OSError('injected durable storage failure')
  c.send=failing_send
  with patch.object(store.ledger,'release',failing_release if failure=='storage-release' else original):
   denied('failure propagated '+failure,lambda:read(client,store,c,failing_send,'geometry','37'))
  check('no failed release acknowledgement '+failure,not releases(events))
  check('failure reservation truth '+failure,store.ledger.blocked('19','2')==(failure!='release-output'))
  check('Unknown history preserved '+failure,not store.ledger.snapshot()['releases'] or store.ledger.snapshot()['releases'][0]['record']['status']=='Unknown');store.close()

 # Multiple exact reservations in one retired scope share one native proof but
 # retain independent durable disposition IDs and complete historical records.
 pair=[record(),record(OLD,'3','13')]
 runtime,store,client,events,c,send=setup('same-scope',pair)
 check('same scope obtains exactly one strict retirement proof',len(client.requests)==1)
 c.proof_ready(ready(c));read(client,store,c,send,'action','91');read(client,store,c,send,'geometry','37')
 frames=releases(events);state=store.ledger.snapshot()
 check('one scope releases two exact records',len(frames)==2 and [f['record'] for f in frames]==pair and [r['record'] for r in state['releases']]==pair)
 check('same scope release identities remain distinct',len({f['release']['id'] for f in frames})==2 and len({json.dumps(f['release']['proof'],sort_keys=True) for f in frames})==1)
 check('same scope clears both exact admission files',all(not (store.path/'admissions-v1'/(storage_key(r)+'.json')).exists() for r in pair) and state['entries']==[])
 store.close()

 # Fail the first release frame after its durable disposition, before the next
 # group member can mutate storage. Reopening must retain the two truths.
 runtime,store,client,events,c,send=setup('same-scope-output-failure',pair)
 c.proof_ready(ready(c));read(client,store,c,send,'action','91')
 def first_release_failure(frame):
  if frame['kind']=='host-reservation-released':raise daemon.OutputFailure('first group release output failed')
  send(frame)
 c.send=first_release_failure
 denied('same scope output failure stops group processing',lambda:read(client,store,c,first_release_failure,'geometry','37'))
 state=store.ledger.snapshot()
 check('partial group preserves one Released and remaining Unknown',len(state['releases'])==1 and state['releases'][0]['record']==pair[0] and state['entries']==[pair[1]] and not releases(events))
 immutable=copy.deepcopy(state['releases'][0]);store.close()
 store=RecoveryStore(str(runtime),'Test','19');state=store.ledger.snapshot()
 check('explicit reopen preserves first immutable disposition',state['releases']==[immutable] and state['entries']==[pair[1]])
 check('reopen reserves only remaining exact target',not store.ledger.blocked('19','2') and store.ledger.blocked('19','3'))
 check('reopen exposes only remaining Unknown record',store.recovery_frames(NOW)[1:]==[{'protocolVersion':3,'kind':'host-reservation-unknown','binding':NOW,'record':pair[1]}])
 check('partial group exact admissions mirror dispositions',not (store.path/'admissions-v1'/(storage_key(pair[0])+'.json')).exists() and (store.path/'admissions-v1'/(storage_key(pair[1])+'.json')).exists())
 store.close()

 # A later proof failure must leave every full Unknown already delivered, with
 # no partial proof announcement and no durable release. This is synthetic
 # transport, passed through the real inherited599 proof decoder.
 second={'lifetime':'19','session':'3','frontend':'1'}
 for fault in ['refused','extra-field','wrong-operation','registered']:
  class FaultClient(Client):
   def request(self,request):
    response=super().request(request)
    if len(self.requests)==2:
     if fault=='refused':raise Refused('synthetic native exact grant refusal')
     if fault=='extra-field':response['extra']=True
     if fault=='wrong-operation':response['operation']='observe'
     if fault=='registered':response['grantState']='Registered'
    return response
  original=[record(),record(second,'3','13')]
  runtime,store,client,events,c,send=setup('proof-'+fault,original,FaultClient,False)
  denied('strict proof failure propagates '+fault,c.announce)
  check('all full Unknown precede failed proof '+fault,events==[{'protocolVersion':3,'kind':'host-reservation-unknown','binding':NOW,'record':r} for r in original] and len(client.requests)==2)
  check('failed proof cannot announce partial scope or release '+fault,c.active is None and not releases(events) and store.ledger.snapshot()['releases']==[] and store.ledger.snapshot()['entries']==original)
  check('failed proof retains every target '+fault,all(store.ledger.blocked('19',r['intent']['incarnation']) for r in original));store.close()

 # Run inherited construction, hello, attach and facts through one endpoint's
 # request override. Native path/process verification is deliberately bypassed;
 # the held executable hash is this local Python process, never a compositor.
 class HandshakeClient(daemon.Endpoint):
  def verify_paths(self):pass
  def verify_process(self):pass
  def request(self,request):
   self.requests.append(copy.deepcopy(request));kind=request['kind']
   if kind=='hello':
    self.epoch+=1;b={**NOW,'frontend':str(self.epoch)}
    return {'protocolVersion':3,'kind':'attached','binding':b,'compositor':{'pid':self.pid,'instance':self.instance,'coreHash':'synthetic-core'},'capabilities':{'observe':True,'effects':True,'minimizedState':True,'effectProtocol':1,'operations':['minimize','restore','activate'],'canonicalScene':False,'taskbarProjectionProtocol':1,'effectInvalidationProtocol':1}}
   if kind=='geometry-attach':
    return {'protocolVersion':3,'kind':'geometry-attached','geometryProtocol':request['geometryProtocol'],'binding':copy.deepcopy(self.bound),'requestId':request['requestId'],'capabilities':{'observe':True,'effects':True,'effectProtocol':2,'operations':['maximize','restore-geometry'],'placementCapacity':True if self.bad_attach else 256,'canonicalScene':False}}
   if kind=='geometry-facts-request':
    return {'protocolVersion':3,'kind':'geometry-facts','geometryProtocol':request['geometryProtocol'],'binding':copy.deepcopy(self.bound),'requestId':'999' if self.bad_facts else request['requestId'],'sequence':'61','revision':'29','outputGeneration':'7','facts':{'focused':None,'inputBlocked':False,'windows':[]}}
   if kind=='binding-retirement-state-request':
    return {'protocolVersion':3,'kind':'binding-retirement','retirementProtocol':1,'operation':'observe','binding':copy.deepcopy(self.bound),'queriedBinding':copy.deepcopy(request['queriedBinding']),'requestId':request['requestId'],'sequence':str(self.proof_sequence),'grantState':'Retired'}
   raise AssertionError('unexpected synthetic transport kind '+kind)
 count=[];constructor=NativeEndpoint.__init__
 def counted(self,*args,**kwargs):count.append(1);constructor(self,*args,**kwargs)
 with patch.object(NativeEndpoint,'__init__',counted):
  client=HandshakeClient(str(OUT),'Test',os.getpid(),start_time(os.getpid()),hashlib.sha256(pathlib.Path('/proc/self/exe').read_bytes()).hexdigest())
 client.requests=[];client.epoch=0;client.proof_sequence=60;client.bad_attach=False;client.bad_facts=False
 check('cooperative endpoint MRO initializes native transport once',count==[1] and client._grant_watermarks=={} and client.bound is None)
 client.hello()
 check('inherited hello initializes geometry negotiation empty',client.bound==NOW and client.geometry_binding is None and client.geometry_protocol is None and client.geometry_capabilities is None)
 proof=client.observe('1',OLD);client.geometry_attach('2',2)
 check('inherited attach shares bound authenticated transport slot',client.geometry_binding==NOW and client.geometry_protocol==2 and client.geometry_capabilities['placementCapacity']==256 and proof.sequence=='60')
 facts=client.geometry_facts('3','60')
 check('inherited geometry facts decoder accepts strict transport fixture',client.geometry_context(facts)=={'lifetime':'19','epoch':'1','output':'7','revision':'29'})
 client.bad_facts=True;denied('inherited geometry decoder rejects request mismatch',lambda:client.geometry_facts('4','60'));client.bad_facts=False
 client.hello()
 check('frontend advance resets geometry but retains grant watermark',client.bound=={**NOW,'frontend':'2'} and client.geometry_binding is None and client.geometry_capabilities is None and client._grant_watermarks=={'19':60})
 denied('old grant sequence cannot revive across inherited hello',lambda:client.observe('5',OLD))
 denied('frontend advance requires geometry reattach',lambda:client.geometry_facts('6','0'))
 client.proof_sequence=61;client.observe('7',OLD)
 client.bad_attach=True;denied('inherited geometry attach rejects boolean capacity',lambda:client.geometry_attach('8',2))
 check('failed reattach leaves geometry unavailable',client.geometry_binding is None and client.geometry_protocol is None)
 client.bad_attach=False;client.geometry_attach('9',2)
 check('fresh frontend reattaches without resetting grant sequence',client.geometry_binding==client.bound and client._grant_watermarks=={'19':61})

 report={'passed':True,'assertions':len(checks),'checks':checks,'builds':builds,'nativeAcceptance':False,'frontendIntegrated':False,'nativeAuthenticationInThisTest':False,'claim':'Actual daemon request handlers and599 strict wire decoder +608 filesystem/C admissions with synthetic transport fixtures; actual C carrier/host compilers/self-tests; inherited shared endpoint constructor/hello/geometry decoder with native identity checks explicitly bypassed',
  'sourceSHA256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for d in ['adapter','native'] for p in (ROOT/d).glob('*') if p.is_file()}}
except BaseException as e:report={'passed':False,'checks':checks,'error':repr(e)};raise
finally:(OUT/'report.json').write_text(json.dumps(report,indent=2));print(OUT/'report.json',flush=True)
