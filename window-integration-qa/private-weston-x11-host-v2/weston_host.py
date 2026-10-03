"""Explicit X11 campaign only. No runtime, process or GUI activity on import."""
from pathlib import Path
import hashlib,importlib.util,json,os,re,secrets,socket,struct,time
STAGE=Path(__file__).resolve().parent;QA=STAGE.parent
authspec=importlib.util.spec_from_file_location('_private_x11_authority',STAGE/'x11_authority.py')
auth=importlib.util.module_from_spec(authspec);authspec.loader.exec_module(auth)
spec=importlib.util.spec_from_file_location('_x11_inherited_host_v4',QA/'private-weston-aq-host-v4/weston_host.py')
v4=importlib.util.module_from_spec(spec);spec.loader.exec_module(v4)
original=v4.original

def effective_lua(source):
 if not isinstance(source,bytes) or not source:raise ValueError('nonempty reviewed config required')
 return source+b'\n-- Explicit isolated X11 compatibility campaign only.\nhl.config({ xwayland={enabled=true,create_abstract_socket=false} })\n'

def write_exclusive(path,raw,mode=0o600):
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,mode)
 os.fchmod(fd,mode)  # Keep reviewed availability bits under the harness umask077.
 with os.fdopen(fd,'wb') as out:out.write(raw)

def verify_inputs():
 packet=json.loads((STAGE/'frozen-inputs.json').read_text())
 for path,value in packet['inputs'].items():
  if auth.sha(path)!=value:raise RuntimeError('X11 input changed: '+path)
 for path,target in packet.get('symlinks',{}).items():
  p=Path(path)
  if not p.is_symlink() or str(p.readlink())!=target:raise RuntimeError('X11 loader symlink changed: '+path)
 v4.verify_inputs()

class ReviewedWestonHost(v4.ReviewedWestonHost):
 def verify(self):
  super().verify();verify_inputs()
 def launch(self,name,command,env=None):
  if name=='hyprland':
   if env is None or env.get('PATH')!=str(self.runtime/'bin')+':/usr/bin:/bin' or env.get('WQA_X11_CONFIG')!=str(self.runtime/'hyprland.lua'):raise RuntimeError('private X11 launch contract absent')
  return super().launch(name,command,env)
 def close(self):
  if self.runtime:
   # Caller has already stopped every client and unloaded its plugin. Shut the
   # compositor first; its exact Xwayland child must exit on parent disconnect.
   rows=[(p,r) for p,r in self.processes if r.get('name')=='hyprland']
   record=self.evidence.get('x11',{}).get('server')
   launch=self.runtime/'x11-launch.json'
   if record is None and launch.exists():
    try:
     auth.private_file(launch);candidate=json.loads(launch.read_text())
     if len(rows)==1 and candidate['parent']['pid']==rows[0][1]['pid'] and candidate['parent']['start']==rows[0][1]['start']:
      record=candidate['server'];self.evidence['x11']=candidate
    except Exception as error:self.evidence['x11LateRecordError']=repr(error)
   if record is not None:
    expected={k:record[k] for k in ('pid','start','pgid')}
    self.observed_descendants[(record['pid'],record['start'])]=expected
    for proc,row in rows:
     try:
      self.stop(row,proc);proc.wait(timeout=4)
     except Exception as error:self.evidence['x11CompositorStopError']=repr(error)
    deadline=time.monotonic()+5
    while original.same_process(expected) and time.monotonic()<deadline:time.sleep(.03)
    # No name-based whitelist; surviving registered X server remains an
    # unexpected descendant and the unchanged base performs guarded fallback.
    self.evidence['x11ServerGoneOnCompositorDisconnect']=not original.same_process(expected)
    display=self.evidence.get('x11',{}).get('display')
    if display:
     n=display[1:];self.evidence['x11DisplayArtifactsGone']=all(not Path(p).exists() for p in ('/tmp/.X'+n+'-lock','/tmp/.X11-unix/X'+n,'/tmp/.X11-unix/X'+n+'_'))
   # Secret files are private QA credentials, never archived. Never unlink any
   # foreign or changed file; refusal is retained as a cleanup failure.
   errors=[]
   for name in ('x11-cookie','x11-authority'):
    path=self.runtime/name
    if path.exists():
     try:auth.private_file(path);path.unlink()
     except Exception as error:errors.append(repr(error))
   self.evidence['x11CredentialCleanupErrors']=errors
  super().close()
 def __exit__(self,kind,error,trace):
  result=super().__exit__(kind,error,trace)
  if kind is None and (not self.evidence.get('x11ServerGoneOnCompositorDisconnect') or not self.evidence.get('x11DisplayArtifactsGone') or self.evidence.get('x11CredentialCleanupErrors') or self.evidence.get('x11CompositorStopError')):raise RuntimeError('private X11 cleanup contract failed')
  return result

