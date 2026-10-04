"""Persistent owned parent input controller; receipts are admission, not recipient proof."""
import hashlib,json,os,re,subprocess,time
from pathlib import Path
from actor import remaining
from journal import Refused,pairs,constant

PATTERN=re.compile(r'(?:motion (?:0|[1-9][0-9]{0,3}) (?:0|[1-9][0-9]{0,3})|(?:press|release) (?:272|273|274)|(?:key-press|key-release) (?:30|42)|observe [1-9][0-9]{0,9} [1-9][0-9]{0,19})')
class Parent:
 def __init__(self,session,host,binary,directory,deadline,verify_peer):
  self.session=session;self.host=host;self.peer=verify_peer;self.directory=Path(directory);self.directory.mkdir(mode=0o700,parents=True,exist_ok=False);self.stdout=self.directory/'stdout.jsonl';self.stderr=self.directory/'stderr.log';self.process=None;self.held=set();self.commands=[];self.rows=[];self.record={'probeAccepted':False,'physicalHardwareAccepted':False,'argv':[str(binary)],'commands':self.commands};self.persist()
  try:
   self.record['peerBefore']=self.peer(deadline)
   with self.stdout.open('xb',buffering=0) as out,self.stderr.open('xb',buffering=0) as err:
    self.process=subprocess.Popen(self.record['argv'],stdin=subprocess.PIPE,stdout=out,stderr=err,env=dict(session.host.env,ELM_PARENT_INPUT_QA='1'),cwd=session.host.runtime,start_new_session=True)
   row=host.original.process(self.process.pid);row.update(name='persistent-parent-input',command=self.record['argv'],log=str(self.stderr));session.host.processes.append((self.process,row));self.record.update(registered=True,process=row);self.persist()
   self.wait(1,deadline)
  except BaseException as error:self.record['error']=repr(error);self.persist();self.abort();raise
 def persist(self):
  for label,path in [('stdout',self.stdout),('stderr',self.stderr)]:
   if path.exists():
    self.record[label+'Bytes']=path.stat().st_size
    with path.open('rb') as source:data=source.read(65536)
    self.record[label+'CapturedBytes']=len(data);self.record[label+'PrefixSHA256']=hashlib.sha256(data).hexdigest();self.record[label+'Truncated']=self.record[label+'Bytes']>len(data)
  (self.directory/'record.json').write_text(json.dumps(self.record,indent=2)+'\n')
 def read(self):
  self.session.guard()
  if self.stdout.stat().st_size>65536 or self.stderr.stat().st_size>65536:raise Refused('persistent parent output bound')
  with self.stdout.open('rb') as source:raw=source.read(65537)
  complete=raw[:raw.rfind(b'\n')+1]
  if any(len(line)>4096 for line in complete.split(b'\n')):raise Refused('parent frame bound')
  try:rows=[json.loads(line,object_pairs_hook=pairs,parse_constant=constant) for line in complete.decode('utf-8').split('\n')[:-1]]
  except (UnicodeError,ValueError,RecursionError) as error:raise Refused('parent strict JSON/UTF8') from error
  if rows[:len(self.rows)]!=self.rows:raise Refused('parent observed prefix changed')
  if rows:
   ready=rows[0]
   if type(ready) is not dict or set(ready)!={'ready','scope'} or ready.get('ready') is not True or type(ready['ready']) is not bool or ready['scope']!='parent-notify-only':raise Refused('canonical parent readiness')
  if len(rows)>len(self.commands)+1:raise Refused('unsolicited or duplicate parent receipt')
  for index,row in enumerate(rows[1:],1):
   observing=self.commands[index-1]['command'].startswith('observe ')
   fields={'sequence','accepted','scope','observation'} if observing else {'sequence','accepted','scope'}
   if type(row) is not dict or set(row)!=fields or type(row.get('sequence')) is not int or row['sequence']!=index or type(row.get('accepted')) is not bool or row['accepted'] is not True or row['scope']!=('parent-surface-observation' if observing else 'parent-notify-only'):raise Refused('exact positive parent receipt')
  self.rows=rows;self.persist();return rows
 def wait(self,count,deadline):
  # Existing native helper transport cap3 clipped to enclosing absolute stage.
  transport_end=min(deadline,time.monotonic()+3)
  while remaining(transport_end):
   rows=self.read();remaining(deadline)
   if len(rows)==count:return rows[-1]
   if self.process.poll() is not None:raise Refused('parent helper ended before receipt')
   time.sleep(min(.01,remaining(transport_end)))
 def send(self,text,deadline):
  if type(text) is not str or not PATTERN.fullmatch(text) or len(self.commands)>=64:raise Refused('closed bounded parent command')
  self.record['peerBeforeCommand']=self.peer(deadline);entry={'sequence':len(self.commands)+1,'command':text,'startedMonotonic':time.monotonic()};self.commands.append(entry);self.persist()
  try:
   remaining(deadline)
   if self.process.poll() is not None:raise Refused('parent helper not live')
   if text.startswith('press ') or text.startswith('key-press '):
    self.held.add(('key' if text.startswith('key-') else 'button',text.split()[1]));self.record['potentialHeldInput']=True
   self.process.stdin.write((text+'\n').encode('ascii'));self.process.stdin.flush();entry['written']=True;self.persist()
   receipt=self.wait(len(self.commands)+1,deadline)
   if text.startswith('release ') or text.startswith('key-release '):self.held.discard(('key' if text.startswith('key-') else 'button',text.split()[1]))
   entry['receipt']=receipt;self.record['peerAfterCommand']=self.peer(deadline);self.persist();return receipt
  except BaseException as error:entry['error']=repr(error);self.persist();raise
 def close(self,deadline):
  try:
   remaining(deadline)
   if self.held:raise Refused('cannot qualify normal helper exit with unbalanced admitted/uncertain input')
   self.process.stdin.write(b'quit\n');self.process.stdin.flush();self.process.stdin.close();self.process.wait(timeout=min(3,remaining(deadline)));remaining(deadline);self.read()
   with self.stdout.open('rb') as source:raw=source.read(65537)
   if self.process.returncode!=0 or not raw.endswith(b'\n') or len(self.rows)!=len(self.commands)+1:raise Refused('normal complete parent helper exit')
   self.record.update(normalExit=True,exitCode=0);self.persist()
  except BaseException as error:self.record['closeError']=repr(error);self.persist();self.abort();raise
 def abort(self):
  if self.process is not None:
   if self.held and self.process.poll() is None and self.process.stdin and not self.process.stdin.closed:
    cleanup={'scope':'failure release-only attempt, never recipient/probe proof','held':sorted(self.held),'attempted':False}
    self.record['releaseOnlyCleanup']=cleanup;self.persist()
    try:
     self.peer(time.monotonic()+.5)
     payload=''.join(('key-release ' if kind=='key' else 'release ')+code+'\n' for kind,code in sorted(self.held)).encode('ascii')
     self.process.stdin.write(payload);self.process.stdin.flush();cleanup['attempted']=True
    except BaseException as error:cleanup['error']=repr(error)
    self.persist()
   if self.process.stdin and not self.process.stdin.closed:self.process.stdin.close()
   if self.process.poll() is None:
    self.process.terminate();self.record['failureCleanupTerminate']=True
    try:self.process.wait(timeout=.5)
    except subprocess.TimeoutExpired:self.process.kill();self.record['failureCleanupKill']=True;self.process.wait(timeout=.5)
   self.record['exitCode']=self.process.returncode
   self.record['destructorReleaseFallback']='May balance parent held input on disconnect; never claimed as successful GTK recipient proof'
  self.persist()
