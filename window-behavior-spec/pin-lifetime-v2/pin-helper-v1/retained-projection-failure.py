#!/usr/bin/env -S /usr/bin/python3 -I -S
"""Candidate exact-owner pin CLI; imports do not contact or alter a desktop."""
from pathlib import Path
import base64,hashlib,json,os,re,socket,stat,struct,sys,time
class Refused(RuntimeError):pass
class Uncertain(Refused):pass
FIELDS={'address','stableId','pid','session','compositorPid','compositorStart','incarnation','epoch','generation'}
FORBIDDEN=('DISPLAY','AT_SPI_BUS_ADDRESS','WAYLAND_SOCKET','SESSION_MANAGER','LD_PRELOAD','LD_AUDIT','PYTHONPATH','PYTHONHOME','DBUS_STARTER_ADDRESS','DBUS_STARTER_BUS_TYPE')
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def process(pid):
 if type(pid)is not int or pid<=0:raise Refused('Exact positive process PID required')
 p=Path('/proc')/str(pid);raw=(p/'stat').read_text().rsplit(')',1)[1].split();status={k:v.strip()for k,v in (s.split(':',1)for s in (p/'status').read_text().splitlines()if':'in s)}
 if p.stat().st_uid!=os.getuid()or status.get('Uid','').split()!=[str(os.getuid())]*4:raise Refused('Process UID authority differs')
 return {'pid':pid,'start':raw[19],'parent':int(raw[1]),'pgid':int(raw[2])}
def live(expected):
 actual=process(expected['pid'])
 if any(actual[k]!=expected[k]for k in ('pid','start','pgid')):raise Refused('Captured process lifetime/group changed')
 return actual

def regular(path,mode):
 p=Path(path);s=p.lstat()
 if not stat.S_ISREG(s.st_mode)or s.st_uid!=os.getuid()or stat.S_IMODE(s.st_mode)!=mode or s.st_nlink!=1:raise Refused('Exact owned regular byte authority required')
 return s

def directory(path):
 p=Path(path);s=p.lstat()
 if not stat.S_ISDIR(s.st_mode)or s.st_uid!=os.getuid()or stat.S_IMODE(s.st_mode)!=0o700 or p.resolve()!=p.absolute():raise Refused('Exact owned nonsymlink0700 directory required')
 return p

def private_path(path,runtime):
 p=Path(path)
 if not p.is_absolute()or p.resolve()!=p or not p.is_relative_to(runtime):raise Refused('Foreign/private path symlink refused')
 for parent in p.parents:
  if parent==runtime:break
  if parent.is_relative_to(runtime):directory(parent)
 return p

def token(value):
 if not isinstance(value,dict)or set(value)!=FIELDS:raise Refused('One complete native pin token required; no active fallback')
 for k in ('pid','compositorPid'):
  if type(value[k])is not int or not 0<value[k]<=2147483647:raise Refused('Exact integer token PID required')
 patterns={'address':r'0x[0-9a-f]+','stableId':r'[0-9a-f]+','session':r'[A-Za-z0-9_]+','incarnation':r'[0-9a-f]{32}','compositorStart':r'[1-9][0-9]*','epoch':r'[1-9][0-9]*','generation':r'[1-9][0-9]*'}
 for k,pattern in patterns.items():
  if type(value[k])is not str or not re.fullmatch(pattern,value[k]):raise Refused('Canonical native token field required:'+k)
 for k in ('epoch','generation'):
  if int(value[k])>18446744073709551615:raise Refused('Native identity generation overflow')
 return dict(value)
def command(value):
 value=token(value);parts=[k+'='+str(value[k])if k in ('pid','compositorPid')else k+'="'+value[k]+'"'for k in sorted(FIELDS)]
 return ('repl print(hl.plugin.hyprbars.pin_request({'+','.join(parts)+'}))').encode()
