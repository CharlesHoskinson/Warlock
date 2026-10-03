"""Import-safe private host. Launch only after root reviews/grants the native slot."""
from pathlib import Path
import hashlib,importlib.util,json,os,re,shutil,signal,socket,stat,subprocess,time
STAGE=Path(__file__).resolve().parent
PREFIX=STAGE/'prefix'
QA_ROOT=STAGE.parent
_spec=importlib.util.spec_from_file_location('_private_weston_qa_launch',QA_ROOT/'qa_launch.py')
qa=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(qa)
DROP=('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','HYPRLAND_INSTANCE_SIGNATURE','DBUS_SESSION_BUS_ADDRESS','DBUS_SESSION_BUS_PID','DBUS_STARTER_ADDRESS','DBUS_STARTER_BUS_TYPE','AT_SPI_BUS_ADDRESS','XAUTHORITY','XDG_ACTIVATION_TOKEN','DESKTOP_STARTUP_ID','LD_LIBRARY_PATH','LD_PRELOAD','LD_AUDIT','PYTHONPATH','PYTHONHOME','AQ_DRM_DEVICES','AQ_BACKENDS','LIBGL_ALWAYS_SOFTWARE','GALLIUM_DRIVER','MESA_LOADER_DRIVER_OVERRIDE','DRI_PRIME','__EGL_VENDOR_LIBRARY_FILENAMES','EGL_PLATFORM','MESA_SHADER_CACHE_DIR','MESA_GL_VERSION_OVERRIDE','MESA_GLSL_VERSION_OVERRIDE','MESA_EXTENSION_OVERRIDE','QT_QUICK_BACKEND','QSG_RHI_BACKEND','QT_OPENGL')
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def mapped_files(pid):
 raw=Path('/proc/'+str(pid)+'/maps').read_text();files={}
 for line in raw.splitlines():
  parts=line.split(maxsplit=5)
  if len(parts)!=6 or not parts[5].startswith('/') or parts[5].endswith(' (deleted)'):continue
  path=Path(parts[5])
  if path.is_file():files[str(path)]=digest(path)
 return dict(maps=raw,files=files)
def process(pid):
 p=Path('/proc')/str(pid)
 if p.stat().st_uid!=os.getuid():raise RuntimeError('foreign UID')
 raw=(p/'stat').read_text();parts=raw[raw.rfind(')')+2:].split()
 return dict(pid=pid,start=parts[19],pgid=int(parts[2]))
def same_process(row):
 try:return process(row['pid'])=={k:row[k] for k in ('pid','start','pgid')}
 except OSError:return False
def private_env(main,runtime,dri_prime=None,mesa_vendor=False):
 runtime=qa.verify_runtime(runtime)
 env={k:v for k,v in main.items() if k not in DROP}
 for key,name in [('HOME','home'),('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_STATE_HOME','state')]:
  folder=runtime/name;folder.mkdir(mode=0o700,exist_ok=True);env[key]=str(folder)
 env.update(XDG_RUNTIME_DIR=str(runtime),DBUS_SESSION_BUS_ADDRESS='unix:path='+str(runtime/'bus'),WAYLAND_DISPLAY='weston-host',XDG_SESSION_TYPE='wayland',GDK_BACKEND='wayland',QT_QPA_PLATFORM='wayland',EGL_PLATFORM='surfaceless',AQ_BACKENDS='wayland')
 env['LD_LIBRARY_PATH']=str(PREFIX/'usr/lib')+':'+str(PREFIX/'usr/lib/weston')
 modules={name:str(path) for name,path in [('headless-backend.so',PREFIX/'usr/lib/libweston-15/headless-backend.so'),('gl-renderer.so',PREFIX/'usr/lib/libweston-15/gl-renderer.so'),('kiosk-shell.so',PREFIX/'usr/lib/weston/kiosk-shell.so')]}
 env['WESTON_MODULE_MAP']=';'.join(name+'='+path for name,path in modules.items())
 if dri_prime is not None:
  assert re.fullmatch(r'(?:[0-9]+|pci-[0-9a-f]{4}_[0-9a-f]{2}_[0-9a-f]{2}_[0-7])',dri_prime)
  env['DRI_PRIME']=dri_prime
 if mesa_vendor:env['__EGL_VENDOR_LIBRARY_FILENAMES']='/usr/share/glvnd/egl_vendor.d/50_mesa.json'
 return env

