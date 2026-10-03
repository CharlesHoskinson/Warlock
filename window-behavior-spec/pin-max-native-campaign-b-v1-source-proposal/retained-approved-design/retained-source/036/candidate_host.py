"""Proposed exact candidate child selectors. No side effects before context entry."""
from pathlib import Path
import hashlib,importlib.util,json,os,re,socket,struct,subprocess,time
QA=Path('/home/hoskinson/window-integration-qa')
CANDIDATE=Path('/home/hoskinson/window-behavior-spec/pin-maximized-core-v3-hit-fallback')
CORE=CANDIDATE/'build-core-make/Hyprland'
B=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('_pin_v3_exact_bootstrap_host',QA/'private-weston-aq-bootstrap-host-v5/weston_host.py')
accepted=importlib.util.module_from_spec(spec);spec.loader.exec_module(accepted)
original=accepted.original;AQ=accepted.AQ
from host_observation import ObservedShutdownMixin
verify_inputs=accepted.verify_inputs
effective_lua=original.effective_lua;nested_base=original.nested_base
socket_identity=original.socket_identity;process=original.process;mapped_files=original.mapped_files
digest=original.digest

def verify_pair():
    import pair_binding
    return pair_binding.read_pair(B/'PAIR_READY.json')

class ReviewedWestonHost(ObservedShutdownMixin,accepted.ReviewedWestonHost):
    _original_module=original
    def launch(self,name,command,env=None):
        if name=='hyprland':
            verify_inputs(); verify_pair()
            if not command or str(command[0])!=str(CORE) or env is None or env.get('AQ_BACKENDS')!='wayland':
                raise RuntimeError('Private library selection requires explicit reviewed child command/env')
            selected=dict(env)
            selected['LD_LIBRARY_PATH']=str(AQ/'prefix/lib')+':'+selected.get('LD_LIBRARY_PATH','')
            self.evidence['privateAquamarine']['childLibraryPath']=selected['LD_LIBRARY_PATH']
            return original.PrivateWestonHost.launch(self,name,command,selected)
        return super().launch(name,command,env)

    def wait_socket(self,name,proc):
        # Leave the parent/Wayland readiness protocol unchanged. Never guess an IPC target.
        parts=Path(name).parts
        if not parts or parts[-1]!='.socket.sock':
            return super().wait_socket(name,proc)
        original.qa.require_qa_scope()
        runtime=original.qa.verify_runtime(self.runtime)
        if len(parts)!=3 or parts[0]!='hypr' or not re.fullmatch(r'[A-Za-z0-9_]+',parts[1]) or Path(name).is_absolute():
            raise RuntimeError('Invalid private IPC readiness path')
        records=[row for owned,row in self.processes if owned is proc and row.get('name')=='hyprland' and row.get('command',[None])[0]==str(CORE)]
        if len(records)!=1:
            raise RuntimeError('IPC readiness requires exact registered child')
        expected=records[0]
        def live():
            if proc.poll() is not None or not original.same_process(expected):
                raise RuntimeError('Private IPC child exited or changed identity')
        live()
        path=runtime/name
        deadline=time.monotonic()+12
        while True:
            live()
            if time.monotonic()>=deadline:raise RuntimeError('Private IPC readiness timed out')
            try:
                before=original.socket_identity(path,runtime)
                # Every intermediate path must remain inside the owned runtime without symlinks.
                if any(part.is_symlink() for part in (path.parent,path.parent.parent)):
                    raise RuntimeError('Private IPC path contains symlink')
                connection=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
                connection.settimeout(min(2,max(.001,deadline-time.monotonic())))
                try:connection.connect(str(path))
                except (ConnectionRefusedError,FileNotFoundError):
                    connection.close();time.sleep(.03);continue
                except BaseException:
                    connection.close();raise
            except FileNotFoundError:
                time.sleep(.03);continue
            # Once connected, a bad peer/protocol response is terminal; never retry it.
            with connection:
                pid,uid,gid=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,struct.calcsize('3i')))
                if pid!=expected['pid'] or uid!=os.getuid():raise RuntimeError('Private IPC peer identity mismatch')
                if original.socket_identity(path,runtime)!=before:raise RuntimeError('Private IPC socket replaced')
                live();connection.sendall(b'j/version')
                reply=bytearray()
                while True:
                    connection.settimeout(min(2,max(.001,deadline-time.monotonic())))
                    chunk=connection.recv(4096)
                    if not chunk:break
                    reply.extend(chunk)
                    if len(reply)>65536:raise RuntimeError('Private IPC version reply too large')
                    if time.monotonic()>=deadline:raise RuntimeError('Private IPC reply timed out')
                version=json.loads(reply.decode('utf-8'))
                if not isinstance(version,dict) or not version:raise RuntimeError('Private IPC version reply must be a nonempty JSON object')
                live()
                if original.socket_identity(path,runtime)!=before:raise RuntimeError('Private IPC socket replaced after reply')
                self.evidence.setdefault('ipcReadiness',[]).append({'path':str(path),'socket':before,'peer':{'pid':pid,'uid':uid,'gid':gid},'request':'j/version','replyBytes':len(reply),'replySHA256':hashlib.sha256(reply).hexdigest(),'completeServerEOF':True,'version':version})
                return

class PrivateHyprSession(accepted.PrivateHyprSession):
    def __init__(self,output,main_env,width,height,nested_lua,dri_prime=None,mesa_vendor=False):
        super().__init__(output,main_env,width,height,nested_lua,dri_prime,mesa_vendor)
        self.host=ReviewedWestonHost(output,main_env,width,height,dri_prime,mesa_vendor)
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
      self.child=self.host.launch('hyprland',[str(CORE),'--config',str(config)],env=base)
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

