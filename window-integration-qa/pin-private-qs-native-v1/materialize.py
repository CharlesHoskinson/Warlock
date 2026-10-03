"""Real installed-QS private launch admission. No launch during import.

Final registration uses only procfs and owned sockets; it calls no provider API.
The root launcher publishes all selected immutable configs before its first
read-only QML query, physical setup input or native feature operation.
"""
from pathlib import Path
import hashlib,json,os,re,shutil,socket,stat,struct,time,sys
from io_guard import directory,publish,publish_json,sha,strict,verify,exact
from selection import *
from payload import verify_payload,load
sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope,verify_runtime,verify_parent
sys.path.pop(0)
pin_config=load('_pin_qs_exact_config_builder',HELPER_STAGE/'pin_config.py')
SELECTORS=('HOME','XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY','DBUS_SESSION_BUS_ADDRESS','WINDOW_PIN_NATIVE_CONFIG','WINDOW_PIN_PROCESS_CONFIG','WINDOW_OBJECT_LIFETIME_CONFIG')
FORBIDDEN=tuple(pin_config.FORBIDDEN)+('XAUTHORITY','QT_QPA_PLATFORMTHEME','QS_CONFIG_PATH','QS_CONFIG_NAME','QS_MANIFEST')
def identity(pid):
 if type(pid)is not int or pid<=0:raise ValueError('Typed actual PID required')
 p=Path('/proc')/str(pid);fields=(p/'stat').read_text().rsplit(')',1)[1].split();status={k:v.strip()for k,v in (r.split(':',1)for r in(p/'status').read_text().splitlines()if ':'in r)}
 if p.stat().st_uid!=os.getuid()or status.get('Uid','').split()!=[str(os.getuid())]*4:raise ValueError('Actual owner UID differs')
 return dict(pid=pid,start=fields[19],parent=int(fields[1]),pgid=int(fields[2]))
def exact_exec(pid,start,env,command):
 before=identity(pid);p=Path('/proc')/str(pid)
 if before['start']!=str(start)or before['pgid']!=pid:raise ValueError('Actual registered QS lifetime/group differs')
 rawargv=(p/'cmdline').read_bytes();argv=[x.decode()for x in rawargv.rstrip(b'\0').split(b'\0')];executable=str((p/'exe').resolve())
 exe_stat=(p/'exe').stat();named=QS.stat()
 if executable!=str(QS)or argv!=command or sha(p/'exe')!=QS_SHA or (exe_stat.st_dev,exe_stat.st_ino)!=(named.st_dev,named.st_ino)or (named.st_dev,named.st_ino,stat.S_IMODE(named.st_mode))!=(32,127204,0o755):raise ValueError('Exact installed QS final exec/source/argv required')
 actual=dict(v.split(b'=',1)for v in(p/'environ').read_bytes().split(b'\0')if b'='in v)
 if any(actual.get(k.encode())!=env[k].encode()for k in SELECTORS)or any(actual.get(k.encode())not in(None,b'')for k in FORBIDDEN):raise ValueError('Actual preselected private selectors/forbidden handles differ')
 group=(p/'cgroup').read_bytes();limits=(p/'limits').read_text()
 if group!=Path('/proc/self/cgroup').read_bytes()or not re.search(rb'/qa-harness\.slice/qa-harness-[A-Za-z0-9_-]+\.scope(?:\n|$)',group)or not re.search(r'^Max core file size\s+1\s+1\s+bytes$',limits,re.M):raise ValueError('Exact QA owner scope/core1 limits required')
 if identity(pid)!=before:raise ValueError('QS lifetime changed during final exec observation')
 return dict(identity=before,argv=argv,rawARGVHash=hashlib.sha256(rawargv).hexdigest(),executable=executable,executableSHA256=QS_SHA,cgroupSHA256=hashlib.sha256(group).hexdigest())