def strict_json(raw):
 def pairs(values):
  result={}
  for key,value in values:
   if key in result:raise ValueError('Duplicate JSON key')
   result[key]=value
  return result
 def nonfinite(value):raise ValueError('Nonfinite JSON value:'+value)
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=nonfinite)
def read_config(path):
 p=Path(path);s=regular(p,0o600);fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 with os.fdopen(fd,'rb')as f:
  opened=os.fstat(f.fileno());raw=f.read(1048577)
  if len(raw)>1048576 or (opened.st_dev,opened.st_ino)!=(s.st_dev,s.st_ino):raise Refused('Config opening identity/bound differs')
 config=strict_json(raw);after=regular(p,0o600)
 projection=lambda r:(r.st_dev,r.st_ino,r.st_size,r.st_mtime_ns)
 if projection(after)!=projection(s)or not isinstance(config,dict)or type(config.get('version'))is not int or config['version']!=1:raise Refused('Explicit stable pin config required')
 config['_authority']={'path':str(p),'sha256':hashlib.sha256(raw).hexdigest(),'identity':projection(s)};return config

def unchanged(config):
 row=config['_authority'];s=regular(row['path'],0o600)
 if (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)!=tuple(row['identity'])or digest(row['path'])!=row['sha256']:raise Refused('Pin configuration changed')

def source_process(row):
 actual=live(row['identity']);p=Path('/proc')/str(actual['pid']);argv=[v.decode()for v in (p/'cmdline').read_bytes().rstrip(b'\0').split(b'\0')]
 if argv!=row['argv']or str((p/'exe').resolve())!=row['executable']or digest(p/'exe')!=row['executableSHA256']or (p/'cgroup').read_text()!=row['cgroup']:raise Refused('Captured process argv/source/exe/scope differs')
 values=dict(x.split(b'=',1)for x in (p/'environ').read_bytes().split(b'\0')if b'='in x)
 if not row['environment']or any(values.get(k.encode())!=(v.encode()if v is not None else None)for k,v in row['environment'].items()):raise Refused('Captured process selected initial-range environment differs')
 return actual

def socket_identity(config):
 runtime=directory(config['runtime']);path=private_path(config['socket']['path'],runtime);expected=runtime/'hypr'/config['selectors']['HYPRLAND_INSTANCE_SIGNATURE']/'.socket.sock'
 if path!=expected:raise Refused('Exact selected compositor socket path required')
 s=path.lstat()
 if not stat.S_ISSOCK(s.st_mode)or s.st_uid!=os.getuid()or [s.st_dev,s.st_ino]!=config['socket']['identity']:raise Refused('Compositor socket changed')
 return path

