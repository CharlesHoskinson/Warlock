"""Actual receipt-hold wrapper CPU behavior; fake transport, never native acceptance."""
import copy,fcntl,hashlib,importlib.util,json,os,resource,shutil,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(path):
 spec=importlib.util.spec_from_file_location('receipt_wrapper',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def receipt():
 return {'protocolVersion':3,'kind':'effect-outcome','effectProtocol':2,'binding':{'lifetime':'11','session':'12','frontend':'13'},'intent':{'request':'14','generation':'15','incarnation':'16','operation':'maximize','context':{'lifetime':'11','epoch':'13','output':'17','revision':'18'}},'status':'Committed','reason':'','revision':'19','outputGeneration':'17'}

def child(wrapper,control,mode):
 w=load(Path(wrapper));sent=[]
 def send(frame):
  sent.append(frame);print(json.dumps(frame,separators=(',',':')),flush=True)
 holder=w.ReceiptHold(control,'16',send,timeout=.3 if mode in ('timeout','locked') else 3)
 def main():
  holder.intercept(receipt());holder.intercept({'protocolVersion':3,'kind':'host-refresh'})
  if mode=='eof':return 0
  # Sleep simulates a blocking selector. Raising SIGUSR1 must unwind it.
  end=time.monotonic()+4
  while time.monotonic()<end:
   if holder.released:return 0
   time.sleep(.02)
  raise RuntimeError('watchdog did not interrupt')
 code=w.supervise(holder,main)
 print(json.dumps({'kind':'cleanup','watchdogAlive':holder.thread.is_alive(),'code':code}),flush=True)
 return code
if len(sys.argv)>1 and sys.argv[1]=='child':raise SystemExit(child(*sys.argv[2:]))
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
OUT=ROOT/'qa'/('hold-'+str(time.time_ns()));OUT.mkdir();INPUT=OUT/'inputs';INPUT.mkdir()
files=[ROOT/'qa/wrapper.py',ROOT/'qa/backend.py',ROOT/'backend-pin.json',Path(__file__)]
rows={str(p.relative_to(ROOT)):sha(p) for p in files}
for p in files:
 dest=INPUT/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
w=load(INPUT/'qa/wrapper.py');checks=[];processes=[]
report={'passed':False,'scope':'Actual QA wrapper with synthetic receipts and CPU subprocess cleanup only; no native execution or rendering acceptance','inputs':rows,'checks':checks,'processes':processes}
def check(name,value):
 checks.append({'name':name,'passed':bool(value)})
 assert value,name
def refused(call):
 try:call();return False
 except (w.HoldFailure,OSError):return True
seq=0
def control():
 global seq
 seq+=1;p=OUT/('control-'+str(seq));p.mkdir(mode=0o700);fd=os.open(p/'gate.json',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.write(fd,b'{"action":"hold"}');os.close(fd);return p

def holder(clock=None):
 p=control();sent=[];kw={} if clock is None else {'clock':clock};h=w.ReceiptHold(p,'16',sent.append,**kw);return p,h,sent

def packet(h):return {'action':'release','wrapper':{'pid':h.pid,'start':h.start},'effectProtocol':2,'binding':copy.deepcopy(h.receipt['binding']),'intent':copy.deepcopy(h.receipt['intent'])}
def wait_file(p,child):
 end=time.monotonic()+2
 while time.monotonic()<end:
  if p.exists():return
  if child.poll() is not None:raise AssertionError('child exited before held record')
  time.sleep(.01)
 raise AssertionError('held record deadline')
try:
 # Authenticate the actual frozen backend packet, without opening its sockets.
 live=load(ROOT/'qa/wrapper.py');backend=live.load_backend()
 manifest=live.SOURCE/'component-manifest.json';m=json.loads(manifest.read_text());build=Path(m['buildRoot'])
 report['backend']={'manifest':str(manifest),'sha256':sha(manifest),'artifacts':{r:v for r,v in m['artifacts'].items() if r.startswith('inputs/adapter/')}}
 check('frozen captured daemon imports exact manifest and artifacts',callable(backend.main) and callable(backend.send))
 p,h,s=holder();r=receipt();h.intercept(r);check('first matching real-shaped receipt retained without send',h.seen and not h.released and s==[])
 hint={'protocolVersion':3,'kind':'host-refresh'};h.intercept(hint);check('refresh passes while outcome held',s==[hint])
 other=receipt();other['intent']['incarnation']='20';h.intercept(other);check('other incarnation passes unchanged',s[-1]==other)
 legacy=receipt();legacy['effectProtocol']=1;h.intercept(legacy);check('legacy outcome passes unchanged',s[-1]==legacy)
 r['intent']['request']='999';check('receipt capture immune to source mutation',h.receipt['intent']['request']=='14')
 bad=packet(h);bad['binding']['session']='99';check('wrong original full binding refused',refused(lambda:h.release(bad)) and not h.released)
 bad=packet(h);bad['intent']['context']['revision']='99';check('wrong original context refused',refused(lambda:h.release(bad)))
 bad=packet(h);bad['effectProtocol']=True;check('bool protocol cannot match integer',refused(lambda:h.release(bad)))
 bad=packet(h);bad['wrapper']['start']='0';check('wrong process start refused',refused(lambda:h.release(bad)))
 w.write_release(p);h.poll_gate();h.poll_gate();check('exact public gate releases original receipt once',h.released and s[-1]==receipt() and sum(x==receipt() for x in s)==1)
 check('duplicate explicit release refused',refused(lambda:h.release(packet(h))))
 h.close();check('normal closed release has no lost receipt',True)
 for name,change in [('bool wire version',lambda r:r.update(protocolVersion=True)),('Unknown receipt',lambda r:r.update(status='Unknown')),('extra field',lambda r:r.update(extra=1)),('leading-zero request',lambda r:r['intent'].update(request='014')),('context binding mismatch',lambda r:r['intent']['context'].update(epoch='99')),('oversized reason',lambda r:r.update(reason='x'*5000))]:
  p,h,s=holder();r=receipt();change(r);check(name+' refuses before delivery',refused(lambda:h.intercept(r)) and not s)
 p,h,s=holder();h.intercept(receipt());check('second matching held receipt refused',refused(lambda:h.intercept(receipt())))
 check('unreleased EOF refuses',refused(h.close))
 now=[1.0];p,h,s=holder(lambda:now[0]);h.intercept(receipt());fd=os.open(p/'gate.json',os.O_RDWR);fcntl.flock(fd,fcntl.LOCK_EX);now[0]=7
 check('locked control cannot postpone deadline',refused(h.poll_gate) and not s);os.close(fd)
 for raw in [b'{"action":"hold","action":"hold"}',b'{',b'{"action":NaN}',b'x'*4097]:check('strict control JSON '+repr(raw[:30]),refused(lambda:w.decode(raw)))
 p,h,s=holder();(p/'replacement').write_text('{"action":"hold"}');os.replace(p/'replacement',p/'gate.json');check('replaced gate inode refuses',refused(h.guard))
 p,h,s=holder();os.chmod(p/'gate.json',0o644);check('nonprivate gate refuses',refused(h.poll_gate))
 p,h,s=holder();(p/'gate.json').unlink();(p/'gate.json').symlink_to(p/'other');check('symlink gate refuses',refused(h.guard))
 check('timeout cannot exceed five seconds',refused(lambda:w.ReceiptHold(control(),'16',lambda _:None,timeout=5.01)))
 # The production supervisor runs in real CPU subprocesses with owned logs.
 for mode in ['release','timeout','malformed','eof','locked']:
  p=control();log=OUT/(mode+'.stdout');err=OUT/(mode+'.stderr')
  with log.open('wb') as stdout,err.open('wb') as stderr:
   proc=subprocess.Popen([sys.executable,'-B',str(INPUT/'qa/test.py'),'child',str(INPUT/'qa/wrapper.py'),str(p),mode],stdout=stdout,stderr=stderr,start_new_session=True)
   row={'mode':mode,'pid':proc.pid,'start':w.start(proc.pid)};processes.append(row)
   lockfd=None
   try:
    wait_file(p/'held.json',proc)
    if mode=='release':w.write_release(p)
    if mode=='malformed':
     fd=os.open(p/'gate.json',os.O_WRONLY);fcntl.flock(fd,fcntl.LOCK_EX);os.ftruncate(fd,0);os.write(fd,b'{"action":"release"}');os.close(fd)
    if mode=='locked':lockfd=os.open(p/'gate.json',os.O_RDWR);fcntl.flock(lockfd,fcntl.LOCK_EX)
    code=proc.wait(timeout=5);row['code']=code
   finally:
    if lockfd is not None:os.close(lockfd)
    if proc.poll() is None:proc.kill();proc.wait();row['forcedCleanup']=True
  packets=[json.loads(line) for line in log.read_text().splitlines()];outcomes=[x for x in packets if x.get('kind')=='effect-outcome'];disconnected=[x for x in packets if x.get('kind')=='host-disconnected'];cleanup=packets[-1]
  check(mode+' process and watchdog terminate normally',not row.get('forcedCleanup') and cleanup=={'kind':'cleanup','watchdogAlive':False,'code':code})
  check(mode+' interleaved refresh remains real send',sum(x.get('kind')=='host-refresh' for x in packets)==1)
  if mode=='release':check('normal release exit0 exact receipt no disconnect',code==0 and outcomes==[receipt()] and not disconnected)
  else:check(mode+' clean unwind exit1 one disconnect no synthetic effect',code==1 and len(disconnected)==1 and not outcomes)
 for rel,digest in rows.items():assert sha(ROOT/rel)==digest
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])