def prepare(session,life):
 require_qa_scope();session.guard();verify_selection();verify_payload()
 if life not in('A','B'):raise ValueError('Two fixed independent QS lifetimes only')
 runtime=verify_runtime(session.env['XDG_RUNTIME_DIR']);peer=verify_parent(session.env)
 if peer['pid']!=session.evidence['compositorPID']or Path(peer['path']).parent!=runtime:raise ValueError('Actual private compositor Wayland peer required')
 before=identity(peer['pid'])
 if before['start']!=session.evidence['compositorStart']:raise ValueError('Private compositor lifetime changed')
 home=runtime/('taskbar-'+life);shutil.copytree(B/'payload/home',home)
 for p in [home,*sorted(home.rglob('*'))]:
  if p.is_symlink()or p.stat().st_uid!=os.getuid():raise ValueError('Foreign/linked private copy refused')
  if p.is_dir():p.chmod(0o700)
 for name in ('PinWindowMenu.qml','Windows.qml'):
  overlay=B/'frontend-observation'/name;destination=home/'.config/omarchy/plugins/hoskinson.windows/private_pin_process_v1'/name
  if sha(destination)!=sha(COMPOSITION/'frontend'/name):raise ValueError('Original frontend before diagnostic overlay changed')
  destination.unlink();publish(destination,overlay.read_bytes())
 (home/'.local/state').mkdir(mode=0o700,exist_ok=True)
 settings=home/'.config/omarchy/taskbar-settings.json';original_settings=strict(settings.read_bytes());original_settings['combineMode']='never';settings.unlink();publish_json(settings,original_settings)
 directory(home);(home/'xdg-cache').mkdir(mode=0o700)
 entry=pin_config.install(home,runtime)
 provider=home/'.local/share/qml/WindowObjectLifetimeV1/libobjectlifetime.so'
 if sha(provider)!=sha(PROVIDER)or provider.stat().st_dev!=runtime.stat().st_dev:raise ValueError('Exact tmpfs provider placement required')
 env={k:v for k,v in session.env.items()if k not in FORBIDDEN and not k.startswith(('HYPR_WINDOWCTL_','PYTHON'))}
 env.update(HOME=str(home),XDG_CONFIG_HOME=str(home/'.config'),XDG_DATA_HOME=str(home/'.local/share'),XDG_STATE_HOME=str(home/'.local/state'),XDG_CACHE_HOME=str(home/'xdg-cache'),PATH=str(home/'.local/bin')+':'+str(B/'payload/omarchy/bin')+':/usr/bin',OMARCHY_PATH=str(B/'payload/omarchy'),QML_IMPORT_PATH=str(home/'.local/share/qml'),QT_QPA_PLATFORM='wayland',QT_NO_XDG_DESKTOP_PORTAL='1',GSETTINGS_BACKEND='memory',GDK_DEBUG='no-portals',GIO_USE_VFS='local',PYTHONDONTWRITEBYTECODE='1',WINDOW_OBJECT_LIFETIME_CONFIG=str(home/'provider-config'),WINDOW_PIN_NATIVE_CONFIG=entry['path'],WINDOW_PIN_PROCESS_CONFIG=str(home/'process-config.json'))
 if identity(peer['pid'])!=before:raise ValueError('Compositor changed during private copy')
 return dict(life=life,home=str(home),runtime=str(runtime),environment=env,entry=entry,provider=str(provider),command=[str(QS),'-p',str(B/'payload/omarchy/shell')],published=False)