def validate(config,value,entry):
 unchanged(config);runtime=directory(config['runtime']);home=directory(config['selectors']['HOME']);private_path(config['_authority']['path'],runtime)
 if not home.is_relative_to(runtime)or not Path(config['_authority']['path']).is_relative_to(home):raise Refused('Selected pin HOME/config authority differs')
 if not sys.flags.isolated or not sys.flags.no_site:raise Refused('Pin helper requires isolated no-site Python')
 if any(os.environ.get(k)for k in FORBIDDEN):raise Refused('Foreign inherited desktop/import handles refused')
 required={'HOME','XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY','DBUS_SESSION_BUS_ADDRESS','WINDOW_PIN_NATIVE_CONFIG'}
 if not required.issubset(config['selectors'])or config['selectors']['XDG_RUNTIME_DIR']!=str(runtime)or config['selectors']['WINDOW_PIN_NATIVE_CONFIG']!=config['_authority']['path']or config['selectors']['DBUS_SESSION_BUS_ADDRESS']!='unix:path='+str(runtime/'bus')or any(os.environ.get(k)!=v for k,v in config['selectors'].items()):raise Refused('Exact selected pin helper environment differs')
 private_path(entry,runtime);regular(entry,0o700)
 if str(Path(entry).resolve())!=config['entry']['path']or digest(entry)!=config['entry']['sha256']:raise Refused('Actual pin helper entry source differs')
 interpreter=config['interpreter'];actual_exe=str(Path('/proc/self/exe').resolve())
 if actual_exe!=interpreter['path']or digest('/proc/self/exe')!=interpreter['sha256']:raise Refused('Actual isolated helper interpreter differs')
 argv=[part.decode()for part in Path('/proc/self/cmdline').read_bytes().rstrip(b'\0').split(b'\0')]
 if argv!=['/usr/bin/python3','-I','-S',str(entry),'toggle',sys.argv[2]]:raise Refused('Actual helper final kernel argv differs')
 own=process(os.getpid());parent=process(own['parent']);roots=[r for r in config['requestRoots']if r['identity']['pid']==parent['pid']]
 if len(roots)!=1 or roots[0]['role']not in ('shell','harness','menu'):raise Refused('Exact captured pin requester required')
 source_process(roots[0]);compositor=source_process(config['compositor'])
 if (Path('/proc/self/cgroup').read_text()!=roots[0]['cgroup']or roots[0]['cgroup']!=config['compositor']['cgroup']):raise Refused('Pin helper/requester/compositor scope differs')
 if value['compositorPid']!=compositor['pid']or value['compositorStart']!=compositor['start']or value['session']!=config['selectors']['HYPRLAND_INSTANCE_SIGNATURE']:raise Refused('Native token compositor differs')
 socket_identity(config);module=config['module'];s=Path(module['path']).stat()
 if Path(module['path']).resolve()!=Path(module['path'])or digest(module['path'])!=module['sha256']or stat.S_IMODE(s.st_mode)!=module['mode']:raise Refused('Selected frozen pin module bytes/mode differ')
 mapped=[]
 for line in (Path('/proc')/str(compositor['pid'])/'maps').read_text().splitlines():
  fields=line.split(None,5)
  if len(fields)==6 and fields[5]==module['path']:mapped.append(fields)
 if not mapped or not any('x'in r[1]for r in mapped)or any(int(r[4])!=s.st_ino for r in mapped):raise Refused('Exact frozen pin module not actually mapped')
 unchanged(config);return {'frontend':own,'requester':parent,'compositor':compositor,'role':roots[0]['role']}

def exchange(config,request,evidence,persist,guard):
 deadline=time.monotonic()+2
 row={'commandBase64':base64.b64encode(request).decode(),'sendStarted':False,'completeServerEOF':False,'rawReplyBase64':'','deadlineMonotonic':deadline};evidence['transport']=row;raw=bytearray()
 def remaining():
  value=deadline-time.monotonic()
  if value<=0:raise TimeoutError('Original absolute two-second pin transaction expired')
  return value
 try:
  persist();remaining();guard();remaining();path=socket_identity(config);remaining()
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)as conn:
   conn.settimeout(remaining());conn.connect(str(path));remaining();pid,uid,gid=struct.unpack('3i',conn.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));row['peer']={'pid':pid,'uid':uid,'gid':gid};persist();remaining()
   if pid!=config['compositor']['identity']['pid']or uid!=os.getuid():raise Refused('Pin actual IPC peer differs')
   guard();remaining();socket_identity(config);remaining();row['sendStarted']=True;persist();conn.settimeout(remaining());conn.sendall(request);remaining()
   while True:
    conn.settimeout(remaining())
    part=conn.recv(4096)
    remaining()
    if not part:row['completeServerEOF']=True;persist();remaining();break
    raw.extend(part);row['rawReplyBase64']=base64.b64encode(raw).decode();row['replyBytes']=len(raw);persist();remaining()
    if len(raw)>65536:raise Refused('Pin result exceeds bounded response')
  socket_identity(config);remaining();guard();remaining();reply=strict_json(raw.decode());remaining();return reply
 except BaseException as error:
  row['error']=repr(error)
  try:persist()
  except BaseException as publication:row['errorPublicationFailure']=repr(publication)
  if row['sendStarted']:raise Uncertain('Pin request may have executed; no automatic retry:'+repr(error))from error
  raise

