"""Actual broker cold lifecycle and strict collection migration; fake native peer."""
import copy,hashlib,json,os,resource,selectors,subprocess,sys,tempfile,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from recovery_store import RecoveryStore
from durable_ledger import Ledger,NAME
from endpoint import Refused
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('multi-'+str(time.time_ns()));OUT.mkdir()
report={'passed':False,'checks':[],'inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'qa/transport.py',*sorted((ROOT/'adapter').glob('*.py'))]},'scope':'Real broker subprocess and durable ledger; synthetic native transport; no live host admission, native geometry/pixels or release acceptance'}
def check(name,value):report['checks'].append({'name':name,'passed':bool(value)});assert value,name
def refused(fn):
 try:fn()
 except (Refused,ValueError,OSError):return True
 return False
B={'lifetime':'71','session':'2','frontend':'3'}
def request(n,inc):return {'protocolVersion':3,'kind':'window-effect','effectProtocol':2,'binding':copy.deepcopy(B),'intent':{'request':str(n),'generation':str(n+2),'incarnation':str(inc),'operation':'maximize','context':{'lifetime':'71','epoch':'3','output':'14','revision':'13'}}}
class Reader:
 def __init__(self,stream):self.stream=stream;self.tail=b'';self.frames=[]
 def frame(self):
  deadline=time.monotonic()+3
  while not self.frames:
   with selectors.DefaultSelector() as s:
    s.register(self.stream,selectors.EVENT_READ);assert s.select(max(0,deadline-time.monotonic())),'CPU frame timeout'
   data=os.read(self.stream.fileno(),4096);assert data,'Unexpected EOF';self.tail+=data
   while b'\n' in self.tail:
    raw,_,self.tail=self.tail.partition(b'\n');self.frames.append(json.loads(raw))
  return self.frames.pop(0)
def send(p,r):p.stdin.write(json.dumps(r).encode()+b'\n');p.stdin.flush()
def retire(p):
 if p.poll() is None:p.kill();p.wait(timeout=3)
 for s in [p.stdin,p.stdout,p.stderr]:s.close()
def start(config):
 p=subprocess.Popen(['/usr/bin/python3','-B',str(ROOT/'qa/transport.py'),str(config)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE);return p,Reader(p.stdout)
try:
 with tempfile.TemporaryDirectory(prefix='elm-multi-cold-') as tmp:
  runtime=Path(tmp);runtime.chmod(0o700)
  with RecoveryStore(runtime,'fixture','71'):pass
  config=runtime/'config.json';config.write_text(json.dumps({'runtime':str(runtime),'instance':'fixture','mode':'mixed'}));config.chmod(0o600)
  a,b=request(41,7),request(42,8)
  p,r=start(config)
  try:
   check('first attached',r.frame()['kind']=='attached');check('initial exact allocation marks',r.frame()['request']=='0');check('first negotiation',r.frame()['kind']=='host-geometry-negotiate')
   send(p,{'protocolVersion':3,'kind':'geometry-attach','geometryProtocol':1,'binding':B,'requestId':'1'});check('negotiated strict geometry',r.frame()['kind']=='geometry-attached')
   send(p,a);check('A native Unknown published',r.frame()['status']=='Unknown');send(p,b);check('B definitive commit published',r.frame()['status']=='Committed')
   p.stdin.close();check('first broker normal EOF',p.wait(timeout=3)==0)
  finally:retire(p)
  p,r=start(config)
  try:
   check('cold broker attached',r.frame()['kind']=='attached');mark=r.frame();check('cold allocator includes committed B',mark=={'protocolVersion':3,'kind':'host-recovery-watermarks','binding':B,'request':'42','generation':'44'})
   frame=r.frame();check('cold broker retains original A exactly',frame=={'protocolVersion':3,'kind':'host-uncertain','effectProtocol':2,'binding':B,'intent':a['intent']})
   check('cold recovery completes negotiation',r.frame()['kind']=='host-geometry-negotiate')
   check('cold start did not repeat native submission',len((runtime/'submitted.jsonl').read_text().splitlines())==2)
   send(p,a);check('duplicate request retires transport without invented receipt',r.frame()=={'protocolVersion':3,'kind':'host-disconnected'});check('duplicate failure exit',p.wait(timeout=3)==1)
   check('duplicate performed zero extra submissions',len((runtime/'submitted.jsonl').read_text().splitlines())==2)
  finally:retire(p)
  with RecoveryStore(runtime,'fixture','71') as store:
   check('duplicate kept A uncertainty',store.uncertain(B)['intent']==a['intent']);check('latest known B remains durable',store.read()['intent']==b['intent'] and store.read()['status']=='Committed')
  # Migrate the exact bounded prototype3 collection, preserving source bytes.
  other=runtime/'migration';other.mkdir(mode=0o700)
  with Ledger(other,'fixture','71') as ledger:
   ledger.begin(B,a['intent'],2);state=ledger.snapshot()
  prior={k:v for k,v in state.items() if k not in ['latest','predecessorSHA256']};prior['schema']=3
  path=Ledger.namespace_path(other,'fixture','71');(path/NAME).unlink();source=path/'ledger-v3.json';source.write_text(json.dumps(prior));source.chmod(0o600);saved=source.read_bytes()
  with RecoveryStore(other,'fixture','71') as store:
   check('strict prototype3 migration preserves A',store.uncertain(B)['intent']==a['intent']);check('strict migration publishes schema4',store.ledger.snapshot()['schema']==4)
   check('prior collection is preserved byte-for-byte',source.read_bytes()==saved)
   check('prior collection hash bound',store.ledger.snapshot()['predecessorSHA256']==hashlib.sha256(saved).hexdigest())
   prior['watermarks'][0]['request']='99';source.write_text(json.dumps(prior));check('old collection producer change refused',refused(store.ledger.snapshot))
  check('cold old producer modification still refused',refused(lambda:RecoveryStore(other,'fixture','71')))
 report['passed']=True
except Exception as error:report.update(error=repr(error),traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
