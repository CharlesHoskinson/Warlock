"""Strict source-backed owned QS startup/registry/normal shutdown. Import is inert."""
from pathlib import Path
import hashlib,json,os,re,subprocess,time
import helper_observer as proc
B=Path(__file__).resolve().parent
ROW_KEYS={'id','pid','shell_id','config_path','launch_time'}
class Pending(RuntimeError):pass
class Refused(RuntimeError):pass

def parse_instances(result):
 if result.returncode!=0 or result.stderr!='':raise Refused('QS list failed/unknown stderr')
 if result.stdout=='No running instances.\n':return []
 try:rows=json.loads(result.stdout,object_pairs_hook=unique)
 except (ValueError,TypeError) as error:raise Refused('Unknown QS list output') from error
 if not isinstance(rows,list) or not rows:raise Refused('Nonempty actual QS JSON list required')
 ids=set();pids=set()
 for row in rows:
  if not isinstance(row,dict) or set(row)!=ROW_KEYS or type(row['pid']) is not int or not 0<row['pid']<(1<<31) or not all(isinstance(row[key],str) and row[key] for key in ROW_KEYS-{'pid'}):raise Refused('Unknown actual QS instance schema')
  if not re.fullmatch(r'[A-Za-z0-9]+',row['id']) or not re.fullmatch(r'[0-9a-f]{32}',row['shell_id']) or not Path(row['config_path']).is_absolute() or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?',row['launch_time']):raise Refused('Noncanonical actual QS instance fields')
  if row['id'] in ids or row['pid'] in pids:raise Refused('Duplicate actual QS instance')
  ids.add(row['id']);pids.add(row['pid'])
 return rows

def unique(pairs):
 row={}
 for key,value in pairs:
  if key in row:raise ValueError('Duplicate JSON instance key')
  row[key]=value
 return row

def ping_state(result):
 if result.returncode==0 and result.stdout=='ok\n' and result.stderr=='':return 'ready'
 if result.returncode==1 and result.stdout=='' and result.stderr in ('omarchy-shell is not running\n','omarchy-shell is not ready\n'):return 'pending'
 raise Refused('Unknown actual QS IPC startup reply')

