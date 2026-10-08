"""Installed Files navigation; exact Quickshell instance, fixed argv, no file ops.

Uses the installed launch/reuse IPC contract. Paths are navigation data only;
frontend values cannot select an executable, QML root, instance or IPC method.
"""
import copy,hashlib,json,os,pathlib,re,secrets,selectors,stat,subprocess,time
from endpoint import Refused,binding,canonical,exact,start_time,unique
COLLECTIONS={'recent','images','videos','documents','downloads','large','screenshots'}
class Unknown(RuntimeError):pass

def command(args,deadline,environment=None):
 if args[0]!='/usr/bin/qs':raise Refused('Files executable')
 process=subprocess.Popen([args[0],"--log-rules","quickshell.bare.info=false",*args[1:]],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=environment or os.environ,start_new_session=True)
 output=bytearray();errors=bytearray()
 try:
  with selectors.DefaultSelector() as selector:
   for stream,label in [(process.stdout,'out'),(process.stderr,'error')]:os.set_blocking(stream.fileno(),False);selector.register(stream,selectors.EVENT_READ,label)
   while selector.get_map():
    left=deadline-time.monotonic()
    if left<=0:raise Unknown('Files native response not confirmed')
    for key,_ in selector.select(left):
     chunk=os.read(key.fileobj.fileno(),8192)
     if not chunk:selector.unregister(key.fileobj);continue
     target=output if key.data=='out' else errors;target.extend(chunk)
     if len(target)>(262144 if key.data=='out' else 8192):raise Unknown('Files native response capacity')
  process.wait(timeout=max(.001,deadline-time.monotonic()))
  if process.returncode:raise Refused('Installed Files operation refused')
  return output.decode('utf-8')
 finally:
  if process.poll() is None:process.terminate()
  try:process.wait(timeout=.3)
  except subprocess.TimeoutExpired:process.kill();process.wait()
  process.stdout.close();process.stderr.close()

