"""Live compiled C admission owner and actual Python ledger, no GUI/native mutation."""
import copy,fcntl,hashlib,json,os,resource,selectors,shutil,subprocess,sys,tempfile,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('cross-'+str(time.time_ns()));OUT.mkdir();INPUT=OUT/'inputs';INPUT.mkdir()
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
build=sorted((ROOT/'qa').glob('build-*/report.json'))[-1];bd=json.loads(build.read_text());assert bd['passed']
for name,digest in bd['inputs'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
HELPER=build.parent/'handoff-helper';assert hashlib.sha256(HELPER.read_bytes()).hexdigest()==bd['artifacts']['handoff-helper']
report={'passed':False,'checks':[],'inputs':inputs,'binarySHA256':bd['artifacts']['handoff-helper'],'buildReport':str(build),'scope':'Actual live compiled C owner and Python ledger/filesystem; no GTK journey, compositor mutation/pixels or native release acceptance','owners':[]}
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
try:
 with tempfile.TemporaryDirectory(prefix='elm-admission-cross-') as tmp:
  base=Path(tmp);base.chmod(0o700)
  def runtime(name):p=base/name;p.mkdir(mode=0o700);return p
  r=runtime('lifecycle');a,b,c=request(41,7),request(42,8,1,'minimize'),request(43,9)
  with Owner(r) as owner:
   check('C host alive admits A before broker reads',owner.command([a]))
   filename=storage_key(rec(a))+'.json';check('C/Python exact full-key filename agrees',(entries(r)/filename).exists())
   check('actual C private Pending record agrees',json.loads((entries(r)/filename).read_text())==rec(a))
   with RecoveryStore(r,'fixture','71') as store:
    check('live C whole-host owner does not block broker storage lock',owner.p.poll() is None)
    check('unread A imported Unknown',store.uncertain(B)['intent']==a['intent'])
    check('recovered admission cannot authorize duplicate native submit',store.begin(B,a['intent'],2) is False)
    before=hashes(r);check('C duplicate rejected before overwrite',not owner.command([a]));check('duplicate preserves every byte',hashes(r)==before)
    check('C legacy B admitted concurrently with broker lifetime',owner.command([b]));check('fresh B authorized only after both durable stages',store.begin(B,b['intent'],1) is True)
    store.settle(outcome(b));check('B known settlement retained until host retirement',len(store.ledger.snapshot()['settled'])==1)
    check('C unrelated C admitted',owner.command([c]));check('fresh C native authorization',store.begin(B,c['intent'],2) is True);store.settle(outcome(c))
    check('new latest C does not erase old definitive B',len(store.ledger.snapshot()['settled'])==2)
   with RecoveryStore(r,'fixture','71') as store:
    frames=store.recovery_frames(B);check('cold recovery only A uncertain',[f['intent'] for f in frames if f['kind']=='host-uncertain']==[a['intent']])
    terminals=store.settlement_frames(B);check('cold broker preserves B and C definitive retirement',len(terminals)==2 and {f['record']['intent']['request'] for f in terminals}=={'42','43'})
    before=hashes(r);check('Unknown cannot retire C admission',not owner.command(rec(a,'Unknown')));check('Unknown retirement preserves bytes',hashes(r)==before)
    foreign=rec(b,'Committed');foreign['binding']['lifetime']='72';foreign['intent']['context']['lifetime']='72';check('foreign lifetime retirement rejected',not owner.command(foreign))
    check('actual C exact B retirement',owner.command(rec(b,'Committed')));check('B only removed',len(hashes(r))==2 and filename in hashes(r))
    store.ledger.synchronization_snapshot();check('B tombstone GC only after durable absence',len(store.ledger.snapshot()['settled'])==1)
    check('actual C exact C retirement',owner.command(rec(c,'Committed')));store.ledger.synchronization_snapshot();check('all known tombstones retired safely',store.ledger.snapshot()['settled']==[])
    check('A Unknown retained after retirements',store.uncertain(B)['intent']==a['intent'])
    check('duplicate C retirement is inert',owner.command(rec(c,'Committed')) and len(hashes(r))==1)
    other=subprocess.run([str(HELPER),str(owner.config),json.dumps(B)],input=b'',capture_output=True,timeout=3);check('second live host owner refused',other.returncode==2 and owner.p.poll() is None)
    path=entries(r)/filename;saved=path.read_bytes();path.write_bytes(b'{"schema":2,"schema":2}');check('duplicate-key admission rejected by actual C scan',not owner.command([request(44,10)]));check('duplicate-key admission rejected by broker',refused(store.ledger.synchronization_snapshot));path.write_bytes(saved);path.chmod(0o600)
    check('explicit correction restores original A',store.uncertain(B)['intent']==a['intent'])
  with RecoveryStore(r,'fixture','71') as store:check('cold host retirement cannot resurrect B or C',len(store.ledger.snapshot()['entries'])==1 and store.ledger.snapshot()['entries'][0]['intent']==a['intent'])
  r=runtime('capacity')
  with Owner(r) as owner:
   for n in range(1,65):check('C admission capacity slot '+str(n),owner.command([request(n,n)]))
   before=hashes(r);check('65th C admission refused without eviction',not owner.command([request(65,65)]));check('all64 C admissions byte-preserved',hashes(r)==before)
   with RecoveryStore(r,'fixture','71') as store:
    check('all64 unread admissions recovered',len(store.ledger.snapshot()['entries'])==64)
    check('unadmitted65 cannot authorize a native call',refused(lambda:store.begin(B,request(65,65)['intent'],2)))
    known=request(32,32);store.settle(outcome(known));check('exact32 settlement retires actual C key',owner.command(rec(known,'Committed')));store.ledger.synchronization_snapshot()
    check('capacity regained without dropping unknowns',owner.command([request(65,65)]));check('fresh65 authorized after explicit exact retirement',store.begin(B,request(65,65)['intent'],2) is True)
    check('ledger contains64 independent preserved targets',len(store.ledger.snapshot()['entries'])==64 and any(e['intent']['incarnation']=='1' for e in store.ledger.snapshot()['entries']))
  r=runtime('missing')
  with Owner(r) as owner:
   owner.command([a])
   with RecoveryStore(r,'fixture','71') as store:path=store.path;check('durable initialization marker exists',(path/MARKER).exists())
   saved=(path/NAME).read_bytes();(path/NAME).unlink();check('missing initialized ledger refuses cold rebuild',refused(lambda:RecoveryStore(r,'fixture','71')));check('unread evidence never removed on missing ledger',len(hashes(r))==1)
   (path/NAME).write_bytes(saved);(path/NAME).chmod(0o600)
   with RecoveryStore(r,'fixture','71') as store:check('explicit ledger correction retains A',store.uncertain(B)['intent']==a['intent'])
  r=runtime('migration')
  with Owner(r) as owner:
   owner.command([a])
   with Ledger(r,'fixture','71') as old:old.begin(B,a['intent'],2);old.settle(outcome(a,'Unknown'))
   old_path=Ledger.namespace_path(r,'fixture','71')/'ledger-v4.json';saved=old_path.read_bytes()
   with RecoveryStore(r,'fixture','71') as store:check('strict schema4 to5 migration retains A',store.uncertain(B)['intent']==a['intent']);check('prior ledger bytes unchanged',old_path.read_bytes()==saved)
   with Ledger(r,'fixture','71') as old:old.begin(B,b['intent'],1)
   check('old producer mutation refuses later adoption',refused(lambda:RecoveryStore(r,'fixture','71')))
 report['passed']=True
except Exception as error:report.update(error=repr(error),traceback=traceback.format_exc())
report['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
