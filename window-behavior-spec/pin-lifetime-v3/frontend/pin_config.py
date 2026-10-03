"""Private candidate materialization; never launches GUI or sends IPC.

Call install() before requester exec and write() only after exact requester,
compositor, private socket and mapped candidate registration. No main paths.
"""
from pathlib import Path
import hashlib,json,os,shutil,stat
B=Path(__file__).resolve().parent
ROOT_HELPER_SHA='30cf295bbc3032b10996e9b6db7c602f6044d38cf73d4eb6ef917e72dd80f0f2'
FORBIDDEN=('DISPLAY','AT_SPI_BUS_ADDRESS','WAYLAND_SOCKET','SESSION_MANAGER','LD_PRELOAD','LD_AUDIT','PYTHONPATH','PYTHONHOME','DBUS_STARTER_ADDRESS','DBUS_STARTER_BUS_TYPE')
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def directory(p):
 p=Path(p);s=p.lstat()
 if not p.is_absolute()or p.resolve()!=p or not stat.S_ISDIR(s.st_mode)or stat.S_IMODE(s.st_mode)!=0o700 or s.st_uid!=os.getuid():raise ValueError('Exact private canonical0700 directory required')
 return p

def under(p,runtime):
 p=Path(p)
 if not p.is_absolute()or not p.is_relative_to(runtime)or p.resolve()!=p:raise ValueError('Private canonical path required')
 for parent in p.parents:
  if parent==runtime:break
  if parent.is_relative_to(runtime):directory(parent)
 return p

