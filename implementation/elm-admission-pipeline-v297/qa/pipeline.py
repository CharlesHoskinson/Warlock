"""Live compiled C admission owner and actual Python ledger, no GUI/native mutation."""
import copy,fcntl,hashlib,json,os,resource,selectors,shutil,subprocess,sys,tempfile,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('pipeline-'+str(time.time_ns()));OUT.mkdir();INPUT=OUT/'inputs';INPUT.mkdir()
files=[*sorted((ROOT/'native').glob('*')),*sorted((ROOT/'adapter').glob('*.py')),Path(__file__)]
inputs={}
for p in files:
 if not p.is_file():continue
 dest=INPUT/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);inputs[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(INPUT/'adapter'))
from recovery_store import RecoveryStore
from admission_ledger import storage_key,NAME,MARKER
from durable_ledger import Ledger
from endpoint import Refused
build=ROOT.parent/'elm-host-admission-handoff-v293/qa/build-1791107424041154044/report.json';bd=json.loads(build.read_text());assert bd['passed']
for name,digest in bd['inputs'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
HELPER=build.parent/'handoff-helper';assert hashlib.sha256(HELPER.read_bytes()).hexdigest()==bd['artifacts']['handoff-helper']
report={'passed':False,'checks':[],'inputs':inputs,'binarySHA256':bd['artifacts']['handoff-helper'],'buildReport':str(build),'scope':'Actual production daemon handler, live compiled C admission owner and durable Python store; synthetic native authority, no GTK/compositor pixels','owners':[]}
B={'lifetime':'71','session':'2','frontend':'3'}
def request(n,inc,protocol=2,operation='maximize'):
 return {'protocolVersion':3,'kind':'window-effect','effectProtocol':protocol,'binding':copy.deepcopy(B),'intent':{'request':str(n),'generation':str(n+2),'incarnation':str(inc),'operation':operation,'context':{'lifetime':'71','epoch':'3','output':'14','revision':'13'}}}
def rec(r,status='Pending'):return {'schema':2,'effectProtocol':r['effectProtocol'],'binding':copy.deepcopy(r['binding']),'intent':copy.deepcopy(r['intent']),'status':status}
def outcome(r,status='Committed'):return {**copy.deepcopy(r),'kind':'effect-outcome','status':status,'reason':'applied','revision':'14','outputGeneration':'14'}
def check(name,value):report['checks'].append({'name':name,'passed':bool(value)});assert value,name
def refused(fn):
 try:
  value=fn()
  if hasattr(value,'close'):value.close()
 except (Refused,OSError,ValueError):return True
 return False
class Owner:
 def __init__(self,runtime):
  self.runtime=runtime;self.config=runtime/'authority.json';self.config.write_text(json.dumps({'runtime':str(runtime),'instance':'fixture'}));self.config.chmod(0o600)
  self.p=subprocess.Popen([str(HELPER),str(self.config),json.dumps(B)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE);self.tail=b'';self.logs=[];assert self.frame()=={'ready':True}
 def frame(self):
  deadline=time.monotonic()+3
  while True:
   while b'\n' not in self.tail:
    with selectors.DefaultSelector() as s:
     s.register(self.p.stdout,selectors.EVENT_READ);assert s.select(max(0,deadline-time.monotonic())),'C owner CPU timeout'
    data=os.read(self.p.stdout.fileno(),4096);assert data,'C owner unexpected EOF';self.tail+=data
   raw,_,self.tail=self.tail.partition(b'\n')
   if raw.startswith(b'{'):return json.loads(raw)
   self.logs.append(raw.decode())
 def command(self,value):
  self.p.stdin.write(json.dumps(value).encode()+b'\n');self.p.stdin.flush();return self.frame()['ok']
 def close(self):
  self.p.stdin.close();code=self.p.wait(timeout=3);report['owners'].append({'exitCode':code,'stderr':self.p.stderr.read().decode(),'logs':self.logs});assert code==0
  self.p.stdout.close();self.p.stderr.close()
 def __enter__(self):return self
 def __exit__(self,*args):
  if self.p.poll() is None and args[0] is not None:self.p.kill();self.p.wait(timeout=3)
  else:self.close()
  for stream in [self.p.stdin,self.p.stdout,self.p.stderr]:stream.close()
def entries(runtime):return RecoveryStore.namespace_path(runtime,'fixture','71')/'admissions-v1'
def hashes(runtime):return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in entries(runtime).glob('*.json')}

import daemon
class NativePeer:
 def __init__(self,store,runtime):self.bound=copy.deepcopy(B);self.store=store;self.runtime=runtime;self.calls=[]
 def submit(self,intent,protocol):
  expected={'schema':2,'effectProtocol':protocol,'binding':copy.deepcopy(B),'intent':copy.deepcopy(intent),'status':'Pending'}
  check('native submit sees exact durable broker Pending '+intent['request'],self.store.ledger.snapshot()['latest']==expected)
  check('native submit sees exact durable C admission '+intent['request'],json.loads((entries(self.runtime)/(storage_key(expected)+'.json')).read_text())==expected)
  self.calls.append(copy.deepcopy(intent));return outcome({'protocolVersion':3,'kind':'window-effect','effectProtocol':protocol,'binding':self.bound,'intent':intent})
 def effect(self,intent):return self.submit(intent,1)
 def geometry_effect(self,intent):return self.submit(intent,2)
try:
 with tempfile.TemporaryDirectory(prefix='elm-admission-pipeline-') as tmp:
  r=Path(tmp);r.chmod(0o700);a,b,c=request(41,7),request(42,8,1,'minimize'),request(43,9)
  with Owner(r) as owner:
   check('actual C unread A durable',owner.command([a]))
   with RecoveryStore(r,'fixture','71') as store:
    peer=NativePeer(store,r);wires=[];daemon.send=wires.append
    check('cold import emits no native calls',peer.calls==[] and store.uncertain(B)['intent']==a['intent'])
    check('C fresh B durable before daemon input',owner.command([b]))
    daemon.handle_request(peer,None,b,store)
    check('actual handler submits B exactly once',peer.calls==[b['intent']])
    check('durable settlement metadata precedes frontend outcome',[f['kind'] for f in wires]==['host-admission-settled','effect-outcome'])
    check('actual handler terminal corresponds to B',wires[-1]==outcome(b))
    check('durable definitive B exists before frontend send',store.ledger.snapshot()['settled']==[rec(b,'Committed')])
    calls=len(peer.calls);check('duplicate daemon input refuses',refused(lambda:daemon.handle_request(peer,None,b,store)));check('duplicate never repeats native call',len(peer.calls)==calls)
    check('C unread C durable before cold boundary',owner.command([c]))
   with RecoveryStore(r,'fixture','71') as store:
    peer=NativePeer(store,r);known=store.settlement_frames(B);recovered=store.recovery_frames(B)
    check('cold lost B receipt does not resurrect B',{f['intent']['incarnation'] for f in recovered if f['kind']=='host-uncertain'}=={'7','9'})
    check('cold B remains definitive retirement metadata',len(known)==1 and known[0]['record']==rec(b,'Committed'))
    check('cold does not submit native operations',peer.calls==[])
    check('actual C consumes exact cold B terminal',owner.command(known[0]['record']))
    store.ledger.synchronization_snapshot();check('known B GC after durable C retirement',store.ledger.snapshot()['settled']==[])
    check('unread C daemon input cannot auto replay',refused(lambda:daemon.handle_request(peer,None,c,store)) and peer.calls==[])
    wrong=request(44,10);check('unproven input cannot reach native authority',refused(lambda:daemon.handle_request(peer,None,wrong,store)) and peer.calls==[])
    check('Unknown A and C remain recoverable',{f['intent']['incarnation'] for f in store.recovery_frames(B) if f['kind']=='host-uncertain'}=={'7','9'})
  with RecoveryStore(r,'fixture','71') as store:check('final cold recovery preserves all Unknowns',len(store.ledger.snapshot()['entries'])==2)
 report['passed']=True
except Exception as error:report.update(error=repr(error),traceback=traceback.format_exc())
report['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(str(OUT/'report.json'));raise SystemExit(not report['passed'])
