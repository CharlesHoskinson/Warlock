"""Private QA delivery fault: retain one real Committed receipt, never retry effects."""
import argparse,copy,fcntl,hashlib,importlib.util,json,os,signal,stat,sys,threading,time
from pathlib import Path
REPO=next(p for p in Path(__file__).resolve().parents if (p/'AGENTS.md').is_file() and (p/'implementation').is_dir())
SOURCE=REPO/'implementation/elm-geometry-staged-menu-build-v74'
MANIFEST_SHA='9678ba49758ba4fd7688d1c0faed2a1fafef4b91e62be3d7dad23e830fb25b5a'
MAX_BYTES=4096
class HoldFailure(RuntimeError):pass
def start(pid):
 try:
  p=Path('/proc')/str(pid)
  if p.stat().st_uid!=os.getuid():return None
  return (p/'stat').read_text().rsplit(')',1)[1].split()[19]
 except (OSError,IndexError):return None
def exact(value,keys):
 if not isinstance(value,dict) or set(value)!=set(keys):raise HoldFailure('QA exact schema')
def counter(value):
 if type(value) is not str or not value.isascii() or not value.isdecimal() or not value or value[0]=='0' or len(value)>20 or int(value)>2**64-1:raise HoldFailure('QA positive canonical counter')
def decode(raw):
 if not raw or len(raw)>MAX_BYTES:raise HoldFailure('QA control bound')
 def unique(rows):
  out={}
  for key,value in rows:
   if key in out:raise HoldFailure('QA duplicate member')
   out[key]=value
  return out
 try:return json.loads(raw,object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(HoldFailure('QA nonfinite JSON')))
 except (UnicodeError,ValueError) as error:raise HoldFailure('QA malformed JSON') from error
def directory(path):
 p=Path(path)
 if not p.is_absolute() or p.resolve(strict=True)!=p:raise HoldFailure('QA directory canonical path')
 s=p.lstat()
 if not stat.S_ISDIR(s.st_mode) or s.st_uid!=os.getuid() or stat.S_IMODE(s.st_mode)!=0o700:raise HoldFailure('QA private directory')
 return p,(s.st_dev,s.st_ino)
