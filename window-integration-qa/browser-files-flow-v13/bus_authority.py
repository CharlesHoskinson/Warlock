"""Read-only proof of one actual owned Brave connection to its private session bus.

This does not inspect current libc getenv or current GIO VFS. The selector
witness is the exact guarded final pre-exec record; proc's old environment range
is retained separately as a diagnostic and cannot establish current getenv.
"""
from pathlib import Path
import ast,hashlib,os,re,socket,stat,struct,subprocess,time
BINARY=Path('/opt/brave-bin/brave');B=Path(__file__).resolve().parent
METHODS={'ListNames':0,'GetConnectionUnixProcessID':1,'GetConnectionUnixUser':1}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def selected_preexec(launch,identity,runtime):
 address='unix:path='+str(runtime/'bus')
 if launch.get('pid')!=identity['pid'] or launch.get('start')!=identity['start'] or launch.get('appBusSelectors')!={'DBUS_SESSION_BUS_ADDRESS':address,'DBUS_SYSTEM_BUS_ADDRESS':address} or launch.get('privateGioVfs')!='local' or launch.get('binarySHA256')!=sha(BINARY):raise RuntimeError('Exact final pre-exec selector/exec witness mismatch')
 return {'source':'Guarded final os.execve environment witness, not direct current getenv/GIO inspection','witnessPID':launch['pid'],'witnessStart':launch['start'],'appBusSelectors':launch['appBusSelectors'],'privateGioVfs':launch['privateGioVfs'],'binarySHA256':launch['binarySHA256'],'guardedExecSource':str(B/'browser_exec.py'),'guardedExecSourceSHA256':sha(B/'browser_exec.py')}
def parse_reply(method,text):
 if method not in METHODS:raise RuntimeError('Read-only bus method refused')
 value=ast.literal_eval(re.sub(r'\buint32\s+','',text.strip()))
 if not isinstance(value,tuple) or len(value)!=1:raise RuntimeError('Exact one-value typed bus reply required')
 result=value[0]
 if method=='ListNames':
  if not isinstance(result,list) or any(not isinstance(x,str) for x in result) or len(result)>256 or len(set(result))!=len(result):raise RuntimeError('Bounded unique actual bus name list required')
  if 'org.freedesktop.DBus' not in result or any(x!='org.freedesktop.DBus' and not re.fullmatch(r':[0-9]+\.[0-9]+',x) for x in result):raise RuntimeError('Unexpected private bus owned name; no name exemption')
 elif type(result)!=int or result<0 or result>2**32-1:raise RuntimeError('Exact uint32 actual bus identity required')
 return result

def prove(launch,identity,runtime,env,bus_identity,same,target_guard):
 deadline=time.monotonic()+8
 runtime=Path(runtime);address='unix:path='+str(runtime/'bus');path=runtime/'bus';evidence={'scope':'Observed actual session-bus connection plus verified launch selectors; not direct current getenv or GIO inspection','queries':[],'result':'pending','root':dict(identity),'bus':dict(bus_identity)}
 try:
  target_guard()
  if env.get('DBUS_SESSION_BUS_ADDRESS')!=address or env.get('DBUS_SYSTEM_BUS_ADDRESS')!=address:raise RuntimeError('Both explicit app bus selectors must be this owned private route')
  evidence['preExecWitness']=selected_preexec(launch,identity,runtime)
  def root_live():
   target_guard()
   if time.monotonic()>=deadline:raise RuntimeError('Bounded actual private-bus/root observation deadline exceeded')
   if not same(identity):raise RuntimeError('Actual browser root lifetime changed')
   p=Path('/proc')/str(identity['pid']);status={k:v.strip() for k,v in (line.split(':',1) for line in (p/'status').read_text().splitlines() if ':' in line)}
   if p.stat().st_uid!=os.getuid() or status.get('Uid','').split()!=[str(os.getuid())]*4 or (p/'cgroup').read_text()!=Path('/proc/self/cgroup').read_text():raise RuntimeError('Actual browser UID/owned scope mismatch')
   if os.readlink(p/'exe')!=str(BINARY) or sha(p/'exe')!=launch['binarySHA256']:raise RuntimeError('Actual browser executable differs from final launch witness')
  def socket_identity():
   if path.is_symlink() or path.resolve()!=path or not same(bus_identity):raise RuntimeError('Private bus path/process lifetime changed')
   st=path.stat()
   if not stat.S_ISSOCK(st.st_mode) or st.st_uid!=os.getuid():raise RuntimeError('Owned private bus socket required')
   return [st.st_dev,st.st_ino]
  root_live();before=socket_identity();evidence['rootLifetimeBefore']=True;evidence['socketIdentity']=before
  def query(method,*args):
   if method not in METHODS or len(args)!=METHODS[method] or any(not re.fullmatch(r':[0-9]+\.[0-9]+',x) for x in args):raise RuntimeError('Fixed read-only bus query argument allowlist required')
   root_live()
   if socket_identity()!=before:raise RuntimeError('Private bus socket replaced before query')
   with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as conn:
    conn.settimeout(2);conn.connect(str(path));pid,uid,gid=struct.unpack('3i',conn.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
    if pid!=bus_identity['pid'] or uid!=os.getuid() or not same(bus_identity):raise RuntimeError('Exact owned private bus actual kernel peer required')
   cmd=['/usr/bin/gdbus','call','--address',address,'--dest','org.freedesktop.DBus','--object-path','/org/freedesktop/DBus','--method','org.freedesktop.DBus.'+method,*args]
   row={'method':method,'arguments':list(args),'command':cmd,'peer':{'pid':pid,'uid':uid,'gid':gid}};evidence['queries'].append(row)
   reply=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=min(2,max(.01,deadline-time.monotonic())));row.update(returncode=reply.returncode,stdout=reply.stdout,stderr=reply.stderr)
   if reply.returncode:raise RuntimeError('Actual read-only bus query refused/failed:'+method+':'+reply.stderr)
   value=parse_reply(method,reply.stdout);row['parsed']=value
   root_live()
   if socket_identity()!=before:raise RuntimeError('Private bus socket/process changed across query')
   return value
  names=query('ListNames');unique=sorted([x for x in names if x.startswith(':')],key=lambda x:tuple(map(int,x[1:].split('.'))))
  for name in unique:
   pid=query('GetConnectionUnixProcessID',name)
   if pid!=identity['pid']:continue
   uid=query('GetConnectionUnixUser',name)
   if uid!=os.getuid():raise RuntimeError('Observed owned browser bus connection UID mismatch')
   root_live()
   if socket_identity()!=before:raise RuntimeError('Private bus changed at actual browser binding')
   evidence.update(result='pass',connection={'name':name,'pid':pid,'uid':uid},rootLifetimeAfter=True)
   return evidence
  raise RuntimeError('No actual exact owned Brave root connection observed on private session bus')
 except Exception as error:evidence.update(result='fail',error=repr(error));return evidence