class Lifecycle:
 def __init__(self,process,identity,command,environment,session_guard,config_path,gate_command=None):
  self.process=process;self.identity=identity;self.command=list(command);self.env=environment;self.session_guard=session_guard;self.config=Path(config_path).resolve();self.gate_command=gate_command
  self.executable=Path(command[0]).resolve();self.executable_sha=proc.digest(self.executable);self.gate_sha=proc.digest(B/'exec_gate.py');self.python_sha=proc.digest('/usr/bin/python3');self.final=False;self.records=[];self.kill_sent=False;self.ready=False
  self.source_sha=proc.digest(self.config);self.launcher=B/'payload/omarchy/bin/omarchy-shell';self.launcher_sha=proc.digest(self.launcher)
 def guard(self,allow_gate=False):
  self.session_guard()
  if self.process.poll() is not None or not proc.still_live(self.identity):raise Refused('Exact owned QS exited during startup/selection')
  path=Path('/proc')/str(self.identity['pid']);argv=proc.cmdline(self.identity['pid']);executable=(path/'exe').resolve()
  if proc.digest(self.config)!=self.source_sha or proc.digest(self.launcher)!=self.launcher_sha:raise Refused('Exact QS config/launcher source changed')
  values=dict(part.split(b'=',1) for part in (path/'environ').read_bytes().split(b'\0') if b'=' in part)
  for key in ('HOME','PATH','XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY','OMARCHY_PATH','WINDOW_QA_HELPER_CONFIG','WINDOW_MOTION_NATIVE_CONFIG','DBUS_SESSION_BUS_ADDRESS'):
   value=self.env.get(key)
   if values.get(key.encode())!=(value.encode() if value is not None else None):raise Refused('Exact owned QS private environment changed')
  if (path/'cgroup').read_text()!=Path('/proc/self/cgroup').read_text():raise Refused('Exact owned QS QA scope changed')
  pending=False
  if argv==self.command and executable==self.executable and proc.digest(executable)==self.executable_sha:self.final=True
  elif allow_gate and not self.final and self.gate_command is not None and argv==self.gate_command and executable==Path('/usr/bin/python3').resolve() and proc.digest(executable)==self.python_sha and proc.digest(B/'exec_gate.py')==self.gate_sha:pending=True
  else:raise Refused('Exact QS final executable/source/argv changed')
  if pending:raise Pending('Exact startup exec gate has not reached final QS argv')
 def invoke(self,role,command,seconds=4):
  self.guard();start=time.monotonic_ns();record=dict(role=role,command=command,startedNs=start,qsIdentity=self.identity,nativeOutcomeNotInferred=True)
  child=subprocess.Popen(command,env=self.env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
  try:
   record['processIdentity']=proc.process(child.pid)
   stdout,stderr=child.communicate(timeout=seconds)
   result=subprocess.CompletedProcess(command,child.returncode,stdout,stderr);record.update(returncode=result.returncode,stdout=stdout,stderr=stderr,completedNs=time.monotonic_ns(),originalProbeGone=not proc.still_live(record['processIdentity']))
  except BaseException as error:
   if child.poll() is None:child.kill()
   stdout,stderr=child.communicate(timeout=2)
   record.update(error=repr(error),returncode=child.returncode,stdout=stdout,stderr=stderr,completedNs=time.monotonic_ns());self.records.append(record);raise
  self.records.append(record);self.session_guard()
  return result
 def await_ready(self,seconds=15):
  deadline=time.monotonic()+seconds
  while time.monotonic()<deadline:
   try:self.guard(allow_gate=True)
   except Pending:time.sleep(.03);continue
   result=self.invoke('startup-ping',[str(self.launcher),'shell','ping'])
   state=ping_state(result);self.guard()
   if state=='ready':self.ready=True;return dict(exactReady=True,identity=self.identity,records=self.records)
   time.sleep(.05)
  raise Refused('Exact QS startup deadline expired')
 def selected(self):
  rows=parse_instances(self.invoke('instance-selection',['/usr/bin/qs','--no-color','list','-a','-j']))
  matches=[row for row in rows if row['pid']==self.identity['pid']]
  if not matches:return None
  if len(matches)!=1 or Path(matches[0]['config_path']).resolve()!=self.config:raise Refused('Exact QS PID registered under a different config')
  self.guard();return matches[0]
 def close(self,seconds=10):
  if self.kill_sent:raise Refused('Exact QS normal kill already submitted; no second send')
  if self.process.poll() is not None:
   self.process.wait(timeout=1)
   if self.process.returncode!=0 or proc.still_live(self.identity):raise Refused('Owned QS exited abnormally before normal close')
   return dict(exitCode=0,exactOriginalGone=True,normalQuit=False,naturallyExitedBeforeClose=True,ready=self.ready,records=self.records)
  deadline=time.monotonic()+seconds;instance=None
  while time.monotonic()<deadline:
   try:self.guard(allow_gate=True)
   except Pending:time.sleep(.03);continue
   instance=self.selected()
   if instance is not None:break
   time.sleep(.05)
  if instance is None:raise Refused('Exact owned QS registry deadline expired before normal close')
  self.guard();self.kill_sent=True
  result=self.invoke('normal-kill',['/usr/bin/qs','--no-color','kill','--pid',str(self.identity['pid'])])
  if result.returncode!=0 or result.stderr or result.stdout!='Killed '+instance['id']+'\n':raise Refused('Actual exact QS normal kill reply failed/unknown')
  self.process.wait(timeout=8)
  if self.process.returncode!=0 or proc.still_live(self.identity):raise Refused('Actual exact QS normal exit failed')
  return dict(exitCode=0,exactOriginalGone=True,normalQuit=True,selectedInstance=instance,records=self.records)