def gate_fd(root,write=False):
 fd=os.open(root/'gate.json',(os.O_RDWR if write else os.O_RDONLY)|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  s=os.fstat(fd)
  if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or stat.S_IMODE(s.st_mode)!=0o600 or s.st_nlink!=1 or s.st_size>MAX_BYTES:raise HoldFailure('QA owned regular gate')
  return fd,(s.st_dev,s.st_ino)
 except BaseException:os.close(fd);raise
class ReceiptHold:
 def __init__(self,control_directory,incarnation,send,timeout=5,clock=time.monotonic,operation='maximize'):
  counter(incarnation)
  if operation not in ('maximize','restore-geometry'):raise HoldFailure('QA closed geometry operation')
  self.operation=operation
  if not 0<timeout<=5:raise HoldFailure('QA timeout bound')
  self.root,self.directory_identity=directory(control_directory);self.incarnation=incarnation;self.send=send;self.timeout=timeout;self.clock=clock
  self.pid=os.getpid();self.start=start(self.pid)
  if not self.start:raise HoldFailure('QA process identity')
  fd,self.gate_identity=gate_fd(self.root)
  try:
   fcntl.flock(fd,fcntl.LOCK_SH|fcntl.LOCK_NB)
   if decode(os.read(fd,MAX_BYTES+1))!={'action':'hold'}:raise HoldFailure('QA initial hold gate')
  finally:os.close(fd)
  self.lock=threading.RLock();self.stop=threading.Event();self.thread=None;self.failure=None;self.seen=False;self.released=False;self.receipt=None;self.deadline=None;self.last_gate=None
 def guard(self):
  _,identity=directory(self.root)
  if identity!=self.directory_identity or start(self.pid)!=self.start or self.pid!=os.getpid():raise HoldFailure('QA owner identity changed')
  s=(self.root/'gate.json').lstat()
  if (s.st_dev,s.st_ino)!=self.gate_identity or not stat.S_ISREG(s.st_mode):raise HoldFailure('QA gate replaced')
 def intercept(self,frame):
  with self.lock:
   self.guard()
   matching=isinstance(frame,dict) and frame.get('kind')=='effect-outcome' and type(frame.get('effectProtocol')) is int and frame.get('effectProtocol')==2 and isinstance(frame.get('intent'),dict) and frame['intent'].get('operation')==self.operation and frame['intent'].get('incarnation')==self.incarnation
   if not matching:self.send(frame);return
   exact(frame,['protocolVersion','kind','effectProtocol','binding','intent','status','reason','revision','outputGeneration'])
   if type(frame['protocolVersion']) is not int or frame['protocolVersion']!=3 or frame['status']!='Committed' or type(frame['reason']) is not str:raise HoldFailure('QA requires actual committed receipt')
   try:valid_reason=len(frame['reason'].encode('utf-16-le'))//2<=256 and not any(ord(c)<32 or 127<=ord(c)<=159 for c in frame['reason'])
   except UnicodeEncodeError:valid_reason=False
   if not valid_reason:raise HoldFailure('QA bounded receipt reason')
   exact(frame['binding'],['lifetime','session','frontend']);exact(frame['intent'],['request','generation','incarnation','operation','context']);exact(frame['intent']['context'],['lifetime','epoch','output','revision'])
   for x in [*frame['binding'].values(),frame['revision'],frame['outputGeneration'],frame['intent']['request'],frame['intent']['generation'],frame['intent']['incarnation'],*frame['intent']['context'].values()]:counter(x)
   if frame['intent']['context']['lifetime']!=frame['binding']['lifetime'] or frame['intent']['context']['epoch']!=frame['binding']['frontend'] or self.seen:raise HoldFailure('QA correlation or duplicate held receipt')
   encoded=json.dumps(frame,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()
   if len(encoded)>MAX_BYTES:raise HoldFailure('QA receipt bound')
   self.receipt=copy.deepcopy(frame);self.seen=True;self.deadline=self.clock()+self.timeout
   record={'wrapper':{'pid':self.pid,'start':self.start},'effectProtocol':2,'binding':copy.deepcopy(frame['binding']),'intent':copy.deepcopy(frame['intent']),'receipt':copy.deepcopy(frame)}
   raw=json.dumps(record,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()
   if len(raw)>MAX_BYTES:raise HoldFailure('QA held record bound')
   fd=os.open(self.root/'held.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
   try:
    with os.fdopen(fd,'wb') as out:out.write(raw);out.flush();os.fsync(out.fileno())
   except BaseException:raise
 def release(self,packet):
  with self.lock:
   self.guard();exact(packet,['action','wrapper','effectProtocol','binding','intent']);exact(packet['wrapper'],['pid','start'])
   if self.receipt is None or self.released or self.clock()>=self.deadline:raise HoldFailure('QA stale or duplicate release')
   if packet['action']!='release' or type(packet['effectProtocol']) is not int or packet['effectProtocol']!=2 or type(packet['wrapper']['pid']) is not int or packet['wrapper']!={'pid':self.pid,'start':self.start} or packet['binding']!=self.receipt['binding'] or packet['intent']!=self.receipt['intent']:raise HoldFailure('QA exact release correlation')
   self.send(copy.deepcopy(self.receipt));self.released=True
 def poll_gate(self):
  self.guard()
  if not self.released and self.deadline is not None and self.clock()>=self.deadline:raise HoldFailure('QA hold deadline')
  fd,identity=gate_fd(self.root)
  try:
   if identity!=self.gate_identity:raise HoldFailure('QA gate identity')
   try:fcntl.flock(fd,fcntl.LOCK_SH|fcntl.LOCK_NB)
   except BlockingIOError:return
   raw=os.read(fd,MAX_BYTES+1)
  finally:os.close(fd)
  if self.released and raw==self.last_gate:return
  packet=decode(raw)
  if packet=={'action':'hold'}:
   if self.released:raise HoldFailure('QA gate reversed after release')
   if self.deadline is not None and self.clock()>=self.deadline:raise HoldFailure('QA hold deadline')
   return
  self.release(packet);self.last_gate=raw
 def watch(self):
  while not self.stop.wait(.01):
   try:self.poll_gate()
   except Exception as error:
    self.failure=error
    if start(self.pid)==self.start:os.kill(self.pid,signal.SIGUSR1)
    return
 def start_watch(self):
  self.thread=threading.Thread(target=self.watch,name='qa-receipt-watch',daemon=False);self.thread.start()
 def close(self):
  self.stop.set()
  if self.thread:self.thread.join(timeout=1)
  if self.thread and self.thread.is_alive():raise HoldFailure('QA watchdog did not finish')
  if self.failure:raise HoldFailure('QA watchdog failure') from self.failure
  if self.seen and not self.released:raise HoldFailure('QA receipt lost at EOF')
def supervise(holder,main):
 old=signal.getsignal(signal.SIGUSR1)
 def interrupted(signum,frame):raise HoldFailure('QA receipt hold failure')
 signal.signal(signal.SIGUSR1,interrupted);result=1;failure=None
 try:
  holder.start_watch();result=main()
 except Exception as error:failure=error
 finally:
  try:holder.close()
  except Exception as error:failure=failure or error
  signal.signal(signal.SIGUSR1,old)
 if failure:
  with holder.lock:holder.send({'protocolVersion':3,'kind':'host-disconnected'})
  return 1
 return result or 0
def write_release(control_directory):
 root,_=directory(control_directory)
 fd=os.open(root/'held.json',os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  s=os.fstat(fd)
  if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or stat.S_IMODE(s.st_mode)!=0o600:raise HoldFailure('QA owned held record')
  record=decode(os.read(fd,MAX_BYTES+1))
 finally:os.close(fd)
 exact(record,['wrapper','effectProtocol','binding','intent','receipt']);exact(record['wrapper'],['pid','start'])
 if type(record['wrapper']['pid']) is not int or start(record['wrapper']['pid'])!=record['wrapper']['start']:raise HoldFailure('QA wrapper owner disappeared')
 packet={key:record[key] for key in ['wrapper','effectProtocol','binding','intent']};packet['action']='release'
 raw=json.dumps(packet,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()
 if len(raw)>MAX_BYTES:raise HoldFailure('QA release bound')
 fd,_=gate_fd(root,True)
 try:
  fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);os.ftruncate(fd,0)
  if os.write(fd,raw)!=len(raw):raise HoldFailure('QA incomplete control write')
  os.fsync(fd)
 finally:os.close(fd)
def load_backend():
 manifest=SOURCE/'component-manifest.json'
 if hashlib.sha256(manifest.read_bytes()).hexdigest()!=MANIFEST_SHA:raise HoldFailure('QA frozen backend manifest')
 m=json.loads(manifest.read_text());build=Path(m['buildRoot'])
 for rel,w in m['artifacts'].items():
  if rel.startswith('inputs/adapter/') and hashlib.sha256((build/rel).read_bytes()).hexdigest()!=w:raise HoldFailure('QA captured backend changed')
 broker=REPO/'implementation/elm-geometry-broker-coherent-v64'
 held=broker/'qa/held-source-manifest.json'
 if hashlib.sha256(held.read_bytes()).hexdigest()!='3aa379a0c7c694455d32f08c69d047b4ac0dd9200015d30b40e68593938b2161':raise HoldFailure('QA exact held broker')
 for source in sorted((broker/'adapter').glob('*.py')):
  p=build/'inputs/adapter'/source.name
  if hashlib.sha256(p.read_bytes()).hexdigest()!=hashlib.sha256(source.read_bytes()).hexdigest():raise HoldFailure('QA broker sibling changed')
  existing=sys.modules.get(source.stem)
  if existing is not None and Path(getattr(existing,'__file__','')).resolve()!=p.resolve():raise HoldFailure('QA foreign cached broker dependency')
 sys.path.insert(0,str(build/'inputs/adapter'))
 p=build/'inputs/adapter/daemon.py';spec=importlib.util.spec_from_file_location('frozen_receipt_hold_backend',p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def main():
 sys.path.insert(0,'/home/hoskinson/window-integration-qa')
 from qa_launch import require_qa_scope
 require_qa_scope()
 parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='operation',required=True)
 release=sub.add_parser('release');release.add_argument('--control-directory',required=True)
 run=sub.add_parser('run');run.add_argument('--control-directory',required=True);run.add_argument('--incarnation',required=True);run.add_argument('--config',required=True);run.add_argument('--effect-operation',choices=['maximize','restore-geometry'],default='maximize')
 args=parser.parse_args()
 if args.operation=='release':write_release(args.control_directory);return 0
 backend=load_backend();holder=ReceiptHold(args.control_directory,args.incarnation,backend.send,operation=args.effect_operation);backend.send=holder.intercept
 old=sys.argv;sys.argv=['daemon',args.config]
 try:return supervise(holder,backend.main)
 finally:sys.argv=old
if __name__=='__main__':raise SystemExit(main())