class Explorer:
 def __init__(self,app_root=None):
  self.root=pathlib.Path(app_root or pathlib.Path.home()/'.local/share/omarchy-files').resolve()
  self.service=str(secrets.randbelow(2**64-1)+1);self.revision=0;self.last=None;self.identity=None;self.spent=set();self.high=0;self.scope=None
  self.qs=pathlib.Path('/usr/bin/qs').resolve();self.binary=None
  try:self.binary=self.qs.stat()
  except OSError:pass
 def __enter__(self):return self
 def __exit__(self,*_):pass
 def source(self):
  if not self.binary or not self.root.is_dir() or not (self.root/'shell.qml').is_file():raise Refused('Installed Files unavailable')
  now=self.qs.stat()
  if (now.st_dev,now.st_ino,now.st_size,now.st_mtime_ns)!=(self.binary.st_dev,self.binary.st_ino,self.binary.st_size,self.binary.st_mtime_ns):raise Refused('Files executable changed')
  result={}
  for name in ['shell.qml','scripts/ops.sh','spec/fileops.qnt']:
   path=self.root/name
   if not path.is_file():raise Refused('Installed Files contract unavailable')
   result[name]=hashlib.sha256(path.read_bytes()).hexdigest()
  return result
 def target(self,value):
  if not isinstance(value,str) or len(value)>512 or any(ord(c)<32 or ord(c)==127 for c in value):raise Refused('Files navigation target')
  if value=='home':return value
  if value.startswith('coll:'):
   if value[5:] not in COLLECTIONS:raise Refused('Files collection unavailable')
   return value
  value=value.strip()
  if value=='~':value=str(pathlib.Path.home())
  elif value.startswith('~/'):value=str(pathlib.Path.home())+value[1:]
  if not value.startswith('/'):raise Refused('Files path must be absolute')
  pieces=[]
  for part in value.split('/'):
   if part in ('','.'):continue
   if part=='..':
    if pieces:pieces.pop()
   else:pieces.append(part)
  target='/'+('/'.join(pieces))
  if not pathlib.Path(target).is_dir():raise Refused('Files folder unavailable')
  return target
 def instances(self,deadline):
  raw=command(['/usr/bin/qs','-p',str(self.root),'list','--json'],deadline)
  rows=json.loads(raw,object_pairs_hook=unique) if raw.strip() else []
  if not isinstance(rows,list) or len(rows)>16:raise Refused('Files instance capacity')
  if len(rows)>1:raise Refused('Multiple Files instances; choose an existing window')
  if not rows:return None
  row=rows[0];pid=row.get('pid');identifier=row.get('id');config=row.get('config_path')
  if type(pid) is not int or pid<=0 or not isinstance(identifier,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}',identifier) or not isinstance(config,str) or pathlib.Path(config).resolve()!=self.root/'shell.qml':raise Refused('Files native instance')
  peer={'pid':pid,'start':start_time(pid),'instance':identifier};self.verify_peer(peer);return peer
 def verify_peer(self,peer):
  proc=pathlib.Path('/proc')/str(peer['pid'])
  if proc.stat().st_uid!=os.getuid() or start_time(peer['pid'])!=peer['start'] or (proc/'exe').resolve()!=self.qs:raise Refused('Files instance changed')
  image=(proc/'exe').stat()
  if (image.st_dev,image.st_ino)!=(self.binary.st_dev,self.binary.st_ino):raise Refused('Files executable identity changed')
 def ipc(self,peer,method,args,deadline):
  if method not in ('migrationStatus','uiState','open'):raise Refused('Files native method')
  self.verify_peer(peer)
  result=command(['/usr/bin/qs','-p',str(self.root),'ipc','--id',peer['instance'],'call','files',method,*args],deadline)
  self.verify_peer(peer);return result
 def probe(self,peer,deadline):
  status=json.loads(self.ipc(peer,'migrationStatus',[],deadline),object_pairs_hook=unique)
  if status.get('pid')!=peer['pid'] or status.get('instance')!=peer['instance'] or status.get('ready') is not True or status.get('error'):raise Refused('Files instance not ready')
  ui=json.loads(self.ipc(peer,'uiState',[],deadline),object_pairs_hook=unique)
  collection=ui.get('collId');view=ui.get('view');cwd=ui.get('cwd');visible=ui.get('visible')
  if not isinstance(collection,str) or collection not in COLLECTIONS|{''} or view not in ('home','folder') or type(visible) is not bool or not isinstance(cwd,str) or not cwd.startswith('/') or len(cwd)>512:raise Refused('Files observed location')
  target='coll:'+collection if collection else 'home' if view=='home' else cwd
  return {**peer,'target':target,'visible':visible}
 def observe(self,deadline=None,advance=False):
  deadline=deadline or time.monotonic()+2;value={'available':False,'reason':'Installed Files unavailable','peer':None};identity=None
  try:
   source=self.source();peer=self.instances(deadline);observed=self.probe(peer,deadline) if peer else None
   value={'available':True,'reason':'','peer':observed};identity={'source':source,'peer':peer}
  except (Refused,Unknown,OSError,ValueError,subprocess.SubprocessError):pass
  if advance or value!=self.last or identity!=self.identity:
   if self.revision>=2**64-1:raise Refused('Files revision exhausted')
   self.revision+=1;self.last=copy.deepcopy(value);self.identity=copy.deepcopy(identity);self.spent={item for item in self.spent if item[0]>=self.revision-32}
  public=copy.deepcopy(value)
  if public['peer'] is not None:public['peer']['pid']=str(public['peer']['pid'])
  return {'service':self.service,'revision':str(self.revision),**public}
 def verify(self,request,client,effect):
  exact(request,['protocolVersion','kind','binding','requestId',*(['intent'] if effect else [])]);canonical(request['requestId'])
  if type(request['protocolVersion']) is not int or request['protocolVersion']!=3 or request['kind']!=('files-open' if effect else 'files-request') or binding(request['binding'])!=client.bound:raise Refused('Files binding')
  client.verify_process();client.verify_paths()
 def read(self,request,client):
  self.verify(request,client,False);snapshot=self.observe();self.verify(request,client,False)
  return {'protocolVersion':3,'kind':'files-snapshot','binding':client.bound,'requestId':request['requestId'],'snapshot':snapshot}
 def open(self,request,client):
  self.verify(request,client,True);intent=request['intent'];exact(intent,['service','revision','target']);canonical(intent['service']);canonical(intent['revision'])
  deadline=time.monotonic()+3;current=self.observe(deadline);status='Refused';submitted=False;key=(int(intent['revision']),intent['target']) if isinstance(intent['target'],str) else None
  if self.scope!=client.bound:self.scope=copy.deepcopy(client.bound);self.high=0
  number=int(request['requestId'])
  if number>self.high:
   self.high=number
   if intent['service']==self.service and intent['revision']==current['revision'] and current['available'] and key is not None and key not in self.spent:
    try:
     target=self.target(intent['target']);source=self.source();peer=copy.deepcopy(self.identity['peer']);self.spent.add(key)
     submitted=True
     if peer:
      self.ipc(peer,'open',[target],deadline)
     else:
      # The same installed explorer, one no-duplicate cold start. An uncertain
      # startup never falls back to another launch or a different instance.
      command(['/usr/bin/qs','-p',str(self.root),'--no-duplicate','--daemonize'],deadline,{**os.environ,'FILES_OPEN':target})
     observed=self.observe(deadline)
     actual=observed['peer'];same=(actual is not None and (peer is None or all(actual[k]==(str(peer[k]) if k=='pid' else peer[k]) for k in ('pid','start','instance'))))
     if not same or actual['target']!=target or not actual['visible'] or self.source()!=source:raise Unknown('Requested Files location not confirmed')
     # A confirmed explicit navigation creates the next proposal generation,
     # even if it was a same-location summon. Old gestures remain consumed.
     current=self.observe(deadline,advance=True);status='Opened'
    except Refused:status='Unknown' if submitted else 'Refused'
    except Exception:status='Unknown'
  if status!='Opened':
   try:current=self.observe(deadline)
   except Exception:pass
  self.verify(request,client,True)
  return {'protocolVersion':3,'kind':'files-outcome','binding':client.bound,'requestId':request['requestId'],'status':status,'snapshot':current}
