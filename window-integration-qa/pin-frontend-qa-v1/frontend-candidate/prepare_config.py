"""Fresh private frontend setup for reviewed native harnesses. Import is inert.

Caller supplies exact owned process identities and expected final argv; the
builder cannot infer a compositor, request root, service or active window.
"""
from pathlib import Path
import hashlib,json,os,stat
import native_frontend as frontend
B=Path(__file__).resolve().parent
SERVICE=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-responsive-v13')
PARENT_ENV_KEYS=('HOME','XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY','DISPLAY','DBUS_SESSION_BUS_ADDRESS','DBUS_SYSTEM_BUS_ADDRESS','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME','WINDOW_MOTION_NATIVE_CONFIG')
SELECTOR_KEYS=('HOME','XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY','DBUS_SESSION_BUS_ADDRESS','DBUS_SYSTEM_BUS_ADDRESS','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME','WINDOW_MOTION_NATIVE_CONFIG')
def capture_request_root(role,identity,expected_argv):
 if role not in ('shell','harness'):raise frontend.Refused('Exact configured requester role required')
 frontend.live(identity);p=Path('/proc')/str(identity['pid'])
 argv=[v.decode() for v in (p/'cmdline').read_bytes().rstrip(b'\0').split(b'\0')]
 if argv!=list(map(str,expected_argv)):raise frontend.Refused('Captured requester argv differs from explicit final invocation')
 executable=(p/'exe').resolve();values=dict(part.split(b'=',1) for part in (p/'environ').read_bytes().split(b'\0') if b'=' in part)
 row={'role':role,'identity':dict(identity),'argv':argv,'executable':str(executable),'executableSHA256':frontend.digest(p/'exe'),'cgroup':(p/'cgroup').read_text(),'environment':{k:values[k.encode()].decode() if k.encode() in values else None for k in PARENT_ENV_KEYS}}
 frontend.live(identity);return row

def install_entry(env,source_sha,expected_legacy_sha):
 runtime=frontend.private_directory(env['XDG_RUNTIME_DIR']);home=frontend.private_directory(env['HOME']);source=B/'native_frontend.py'
 if frontend.digest(source)!=source_sha:raise frontend.Refused('Reviewed candidate source changed before private copy')
 entry=frontend.private_path(home/'.local/bin/hypr-windowctl',runtime)
 if not entry.is_relative_to(home):raise frontend.Refused('Private copied product entry only')
 if not entry.is_file() or entry.is_symlink() or frontend.digest(entry)!=expected_legacy_sha:raise frontend.Refused('Exact copied legacy product entry required before candidate substitution')
 temp=entry.with_name('hypr-windowctl-native-candidate.new');fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o700)
 with os.fdopen(fd,'wb') as stream:stream.write(source.read_bytes());stream.flush();os.fsync(stream.fileno())
 os.replace(temp,entry)
 if frontend.digest(entry)!=source_sha or stat.S_IMODE(entry.stat().st_mode)!=0o700:raise frontend.Refused('Private frontend candidate copy differs')
 return entry

def create_config(env,entry,request_roots,compositor,service,service_root,path):
 runtime=frontend.private_directory(env['XDG_RUNTIME_DIR']);home=frontend.private_directory(env['HOME']);entry=frontend.private_path(entry,runtime);path=frontend.private_path(path,runtime)
 if not entry.is_relative_to(home) or not path.is_relative_to(home) or not request_roots or len(request_roots)>2 or len({r['identity']['pid'] for r in request_roots})!=len(request_roots):raise frontend.Refused('Explicit unique owned requester/config/entry paths required')
 selectors={k:env[k] for k in SELECTOR_KEYS if k in env};selectors['WINDOW_MOTION_NATIVE_CONFIG']=str(path)
 if not {'HOME','XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY'}.issubset(selectors):raise frontend.Refused('Exact private compositor selectors required')
 if any(r['cgroup']!=Path('/proc/self/cgroup').read_text() for r in request_roots):raise frontend.Refused('All request roots must belong to this captured scope')
 for r in request_roots:frontend.live(r['identity'])
 frontend.live(compositor);frontend.live(service);service_root=frontend.private_directory(service_root);frontend.private_path(service_root,runtime)
 socket_path=runtime/'hypr'/selectors['HYPRLAND_INSTANCE_SIGNATURE']/'.socket.sock';api=service_root/'api.sock'
 for p in [socket_path,api]:
  frontend.private_path(p,runtime);st=p.lstat()
  if not stat.S_ISSOCK(st.st_mode) or st.st_uid!=os.getuid():raise frontend.Refused('Owned current compositor/service socket required')
 cs=socket_path.stat();ss=api.stat();log=path.with_suffix('.jsonl');frontend.private_path(log,runtime)
 fd=os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600);os.close(fd)
 inputs={str(p):{'sha256':frontend.digest(p),'mode':stat.S_IMODE(p.stat().st_mode)} for p in SERVICE.glob('*.py')}
 config={'version':1,'runtime':str(runtime),'selectors':selectors,'entry':str(entry),'entrySHA256':frontend.digest(entry),'requestRoots':request_roots,'delegateInputs':inputs,'delegateDirectory':str(SERVICE),'serviceRoot':str(service_root),'session':selectors['HYPRLAND_INSTANCE_SIGNATURE'],'service':dict(service),'serviceSocketIdentity':[ss.st_dev,ss.st_ino],'compositor':dict(compositor),'compositorSocket':str(socket_path),'compositorSocketIdentity':[cs.st_dev,cs.st_ino],'log':str(log)}
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as stream:json.dump(config,stream,sort_keys=True,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
 return {'config':str(path),'log':str(log),'entry':str(entry),'configSHA256':frontend.digest(path),'entrySHA256':frontend.digest(entry),'environment':{'WINDOW_MOTION_NATIVE_CONFIG':str(path)}}