class PrivateHyprSession(v4.PrivateHyprSession):
 def __init__(self,output,main_env,width,height,nested_lua,dri_prime=None,mesa_vendor=False):
  super().__init__(output,main_env,width,height,nested_lua,dri_prime,mesa_vendor)
  self.host=ReviewedWestonHost(output,main_env,width,height,dri_prime,mesa_vendor);self.evidence=self.host.evidence
 def __enter__(self):
  # This is the reviewed base entry sequence, with only the explicit X11 config,
  # private PATH launcher setup, and post-readiness X11 registration added.
  self.host.__enter__()
  try:
   self.evidence['actualDmabuf']=self.host.probe();runtime=self.host.runtime
   config=runtime/'hyprland.lua';effective=effective_lua(self.lua);write_exclusive(config,effective)
   self.evidence.update(sourceLuaSHA256=hashlib.sha256(self.lua).hexdigest(),xwaylandEnabled=True)
   privatebin=runtime/'bin';privatebin.mkdir(mode=0o700)
   launcher=b'#!/bin/sh\nexec /usr/bin/python3 -I -B '+str(STAGE/'x11_authority.py').encode()+b' "$@"\n'
   write_exclusive(privatebin/'Xwayland',launcher,0o755)
   write_exclusive(runtime/'x11-cookie',secrets.token_bytes(16))
   write_exclusive(runtime/'x11-control.json',json.dumps({'configSHA256':auth.sha(config),'mainDisplay':self.host.main_env.get('DISPLAY'),'launcherSHA256':hashlib.sha256(launcher).hexdigest()}).encode())
   base,parent=original.nested_base(self.host);base.update(PATH=str(privatebin)+':/usr/bin:/bin',WQA_X11_CONFIG=str(config));base.pop('DISPLAY',None);base.pop('XAUTHORITY',None);base.pop('SESSION_MANAGER',None)
   self.evidence['parentSocket']=parent
   self.child=self.host.launch('hyprland',['/usr/bin/Hyprland','--config',str(config)],env=base)
   deadline=time.monotonic()+15;info=None
   while time.monotonic()<deadline:
    if self.child.poll() is not None:raise RuntimeError('private Hyprland exited '+str(self.child.returncode))
    result=original.subprocess.run(['/usr/bin/hyprctl','instances','-j'],env=base,capture_output=True,text=True,timeout=2)
    try:matches=[r for r in json.loads(result.stdout) if r['pid']==self.child.pid]
    except (ValueError,KeyError,TypeError):matches=[]
    if len(matches)>1:raise RuntimeError('ambiguous private instance')
    if matches:info=matches[0];break
    time.sleep(.03)
   if info is None:raise RuntimeError('private instance discovery timeout')
   signature=info['instance'];display=info['wl_socket']
   if not re.fullmatch(r'[A-Za-z0-9_]+',signature) or not re.fullmatch(r'wayland-[0-9]+',display):raise RuntimeError('unsafe private instance/socket name')
   ipc=runtime/'hypr'/signature/'.socket.sock';self.host.wait_socket(str(ipc.relative_to(runtime)),self.child);self.host.wait_socket(display,self.child)
   self.sockets=[original.socket_identity(ipc,runtime),original.socket_identity(runtime/display,runtime)]
   self.child_identity=original.process(self.child.pid);self.env={**base,'HYPRLAND_INSTANCE_SIGNATURE':signature,'WAYLAND_DISPLAY':display};self.env.pop('WESTON_MODULE_MAP',None);self.env.pop('WQA_X11_CONFIG',None)
   self.evidence.update(compositorPID=self.child.pid,compositorStart=self.child_identity['start'],compositorPGID=self.child_identity['pgid'],compositorConfig=str(config),compositorConfigSHA256=auth.sha(config),signature=signature,waylandSocket=display,sockets=self.sockets,hyprlandMaps=original.mapped_files(self.child.pid))
   self.ctl('version');self.register_x11();return self
  except BaseException:
   self.host.close();raise
 def register_x11(self):
  end=time.monotonic()+12;path=self.host.runtime/'x11-launch.json'
  while not path.exists() and time.monotonic()<end:
   self.guard();time.sleep(.03)
  if not path.exists():raise RuntimeError('owned Xwayland launcher registration timed out; no server authority available')
  auth.private_file(path);record=json.loads(path.read_text());server=record['server'];parent=record['parent']
  if parent['pid']!=self.child.pid or parent['start']!=self.child_identity['start'] or server['ppid']!=self.child.pid or server['pgid']!=self.child_identity['pgid']:raise RuntimeError('Xwayland launch parent/start/group mismatch')
  # Wait only for the exact captured launcher PID to exec the unchanged binary.
  end=time.monotonic()+8
  while time.monotonic()<end:
   current=auth.process(server['pid'])
   if current!=server:raise RuntimeError('Xwayland PID identity changed')
   if Path('/proc/'+str(server['pid'])+'/exe').resolve()==Path('/usr/bin/Xwayland'):break
   time.sleep(.03)
  else:raise RuntimeError('Xwayland launcher did not exec unchanged server')
  display=record['display'];authority=self.host.runtime/'x11-authority'
  if auth.private_file(authority)!=record['authority']:raise RuntimeError('Xwayland authority inode replaced')
  args=auth.argv(server['pid']);expected=['/usr/bin/Xwayland',*record['upstreamArgs'],'-auth',str(authority)]
  if args!=expected or display==self.host.main_env.get('DISPLAY'):raise RuntimeError('Xwayland actual argv/display mismatch')
  env=auth.environment(server['pid'])
  if env.get('XDG_RUNTIME_DIR')!=str(self.host.runtime) or env.get('DISPLAY')!=display or env.get('XAUTHORITY')!=str(authority):raise RuntimeError('Xwayland exec environment mismatch')
  lock=Path('/tmp/.X'+display[1:]+'-lock');s=lock.lstat()
  if s.st_uid!=os.getuid() or not original.stat.S_ISREG(s.st_mode) or lock.read_text()!=f'{self.child.pid:010d}\n':raise RuntimeError('X display lock not owned by private compositor')
  endpoints=[]
  for suffix in ('','_'):
   p=Path('/tmp/.X11-unix/X'+display[1:]+suffix);identity=auth.socket_identity(p);inode=auth.socket_kernel_inode(p)
   if not auth.has_fd(self.child.pid,inode) or not auth.has_fd(server['pid'],inode):raise RuntimeError('X listener not shared by captured compositor and server')
   endpoints.append({'socket':identity,'kernelInode':inode})
  self.x11_identity=server;self.x11_sockets=endpoints;self.x11_auth_identity=auth.private_file(authority);self.x11_authority_sha=auth.sha(authority)
  limits=Path('/proc/'+str(server['pid'])+'/limits').read_text()
  core=[line.split() for line in limits.splitlines() if line.startswith('Max core file size')]
  if len(core)!=1 or core[0][-3:-1]!=['1','1']:raise RuntimeError('actual Xwayland core1 inheritance missing')
  self.evidence['x11']={**record,'actualArgv':args,'actualCoreLimits':[1,1],'executableSHA256':auth.sha('/usr/bin/Xwayland'),'listenerAuthority':endpoints,'lock':{'path':str(lock),'device':s.st_dev,'inode':s.st_ino,'ownerPID':self.child.pid},'authority':self.x11_auth_identity}
  self.env.update(DISPLAY=display,XAUTHORITY=str(authority))
  # Both requests are read-only protocol setup, on the exact verified endpoint.
  cookie_display,cookie=auth.decode_authority(authority.read_bytes())
  if cookie_display!=display:raise RuntimeError('Xauthority display mismatch')
  replies=[]
  for label,credential in (('unauthenticated',None),('authenticated',cookie)):
   self.guard();p=endpoints[0]['socket']['path']
   with socket.socket(socket.AF_UNIX) as endpoint:
    endpoint.settimeout(3);endpoint.connect(p)
    pid,uid,gid=struct.unpack('3i',endpoint.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
    if pid!=self.child.pid or uid!=os.getuid():raise RuntimeError('X listener peer is not captured compositor creator')
    endpoint.sendall(auth.setup_request(credential));reply=auth.setup_reply(endpoint)
   if auth.socket_identity(p)!=endpoints[0]['socket']:raise RuntimeError('X listener replaced during setup')
   replies.append({'kind':label,'peerCreator':{'pid':pid,'uid':uid,'gid':gid},**reply})
   if (label=='unauthenticated' and reply['status']!=0) or (label=='authenticated' and (reply['status']!=1 or reply['major']!=11)):raise RuntimeError('Actual X11 authentication acceptance/refusal contract failed')
  self.evidence['x11']['readOnlySetup']=replies
 def guard(self):
  super().guard()
  if hasattr(self,'x11_identity'):
   if auth.process(self.x11_identity['pid'])!=self.x11_identity:raise RuntimeError('private Xwayland identity changed')
   if auth.private_file(self.env['XAUTHORITY'])!=self.x11_auth_identity or auth.sha(self.env['XAUTHORITY'])!=self.x11_authority_sha or self.env.get('DISPLAY')!=self.evidence['x11']['display']:raise RuntimeError('private X11 routing changed')
   for row in self.x11_sockets:
    if auth.socket_identity(row['socket']['path'])!=row['socket'] or auth.socket_kernel_inode(row['socket']['path'])!=row['kernelInode']:raise RuntimeError('private X listener changed')
