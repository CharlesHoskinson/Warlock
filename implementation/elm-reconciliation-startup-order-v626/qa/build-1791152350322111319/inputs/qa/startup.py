import copy,hashlib,json,os,pathlib,resource,shlex,subprocess,sys,time
from contextlib import contextmanager
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
import daemon
from recovery_store import RecoveryStore
from endpoint import Refused
OLD={'lifetime':'19','session':'1','frontend':'1'};NOW={'lifetime':'19','session':'10','frontend':'1'}
OTHER={'lifetime':'19','session':'3','frontend':'1'}
OUT=ROOT/'qa'/('startup-'+str(time.time_ns()));OUT.mkdir();checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def command(name,args):
 p=subprocess.run(args,capture_output=True,text=True,timeout=90);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);check(name,p.returncode==0);return p.stdout
def record(bound=OLD,target='2',number='12'):
 return {'schema':2,'effectProtocol':1,'binding':copy.deepcopy(bound),'status':'Unknown','intent':{'request':number,'generation':number,'incarnation':target,'operation':'minimize','context':{'lifetime':'19','epoch':'1','output':'7','revision':'21'}}}
class Client(daemon.Endpoint):
 def __init__(self):self.bound=copy.deepcopy(NOW);self._grant_watermarks={};self.requests=[];self.sequence=50;self.bad=False
 def request(self,r):
  self.requests.append(copy.deepcopy(r));self.sequence+=1
  response={'protocolVersion':3,'kind':'binding-retirement','retirementProtocol':1,'operation':'retire','binding':copy.deepcopy(NOW),'queriedBinding':copy.deepcopy(r['queriedBinding']),'requestId':r['requestId'],'sequence':str(self.sequence),'grantState':'Retired'}
  if self.bad:response['extra']=True
  return response
try:
 flags=shlex.split(command('flags',['pkg-config','--cflags','--libs','json-glib-1.0']))
 command('compiled-actual-C-bind',['cc','-std=gnu11','-O2','-Wall','-Wextra','-Werror','-Wno-unused-function',str(ROOT/'native/admission-test.c'),'-o',str(OUT/'admission-test'),*flags])
 def setup(name,records):
  runtime=OUT/name;runtime.mkdir(mode=0o700);config=runtime/'config.json';config.write_text(json.dumps({'runtime':str(runtime),'instance':'Test'}));config.chmod(0o600)
  for r in records:
   request={'protocolVersion':3,'kind':'window-effect','effectProtocol':1,'binding':r['binding'],'intent':r['intent']}
   command(name+'-admit-'+r['intent']['incarnation'],[str(OUT/'admission-test'),str(config),json.dumps([request]),json.dumps(r['binding'])])
  return runtime,config,RecoveryStore(str(runtime),'Test','19')
 def bind(config):return subprocess.run([str(OUT/'admission-test'),str(config),'[]',json.dumps(NOW)],capture_output=True,text=True,timeout=10).returncode
 runtime,config,store=setup('race',[])
 # Deterministic control reproduces exactly the native nonblocking bind refusal
 # when attached races a live short broker host lock; no graphical host launches.
 with store.ledger.host_guard():check('actual C attached bind refuses broker-held host lock',bind(config)==1)
 check('same actual C bind succeeds after short lock releases',bind(config)==0);store.close()

 for name,records in [('empty',[]),('serial',[record(),record(OTHER,'3','13')])]:
  runtime,config,store=setup(name,records);client=Client();frames=[];events=[];published=[False];guard=store.ledger.host_guard
  @contextmanager
  def tracked():
   events.append({'kind':'host_guard','afterAttached':published[0]})
   with guard() as directory:yield directory
  def send(frame):
   if frame['kind']=='attached':
    published[0]=True;check('actual C bind succeeds at attached publication '+name,bind(config)==0)
   frames.append(copy.deepcopy(frame))
  hello={'protocolVersion':3,'kind':'attached','binding':copy.deepcopy(NOW)}
  with patch.object(store.ledger,'host_guard',tracked),patch.object(daemon,'send',send):c=daemon.publish_startup(client,hello,store)
  check('zero broker host-lock acquisitions after attached startup '+name,events and not any(e['afterAttached'] for e in events))
  expected=['attached','host-recovery-watermarks']+['host-reservation-unknown']*len(records)+(['binding-retirement'] if records else [])+['host-geometry-negotiate']
  check('published startup order unchanged '+name,[f['kind'] for f in frames]==expected)
  check('all full Unknown records before active proof '+name,[f['record'] for f in frames if f['kind']=='host-reservation-unknown']==records)
  check('live callback restored before frontend requests '+name,c.send is send)
  if records:
   check('strict599 proofs acquired before wire publication',len(client.requests)==2 and c.active.as_dict()==frames[-2])
   def complete(action,geometry):
    p=c.active;c.proof_ready({'protocolVersion':3,'kind':'reconciliation-ready','binding':NOW,'queriedBinding':p.queried_binding.as_dict(),'proofRequestId':p.request_id})
    for domain,request,revision in [('action',action,'22'),('geometry',geometry,'29')]:c.requested_read(domain,request);c.delivered_read(domain,request,{'lifetime':'19','epoch':'1','output':'7','revision':revision})
   complete('91','37')
   check('next scope proof uses live wire callback',frames[-2]['kind']=='host-reservation-released' and frames[-1]['kind']=='binding-retirement' and store.ledger.blocked('19','3'))
   complete('92','38')
   check('serial scopes still require independent ready/read release',len([f for f in frames if f['kind']=='host-reservation-released'])==2 and store.ledger.snapshot()['entries']==[])
  (OUT/(name+'-frames.json')).write_text(json.dumps(frames,indent=2));(OUT/(name+'-lock-events.json')).write_text(json.dumps(events,indent=2));store.close()

 runtime,config,store=setup('bad-proof',[record()]);client=Client();client.bad=True;frames=[]
 with patch.object(daemon,'send',lambda f:frames.append(copy.deepcopy(f))):
  try:daemon.publish_startup(client,{'kind':'attached'},store)
  except Refused:check('failed staged proof cannot publish attached or partial startup',frames==[])
  else:check('failed staged proof cannot publish attached or partial startup',False)
 check('staged failure retains full Unknown',store.ledger.snapshot()['entries']==[record()] and store.ledger.snapshot()['releases']==[]);store.close()
 report={'passed':True,'assertions':len(checks),'checks':checks,'nativeAcceptance':False,'nativeAuthentication':False,'claim':'Actual compiled C admission bind/nonblocking locks and unchanged608 real store; synthetic strictly decoded599 proof fixtures; actual daemon startup helper ordering, no GUI',
  'sourceSHA256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for d in ['adapter','native'] for p in (ROOT/d).glob('*') if p.is_file()}}
except BaseException as error:report={'passed':False,'checks':checks,'error':repr(error)};raise
finally:(OUT/'report.json').write_text(json.dumps(report,indent=2));print(OUT/'report.json',flush=True)