def peer_socket(path,pid,runtime):
 path=Path(path);runtime=directory(runtime)
 if path.resolve()!=path or not path.is_relative_to(runtime):raise ValueError('Private canonical socket required')
 s=path.lstat()
 if not stat.S_ISSOCK(s.st_mode)or s.st_uid!=os.getuid():raise ValueError('Owned actual socket required')
 with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)as conn:
  conn.settimeout(2);conn.connect(str(path));actual=struct.unpack('3i',conn.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
 if actual[0]!=pid or actual[1]!=os.getuid():raise ValueError('Actual socket peer differs')
 after=path.lstat()
 if (s.st_dev,s.st_ino,s.st_mode,s.st_uid)!=(after.st_dev,after.st_ino,after.st_mode,after.st_uid):raise ValueError('Socket changed during admission')
 return dict(path=str(path),device=s.st_dev,inode=s.st_ino,peerPID=actual[0],peerUID=actual[1])
def mapped_provider(pid,path):
 p=Path(path);s=p.lstat();raw=(Path('/proc')/str(pid)/'maps').read_text();rows=[];aliases=[]
 for line in raw.splitlines():
  v=line.split(None,5)
  if len(v)!=6:continue
  if v[5]==str(p):rows.append(v)
  if v[5].endswith('/libobjectlifetime.so')or '/libobjectlifetime-process-'in v[5]:aliases.append(v[5])
 if not rows:return None
 if not stat.S_ISREG(s.st_mode)or s.st_uid!=os.getuid()or s.st_nlink!=1 or stat.S_IMODE(s.st_mode)!=0o600 or set(aliases)!={str(p)}or not any('x'in r[1]for r in rows)or any(int(r[4])!=s.st_ino or tuple(int(x,16)for x in r[3].split(':'))!=(os.major(s.st_dev),os.minor(s.st_dev))for r in rows)or sha(p)!=sha(PROVIDER):raise ValueError('Actual unique provider image/source/mapping differs')
 return dict(path=str(p),sha256=sha(p),mode=stat.S_IMODE(s.st_mode),device=s.st_dev,inode=s.st_ino,rawMapsSHA256=hashlib.sha256(raw.encode()).hexdigest(),rows=rows)
def publish_configs(session,process,prepared,frozen,evidence_path):
 """Only actual final exec registration; no IPC/provider method is called here."""
 require_qa_scope();session.guard();verify(frozen);env=prepared['environment'];runtime=verify_runtime(prepared['runtime']);home=directory(prepared['home']);start=identity(process.pid)['start'];observations=[];deadline=time.monotonic()+5
 def retain():publish_json(evidence_path.parent/('admission-'+str(len(observations))+'.json'),dict(observations=observations,published=False))
 while True:
  if process.poll()is not None:raise ValueError('Actual QS exited before config admission')
  row=dict(finalExec=exact_exec(process.pid,start,env,prepared['command']));observations.append(row)
  try:row['provider']=mapped_provider(process.pid,prepared['provider'])
  except BaseException as e:row['error']=repr(e);retain();raise
  retain()
  if time.monotonic()>=deadline:raise TimeoutError('Original bounded QS admission observation expired')
  if row['provider']:break
  time.sleep(.03)
 first=row['finalExec'];image=row['provider'];selectors={k:env[k]for k in SELECTORS};root=pin_config.source_process(process.pid,selectors,'shell')
 if root['argv']!=prepared['command']or root['identity']!=first['identity']:raise ValueError('Final requester source tuple changed')
 compenv={k:session.env[k]for k in('XDG_RUNTIME_DIR','DBUS_SESSION_BUS_ADDRESS')};compositor=pin_config.source_process(session.evidence['compositorPID'],compenv)
 if compositor['identity']['start']!=session.evidence['compositorStart']or compositor['executable']!=str(CORE)or compositor['executableSHA256']!=CORE_SHA:raise ValueError('Actual selected compositor differs')
 ipc=runtime/'hypr'/session.evidence['signature']/'.socket.sock';bus=runtime/'bus'
 peers=[peer_socket(ipc,compositor['identity']['pid'],runtime),peer_socket(runtime/env['WAYLAND_DISPLAY'],compositor['identity']['pid'],runtime),peer_socket(bus,session.evidence['privateBus']['pid'],runtime)]
 fields=[('pid',process.pid),('start',start),('executable',str(QS)),('executableSHA256',QS_SHA),('argvSHA256',first['rawARGVHash']),('cgroupSHA256',first['cgroupSHA256']),('runtime',str(runtime)),('home',str(home)),('image',image['path']),('imageSHA256',image['sha256']),('imageMode',image['mode']),('imageDevice',image['device']),('imageInode',image['inode'])]
 raw=('qml-object-lifetime-config-v1\n'+''.join(k+'='+str(v)+'\n'for k,v in fields)).encode();provider_hash=publish(env['WINDOW_OBJECT_LIFETIME_CONFIG'],raw)
 pin=pin_config.write(prepared['entry'],runtime,selectors,[root],compositor,dict(path=str(PLUGIN),sha256=PLUGIN_SHA,mode=stat.S_IMODE(PLUGIN.stat().st_mode)))
 runtime_path=B/'process-runtime-inputs.json'
 if str(runtime_path)not in frozen['inputs']or sha(runtime_path)!=frozen['inputs'][str(runtime_path)]:raise ValueError('Exact separately reviewed runtime source manifest required')
 selected=strict(runtime_path.read_bytes());verify(selected)
 dynamic=dict(inputs=dict(selected['inputs']),inputModes=dict(selected['inputModes']),symlinks=dict(selected['symlinks']))
 # Same exact code bytes at their actual fresh runtime paths; no source cache.
 for p in sorted(home.rglob('*')):
  if p.is_symlink():raise ValueError('Runtime named source aliases refused')
  if p.is_file():dynamic['inputs'][str(p)]=sha(p);dynamic['inputModes'][str(p)]=stat.S_IMODE(p.stat().st_mode)
 manifest=home/'process-frozen-inputs.json';manifest_raw=(json.dumps(dynamic,separators=(',',':'),allow_nan=False)+'\n').encode()
 if len(manifest_raw)>16*1024*1024:raise ValueError('Actual source manifest exceeds unchanged native16MiB limit')
 manifest_hash=publish(manifest,manifest_raw)
 process_config=dict(schema='qml-pin-process-config-v1',pinConfig=dict(path=prepared['entry']['path'],sha256=sha(prepared['entry']['path'])),frozenInputs=dict(path=str(manifest),sha256=manifest_hash));process_hash=publish_json(env['WINDOW_PIN_PROCESS_CONFIG'],process_config)
 final=exact_exec(process.pid,start,env,prepared['command']);last_image=mapped_provider(process.pid,prepared['provider']);session.guard()
 if final!=first or any(last_image[k]!=image[k]for k in('path','sha256','mode','device','inode'))or pin_config.source_process(process.pid,selectors,'shell')!=root:raise ValueError('Actual launch/source identity changed across publication')
 prepared.update(published=True,process=process,requester=root,pinConfig=pin,configs=dict(providerSHA256=provider_hash,pinSHA256=sha(prepared['entry']['path']),processSHA256=process_hash,manifestSHA256=manifest_hash))
 evidence=dict(schema='pin-private-qs-final-admission-v1',accepted=True,observations=observations,final=final,provider=image,providerAfter=last_image,peers=peers,requester=root,compositor=compositor,configs=prepared['configs'],providerMethodsBeforePublication=0,fixtureSetupNotFeatureAcceptance=True)
 publish_json(evidence_path,evidence);return evidence