def result(value,captured):
 if not isinstance(value,dict)or type(value.get('ok'))is not bool or type(value.get('actionsInvoked'))is not bool or type(value.get('possiblePartialOutcome'))is not bool or value.get('phase')not in ('validate','float','pin','raise','complete')or type(value.get('reason'))is not str:raise Uncertain('Malformed native pin receipt; no retry')
 if value['possiblePartialOutcome']!=(not value['ok']and value['actionsInvoked']):raise Uncertain('Inconsistent native partial result; no retry')
 if not value['ok']:
  if value['phase']=='complete'or (value['phase']=='validate'and value['actionsInvoked'])or (value['phase']!='validate'and not value['actionsInvoked']):raise Uncertain('Inconsistent native refusal phase/action; no retry')
  if 'captured'in value:
   try:received=token(value['captured'])
   except Refused as error:raise Uncertain('Malformed native refusal token; no retry')from error
   if received!=captured:raise Uncertain('Native refusal owner token differs; no retry')
 if value['ok']:
  try:received=token(value.get('captured'))
  except Refused as error:raise Uncertain('Malformed native completion token; no retry')from error
  if value['phase']!='complete'or received!=captured or value['actionsInvoked']is not True:raise Uncertain('Native completion token/action differs; no retry')
  for name in ('before','after'):
   row=value.get(name)
   if not isinstance(row,dict)or any(row.get(k)!=captured[k]for k in ('address','stableId','pid','session','incarnation','epoch','generation'))or row.get('live')is not True or row.get('normal')is not True or row.get('fullscreen')is not False:raise Uncertain('Native completed owner projection differs; no retry')
  before=value['before'].get('pinned');desired=value.get('desiredPinned')
  if type(before)is not bool or type(desired)is not bool or desired is before or value['after'].get('floating')is not True or value['after'].get('pinned')is not desired:raise Uncertain('Native completed pin toggle state differs; no retry')
 return value

def publish(fd,evidence):
 raw=(json.dumps(evidence,indent=2,allow_nan=False)+'\n').encode();os.lseek(fd,0,os.SEEK_SET);os.ftruncate(fd,0);offset=0
 while offset<len(raw):
  count=os.write(fd,raw[offset:])
  if count<=0:raise OSError('Evidence full write did not advance')
  offset+=count
 os.fsync(fd)

def main():
 evidence={'nativeCompletionClaimed':False,'automaticRetries':0,'result':'refused'};fd=None
 try:
  if len(sys.argv)!=3 or sys.argv[1]!='toggle'or len(sys.argv[2])>4096:raise Refused('Explicit toggle and complete captured JSON token required')
  captured=token(strict_json(sys.argv[2]));config=read_config(os.environ['WINDOW_PIN_NATIVE_CONFIG']);entry=Path(__file__).resolve();evidence.update(captured=captured,authority=validate(config,captured,entry))
  folder=directory(config['evidenceDirectory']);private_path(folder,Path(config['runtime']));own=evidence['authority']['frontend'];path=folder/(str(own['pid'])+'-'+own['start']+'.json');fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
  directory_fd=os.open(folder,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
  try:os.fsync(directory_fd)
  finally:os.close(directory_fd)
  def persist():publish(fd,evidence)
  persist();reply=exchange(config,command(captured),evidence,persist,lambda:validate(config,captured,entry));evidence['rawNativeResult']=reply;persist();reply=result(reply,captured)
  if time.monotonic()>=evidence['transport']['deadlineMonotonic']:raise Uncertain('Pin completion exceeded original absolute deadline; no retry')
  evidence['result']='complete'if reply['ok']else'native-refused';evidence['nativeCompletionClaimed']=reply['ok'];persist()
  if time.monotonic()>=evidence['transport']['deadlineMonotonic']:raise Uncertain('Pin final publication exceeded original absolute deadline; no retry')
  print(json.dumps(evidence));return 0 if reply['ok']else 2
 except BaseException as error:
  uncertain=isinstance(error,Uncertain)or evidence.get('transport',{}).get('sendStarted',False)
  evidence['nativeCompletionClaimed']=False;evidence['result']='uncertain'if uncertain else'refused';evidence['error']=repr(error)
  if fd is not None:
   try:publish(fd,evidence)
   except BaseException as publication:evidence['errorPublicationFailure']=repr(publication)
  print(json.dumps(evidence),file=sys.stderr);return 3 if uncertain else 1
 finally:
  if fd is not None:os.close(fd)
if __name__=='__main__':raise SystemExit(main())