def archive_runtime(runtime,output):
 archive=Path(output)/'runtime-archive';archive.mkdir(mode=0o700,exist_ok=True);rows=[]
 for source in sorted(Path(runtime).rglob('*')):
  if source.is_symlink() or not source.is_file() or source.stat().st_uid!=os.getuid():continue
  if source.suffix not in ('.log','.json','.lua','.debug','.ini','.txt') and 'log' not in source.name:continue
  target=archive/source.relative_to(runtime);target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
  descriptor=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(descriptor,'wb') as stream:stream.write(source.read_bytes())
  rows.append(dict(source=str(source),archive=str(target),sha256=digest(target)))
 return rows

class PrivateWestonHost:
 def __init__(self,output,main_env,width=1600,height=1000,dri_prime=None,mesa_vendor=False):
  self.output=Path(output).resolve();self.main_env=dict(main_env);self.width=width;self.height=height;self.dri_prime=dri_prime;self.mesa_vendor=mesa_vendor
  assert 320<=width<=4096 and 240<=height<=4096
  self.runtime=None;self.processes=[];self.logs=[];self.observed_descendants={};self.evidence=dict(nativeHostAccepted=False,mainDisplayUsed=False,width=width,height=height,hostScale=1)
 def verify(self):
  manifest=STAGE/'host-stage-report.json';row=json.loads(manifest.read_text())
  for name,value in row['files'].items():assert digest(STAGE/name)==value,name
  for name,value in row['externalDependencies'].items():assert digest(name)==value,name
  for name,value in row['symlinks'].items():assert (STAGE/name).is_symlink() and os.readlink(STAGE/name)==value,name
  self.evidence['manifestSHA256']=digest(manifest)
 def launch(self,name,command,env=None):
  path=self.output/(name+'.log');descriptor=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);log=os.fdopen(descriptor,'wb');self.logs.append(log)
  proc=subprocess.Popen(list(map(str,command)),env=self.env if env is None else env,cwd=self.runtime,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  row=process(proc.pid);assert row['pgid']==proc.pid
  row.update(name=name,command=list(map(str,command)),log=str(path));self.processes.append((proc,row));self.evidence[name]=row;return proc
 def wait_socket(self,name,proc):
  end=time.monotonic()+12
  while time.monotonic()<end:
   if proc.poll() is not None:raise RuntimeError(name+' process exited '+str(proc.returncode))
   path=self.runtime/name
   try:
    st=path.stat();assert stat.S_ISSOCK(st.st_mode) and st.st_uid==os.getuid()
    connection=socket.socket(socket.AF_UNIX);connection.settimeout(.2)
    try:connection.connect(str(path));return
    finally:connection.close()
   except (OSError,AssertionError):time.sleep(.03)
  raise RuntimeError('private socket timed out '+name)
 def __enter__(self):
  self.evidence['qaScope']=qa.require_qa_scope()
  self.verify();assert str(self.output).startswith(str(Path.home()/'window-integration-qa')+'/')
  self.evidence['accessibleRenderNodes']=qa.verify_device_access()
  self.output.mkdir(mode=0o700);self.runtime=qa.private_runtime()
  try:
   self.env=private_env(self.main_env,self.runtime,self.dri_prime,self.mesa_vendor)
   self.evidence.update(runtime=str(self.runtime),driPrime=self.dri_prime,mesaVendorSelected=self.mesa_vendor,privateEnv={k:self.env[k] for k in ('HOME','XDG_RUNTIME_DIR','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME','DBUS_SESSION_BUS_ADDRESS','WAYLAND_DISPLAY','LD_LIBRARY_PATH','WESTON_MODULE_MAP')})
   bus=self.launch('privateBus',['/usr/bin/dbus-daemon','--session','--nofork','--address='+self.env['DBUS_SESSION_BUS_ADDRESS']]);self.wait_socket('bus',bus)
   command=[PREFIX/'usr/bin/weston','--backend=headless','--renderer=gl','--shell=kiosk-shell.so','--fake-seat','--no-config','--socket=weston-host','--width='+str(self.width),'--height='+str(self.height),'--scale=1','--idle-time=0','--log='+str(self.output/'weston-renderer.log')]
   host=self.launch('weston',command);self.wait_socket('weston-host',host)
   self.evidence['westonMaps']=mapped_files(host.pid)
   return self
  except BaseException:
   self.close();raise
 def probe(self):
  result=subprocess.run([str(STAGE/'probe/dmabuf_probe')],env=self.env,cwd=self.runtime,capture_output=True,text=True,timeout=12)
  (self.output/'dmabuf-probe.stdout').write_text(result.stdout);(self.output/'dmabuf-probe.stderr').write_text(result.stderr)
  (self.output/'dmabuf-probe.stdout').chmod(0o600);(self.output/'dmabuf-probe.stderr').chmod(0o600)
  self.evidence['dmabufProbe']=dict(exitCode=result.returncode,stdout=result.stdout,stderr=result.stderr)
  if result.returncode:raise RuntimeError('actual private DMA-BUF capability failed')
  return json.loads(result.stdout)
 def descendants(self):
  rows={};parents={};tokens=set();token=('XDG_RUNTIME_DIR='+str(self.runtime)).encode()
  active=[row for _,row in self.processes if same_process(row)]+[row for row in self.observed_descendants.values() if same_process(row)]
  groups={row['pgid'] for row in active};owned={row['pid'] for row in active}
  for path in Path('/proc').glob('[0-9]*'):
   try:
    if path.stat().st_uid!=os.getuid():continue
    pid=int(path.name);row=process(pid);raw=(path/'stat').read_text();parts=raw[raw.rfind(')')+2:].split();parents[pid]=int(parts[1]);rows[pid]=row
    if token in (path/'environ').read_bytes().split(b'\0') or row['pgid'] in groups:tokens.add(pid)
   except (OSError,IndexError):pass
  known=owned|tokens
  for _ in range(len(rows)+1):
   added={pid for pid,parent in parents.items() if parent in known}-known
   if not added:break
   known.update(added)
  result=[rows[pid] for pid in sorted(known) if pid in rows]
  for row in result:self.observed_descendants[(row['pid'],row['start'])]=row
  return result
 def stop(self,row,proc=None):
  if proc is not None and proc.poll() is not None:return
  if not same_process(row):return
  os.kill(row['pid'],signal.SIGTERM);end=time.monotonic()+4
  while same_process(row) and time.monotonic()<end:
   if proc is not None and proc.poll() is not None:return
   time.sleep(.03)
  if same_process(row):os.kill(row['pid'],signal.SIGKILL)
 def close(self):
  if not self.runtime:return
  errors=[]
  own={row['pid'] for _,row in self.processes};unexpected=[r for r in self.descendants() if r['pid'] not in own]
  self.evidence['unexpectedInnerDescendants']=unexpected
  for row in reversed(unexpected):
   try:self.stop(row)
   except OSError as error:errors.append(repr(error))
  for proc,row in reversed(self.processes):
   try:self.stop(row,proc);proc.wait(timeout=4)
   except (OSError,subprocess.TimeoutExpired) as error:errors.append(repr(error))
  try:self.evidence['archivedRuntime']=archive_runtime(self.runtime,self.output)
  except OSError as error:errors.append('archive: '+repr(error))
  self.evidence['remainingDescendants']=self.descendants()
  self.evidence['observedDescendantIdentities']=list(self.observed_descendants.values())
  for log in self.logs:log.close()
  for path in self.output.glob('*.log'):path.chmod(0o600)
  if not self.evidence['remainingDescendants'] and not errors:shutil.rmtree(self.runtime)
  self.evidence['cleanupErrors']=errors
  self.evidence['runtimeGone']=not self.runtime.exists()
  destination=self.output/'host-evidence.json';destination.write_text(json.dumps(self.evidence,indent=2)+'\n');destination.chmod(0o600)
  self.runtime=None
 def __exit__(self,kind,error,trace):
  self.close()
  if kind is None and (self.evidence['cleanupErrors'] or self.evidence['unexpectedInnerDescendants'] or self.evidence['remainingDescendants'] or not self.evidence['runtimeGone']):raise RuntimeError('private host cleanup invariant failed')
  return False

def socket_identity(path,runtime):
 path=Path(path);runtime=Path(runtime).resolve()
 if path.is_symlink() or not path.resolve().is_relative_to(runtime):raise RuntimeError('foreign socket path')
 row=path.stat()
 if row.st_uid!=os.getuid() or not stat.S_ISSOCK(row.st_mode):raise RuntimeError('foreign socket owner/type')
 return dict(path=str(path),uid=row.st_uid,device=row.st_dev,inode=row.st_ino)

def effective_lua(source):
 return source+b'\n-- Crash handoff: X11 is outside this private fixture.\nhl.config({ xwayland = { enabled = false } })\n'

def nested_base(host):
 base,parent=qa.nested_env(host.env,host.runtime);base.pop('EGL_PLATFORM',None)
 if parent['pid']!=host.evidence['weston']['pid'] or not same_process(host.evidence['weston']):raise RuntimeError('private Weston parent identity changed')
 return base,parent

class PrivateHyprSession:
 """No side effects until context entry. Caller owns normal fixture shutdown."""
 def __init__(self,output,main_env,width,height,nested_lua,dri_prime=None,mesa_vendor=False):
  if not isinstance(nested_lua,bytes) or not nested_lua:raise ValueError('reviewed Lua must be nonempty bytes')
  self.lua=nested_lua
  self.host=PrivateWestonHost(output,main_env,width,height,dri_prime,mesa_vendor)
  self.evidence=self.host.evidence
 def __enter__(self):
  self.host.__enter__()
  try:
   self.evidence['actualDmabuf']=self.host.probe()
   config=self.host.runtime/'hyprland.lua'
   fd=os.open(config,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
   effective=effective_lua(self.lua)
   with os.fdopen(fd,'wb') as out:out.write(effective)
   self.evidence['sourceLuaSHA256']=hashlib.sha256(self.lua).hexdigest();self.evidence['xwaylandEnabled']=False
   base,parent=nested_base(self.host)
   self.evidence['parentSocket']=parent
   self.child=self.host.launch('hyprland',['/usr/bin/Hyprland','--config',str(config)],env=base)
   deadline=time.monotonic()+15;info=None
   while time.monotonic()<deadline:
    if self.child.poll() is not None:raise RuntimeError('private Hyprland exited '+str(self.child.returncode))
    result=subprocess.run(['/usr/bin/hyprctl','instances','-j'],env=base,capture_output=True,text=True,timeout=2)
    try:matches=[r for r in json.loads(result.stdout) if r['pid']==self.child.pid]
    except (ValueError,KeyError,TypeError):matches=[]
    if len(matches)>1:raise RuntimeError('ambiguous private instance')
    if matches:info=matches[0];break
    time.sleep(.03)
   if info is None:raise RuntimeError('private instance discovery timeout')
   signature=info['instance'];display=info['wl_socket']
   if not re.fullmatch(r'[A-Za-z0-9_]+',signature) or not re.fullmatch(r'wayland-[0-9]+',display):raise RuntimeError('unsafe private instance/socket name')
   ipc=self.host.runtime/'hypr'/signature/'.socket.sock'
   self.host.wait_socket(str(ipc.relative_to(self.host.runtime)),self.child)
   self.host.wait_socket(display,self.child)
   self.sockets=[socket_identity(ipc,self.host.runtime),socket_identity(self.host.runtime/display,self.host.runtime)]
   self.child_identity=process(self.child.pid)
   self.env={**base,'HYPRLAND_INSTANCE_SIGNATURE':signature,'WAYLAND_DISPLAY':display}
   self.env.pop('WESTON_MODULE_MAP',None)
   self.evidence.update(compositorPID=self.child.pid,compositorStart=self.child_identity['start'],compositorPGID=self.child_identity['pgid'],compositorConfig=str(config),compositorConfigSHA256=digest(config),signature=signature,waylandSocket=display,sockets=self.sockets,hyprlandMaps=mapped_files(self.child.pid))
   self.ctl('version')
   return self
  except BaseException:
   self.host.close();raise
 def guard(self):
  if not same_process(self.child_identity):raise RuntimeError('private compositor identity changed')
  for expected in self.sockets:
   if socket_identity(expected['path'],self.host.runtime)!=expected:raise RuntimeError('private compositor socket replaced')
  if self.env.get('HYPRLAND_INSTANCE_SIGNATURE')!=self.evidence['signature'] or self.env.get('WAYLAND_DISPLAY')!=self.evidence['waylandSocket']:raise RuntimeError('private routing changed')
  if self.env.get('XDG_RUNTIME_DIR')!=str(self.host.runtime) or self.env.get('DBUS_SESSION_BUS_ADDRESS')!='unix:path='+str(self.host.runtime/'bus'):raise RuntimeError('private runtime/bus routing changed')
 def ctl(self,*args):
  self.guard()
  result=subprocess.run(['/usr/bin/hyprctl','-i',self.evidence['signature'],*map(str,args)],env=self.env,capture_output=True,text=True,timeout=5)
  if result.returncode:raise RuntimeError('private IPC failed: '+result.stderr+result.stdout)
  return result.stdout
 def data(self,*args):return json.loads(self.ctl('-j',*args))
 def __exit__(self,kind,error,trace):return self.host.__exit__(kind,error,trace)
