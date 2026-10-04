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
from endpoint import Refused

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

 def setup(name,records=None):
  runtime=OUT/name;runtime.mkdir(mode=0o700);config=runtime/'config.json';config.write_bytes(encoded({'runtime':str(runtime),'instance':'Test'}));config.chmod(0o600)
  for r in records or [record()]:
   request={'protocolVersion':3,'kind':'window-effect','effectProtocol':r['effectProtocol'],'binding':r['binding'],'intent':r['intent']}
   run(name+'-admit-'+r['intent']['incarnation'],[str(OUT/'admission-test'),str(config),json.dumps([request]),json.dumps(r['binding'])])
  store=RecoveryStore(str(runtime),'Test','19');client=Client();events=[]
  def send(frame):events.append(copy.deepcopy(frame))
  coordinator=Reconciliation(client,store.ledger,send)
  coordinator.announce()
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
 first_ready=ready(c);c.proof_ready(first_ready);read(client,store,c,send,'geometry','37');read(client,store,c,send,'action','91')
 check('first proof cannot release unannounced scope',len(releases(events))==1 and store.ledger.blocked('19','3') and events[-1]['kind']=='binding-retirement')
 c.proof_ready(first_ready)
 check('late completed proof acknowledgement cannot ready next scope',not c.ready and c.requested=={} and c.accepted=={})
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

 report={'passed':True,'assertions':len(checks),'checks':checks,'builds':builds,'nativeAcceptance':False,'frontendIntegrated':False,'nativeAuthenticationInThisTest':False,'claim':'Actual daemon request handlers and599 strict wire decoder +608 filesystem/C admissions with synthetic transport fixtures; actual C carrier/host compilers/self-tests',
  'sourceSHA256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for d in ['adapter','native'] for p in (ROOT/d).glob('*') if p.is_file()}}
except BaseException as e:report={'passed':False,'checks':checks,'error':repr(e)};raise
finally:(OUT/'report.json').write_text(json.dumps(report,indent=2));print(OUT/'report.json',flush=True)
