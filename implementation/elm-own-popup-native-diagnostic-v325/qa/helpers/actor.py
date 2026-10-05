"""Owned GTK actor. Command receipt is not configure/pixel/server retirement proof."""
import hashlib,json,os,re,subprocess,time
from pathlib import Path
from journal import Refused,parse

PLAIN={'create-owners','create-family','open-modal','close-modal','close-owner','open-nested','close-nested','open-popover','close-popover','inspect','quit'}
TARGETED={'minimize','restore','maximize','unmaximize'}

def remaining(deadline):
 value=deadline-time.monotonic()
 if value<=0:raise Refused('Original absolute six-second stage deadline')
 return value

def command(sequence,operation,role=None):
 if type(sequence) is not int or not 1<=sequence<=2**63-1:raise Refused('command sequence')
 if operation in PLAIN and role is None:return f'{sequence} {operation}\n'.encode('ascii')
 if operation in TARGETED and role in ('A','C'):return f'{sequence} {operation} {role}\n'.encode('ascii')
 raise Refused('closed GTK command')

class Actor:
 def __init__(self,session,host,binary,directory,deadline,*,profile="independent-groups"):
  if profile not in ("independent-groups","default-group"):raise Refused("closed GTK profile")
  self.profile=profile
  self.session=session;self.host=host;self.directory=Path(directory);self.directory.mkdir(mode=0o700,parents=True,exist_ok=False)
  self.stdout=self.directory/'journal.jsonl';self.stderr=self.directory/'wayland.log';self.record={'nativeAccepted':False,'argv':[str(binary),'--run' if profile=='independent-groups' else '--run-default-group'],'commands':[]};self.rows=[];self.number=0;self.process=None
  self.persist()
  try:
   remaining(deadline)
   with self.stdout.open('xb',buffering=0) as out,self.stderr.open('xb',buffering=0) as err:
    self.process=subprocess.Popen(self.record['argv'],stdin=subprocess.PIPE,stdout=out,stderr=err,env=dict(session.env,ELM_GTK_ROLE_QA='1',GDK_BACKEND='wayland',WAYLAND_DEBUG='client'),cwd=session.host.runtime,start_new_session=True)
   owned=host.original.process(self.process.pid);owned.update(name='gtk-role-client',command=self.record['argv'],log=str(self.stderr));session.host.processes.append((self.process,owned))
   self.record.update(process=owned,registered=True);self.pid=self.process.pid;self.started=str(owned['startTime']) if 'startTime' in owned else Path('/proc',str(self.pid),'stat').read_text().rsplit(')',1)[1].split()[19]
   self.record['actualStart']=self.started;self.persist()
   self.wait(lambda rows:any(r['event']=='ready' for r in rows),deadline)
  except BaseException as error:
   self.record['error']=repr(error);self.persist();self.abort();raise
 def persist(self):
  for name,path,cap in [('stdout',self.stdout,2*1024*1024),('stderr',self.stderr,8*1024*1024)]:
   if path.exists():
    self.record[name+'Bytes']=path.stat().st_size
    with path.open('rb') as source:data=source.read(cap)
    self.record[name+'CapturedBytes']=len(data);self.record[name+'PrefixSHA256']=hashlib.sha256(data).hexdigest();self.record[name+'Truncated']=self.record[name+'Bytes']>len(data)
  (self.directory/'actor.json').write_text(json.dumps(self.record,indent=2)+'\n')
 def read(self):
  self.session.guard()
  if self.stdout.stat().st_size>2*1024*1024 or self.stderr.stat().st_size>8*1024*1024:raise Refused('owned actor journal/protocol byte bounds')
  with self.stdout.open('rb') as source:raw=source.read(2*1024*1024+1)
  self.rows=parse(raw,pid=self.pid,started=self.started,previous=self.rows,profile=self.profile);self.persist();return self.rows
 def wait(self,predicate,deadline):
  while remaining(deadline):
   rows=self.read();value=predicate(rows);remaining(deadline)
   if value:return value
   if self.process.poll() is not None:raise Refused('GTK actor exited before required evidence')
   time.sleep(min(.02,remaining(deadline)))
 def send(self,operation,deadline,role=None):
  self.number+=1;payload=command(self.number,operation,role);attempt={'sequence':self.number,'operation':operation,'role':role,'payload':payload.decode('ascii'),'startedMonotonic':time.monotonic()};self.record['commands'].append(attempt);self.persist()
  try:
   remaining(deadline);self.session.guard()
   if self.process.poll() is not None or self.process.stdin.closed:raise Refused('actor not live')
   self.process.stdin.write(payload);self.process.stdin.flush();attempt['written']=True;self.persist()
   if operation=='quit':return attempt
   self.wait(lambda rows:any(r['event']=='request' and r['requestSequence']==self.number and r.get('command')==operation and r.get('requestedRole')==role for r in rows),deadline)
   attempt['requestObserved']=True;self.persist();return attempt
  except BaseException as error:attempt['error']=repr(error);self.persist();raise
 def close(self,deadline):
  try:
   self.send('quit',deadline)
   if not self.process.stdin.closed:self.process.stdin.close()
   self.process.wait(timeout=remaining(deadline));remaining(deadline);self.read()
   with self.stdout.open('rb') as source:terminal=source.read(2*1024*1024+1)
   if not terminal.endswith(b'\n') or not self.rows or self.rows[-1]['event']!='normalexit' or sum(r['event']=='normalexit' for r in self.rows)!=1 or self.process.returncode!=0:raise Refused('complete terminal journal with final unique normalexit required')
   self.record['normalExit']=True;self.record['exitCode']=self.process.returncode;self.persist()
  except BaseException as error:self.record['closeError']=repr(error);self.persist();self.abort();raise
 def abort(self):
  if self.process is not None:
   if self.process.stdin and not self.process.stdin.closed:self.process.stdin.close()
   if self.process.poll() is None:
    self.process.terminate();self.record['failureCleanupTerminate']=True
    try:self.process.wait(timeout=.5)
    except subprocess.TimeoutExpired:self.process.kill();self.record['failureCleanupKill']=True;self.process.wait(timeout=.5)
   self.record['exitCode']=self.process.returncode
  self.persist()