def write_bytes(path,raw,mode):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,mode)
 try:
  view=memoryview(raw)
  while view:
   count=os.write(fd,view)
   if count<=0:raise OSError('Materialization full write failed')
   view=view[count:]
  os.fsync(fd)
 finally:os.close(fd)
 fd=os.open(Path(path).parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:os.fsync(fd)
 finally:os.close(fd)

def install(home,runtime):
 runtime=directory(runtime);home=directory(home);under(home,runtime)
 if digest(B/'pin_helper.py')!=ROOT_HELPER_SHA:raise ValueError('Exact reviewed root helper bytes changed')
 local=home/'.local';local.mkdir(mode=0o700,exist_ok=True);directory(local)
 bin_dir=local/'bin';bin_dir.mkdir(mode=0o700,exist_ok=True);directory(bin_dir)
 entries={}
 for name,source in [('hypr-pin-toggle',B/'pin_helper.py'),('hypr-pin-capture',B/'pin_capture.py')]:
  destination=under(bin_dir/name,runtime)
  if destination.exists()or destination.is_symlink():raise ValueError('Fresh entry only; no prior helper replacement')
  write_bytes(destination,source.read_bytes(),0o700)
  if digest(destination)!=digest(source):raise ValueError('Copied product entry differs')
  entries[name]={'path':str(destination),'sha256':digest(destination)}
 folder=home/'pin-evidence';folder.mkdir(mode=0o700);directory(folder)
 config=home/'pin-config.json'
 if config.exists()or config.is_symlink():raise ValueError('Fresh configuration only')
 return dict(entry=entries['hypr-pin-toggle'],captureEntry=entries['hypr-pin-capture'],evidenceDirectory=str(folder),path=str(config))

def source_process(pid,environment,role=None):
 if type(pid)is not int or pid<=0 or not environment:raise ValueError('Exact process and selected initial environment required')
 p=Path('/proc')/str(pid)
 def identity():
  s=(p/'stat').read_text().rsplit(')',1)[1].split();status={k:v.strip()for k,v in (line.split(':',1)for line in(p/'status').read_text().splitlines()if ':'in line)}
  if p.stat().st_uid!=os.getuid()or status.get('Uid','').split()!=[str(os.getuid())]*4:raise ValueError('Process UID differs')
  return dict(pid=pid,start=s[19],parent=int(s[1]),pgid=int(s[2]))
 before=identity();actual=dict(x.split(b'=',1)for x in(p/'environ').read_bytes().split(b'\0')if b'='in x)
 if any(actual.get(k.encode())!=(v.encode()if v is not None else None)for k,v in environment.items()):raise ValueError('Selected actual process environment differs')
 row=dict(identity=before,argv=[part.decode()for part in(p/'cmdline').read_bytes().rstrip(b'\0').split(b'\0')],executable=str((p/'exe').resolve()),executableSHA256=digest(p/'exe'),cgroup=(p/'cgroup').read_text(),environment=dict(environment))
 if identity()!=before:raise ValueError('Process lifetime changed during registration')
 if role is not None:
  if role not in ('shell','harness','menu'):raise ValueError('Explicit requester role required')
  row['role']=role
 return row

def write(materialized,runtime,selectors,request_roots,compositor,module):
 runtime=directory(runtime);home=directory(selectors['HOME']);under(home,runtime)
 required={'HOME','XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY','DBUS_SESSION_BUS_ADDRESS','WINDOW_PIN_NATIVE_CONFIG'}
 if not required.issubset(selectors)or selectors['XDG_RUNTIME_DIR']!=str(runtime)or selectors['WINDOW_PIN_NATIVE_CONFIG']!=materialized['path']or selectors['DBUS_SESSION_BUS_ADDRESS']!='unix:path='+str(runtime/'bus')or any(type(v)is not str for v in selectors.values()):raise ValueError('Preselected exact private selectors required')
 if not request_roots or len({r['identity']['pid']for r in request_roots})!=len(request_roots)or any(r.get('role')not in ('shell','harness','menu')or r['cgroup']!=compositor['cgroup']for r in request_roots):raise ValueError('Exact unique requester/compositor scope roots required')
 for row in [compositor,*request_roots]:
  if source_process(row['identity']['pid'],row['environment'],row.get('role'))!=row:raise ValueError('Final registered process/source lifetime changed')
 socket=under(runtime/'hypr'/selectors['HYPRLAND_INSTANCE_SIGNATURE']/'.socket.sock',runtime);info=socket.lstat()
 if not stat.S_ISSOCK(info.st_mode)or info.st_uid!=os.getuid():raise ValueError('Owned compositor socket required')
 p=Path(module['path']);s=p.lstat()
 if not p.is_absolute()or p.resolve()!=p or not stat.S_ISREG(s.st_mode)or digest(p)!=module['sha256']or stat.S_IMODE(s.st_mode)!=module['mode']:raise ValueError('Frozen native module source authority differs')
 maps=(Path('/proc')/str(compositor['identity']['pid'])/'maps').read_text().splitlines();rows=[line.split(None,5)for line in maps if len(line.split(None,5))==6 and line.split(None,5)[5]==str(p)]
 if not rows or not any('x'in row[1]for row in rows)or any(int(row[4])!=s.st_ino for row in rows):raise ValueError('Selected module not actually mapped by exact compositor')
 for name in ('entry','captureEntry'):
  p=under(materialized[name]['path'],runtime);s=p.lstat()
  if not stat.S_ISREG(s.st_mode)or stat.S_IMODE(s.st_mode)!=0o700 or s.st_uid!=os.getuid()or s.st_nlink!=1 or digest(p)!=materialized[name]['sha256']:raise ValueError('Fresh installed product entry differs')
 config=dict(version=1,runtime=str(runtime),selectors=dict(selectors),entry=materialized['entry'],captureEntry=materialized['captureEntry'],interpreter=dict(path=str(Path('/usr/bin/python3').resolve()),sha256=digest('/usr/bin/python3')),requestRoots=request_roots,compositor=compositor,socket=dict(path=str(socket),identity=[info.st_dev,info.st_ino]),module=module,evidenceDirectory=materialized['evidenceDirectory'])
 write_bytes(under(materialized['path'],runtime),(json.dumps(config,indent=2,allow_nan=False)+'\n').encode(),0o600)
 return config
