"""Fresh V3 private activation-free bus adapter; all V4 host guards remain inherited."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,socket,stat,struct,subprocess
from xml.sax.saxutils import escape
B=Path(__file__).resolve().parent;HOST=B.parent/'private-weston-aq-host-v4'
spec=importlib.util.spec_from_file_location('_browser_v3_accepted_host_v4',HOST/'weston_host.py');accepted=importlib.util.module_from_spec(spec);spec.loader.exec_module(accepted)
original=accepted.original
BUS_TEMPLATE='''<!DOCTYPE busconfig PUBLIC "-//freedesktop//DTD D-BUS Bus Configuration 1.0//EN" "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">
<busconfig>
 <type>session</type>
 <listen>@PRIVATE_BUS_ADDRESS@</listen>
 <auth>EXTERNAL</auth>
 <policy context="default">
  <allow send_destination="*" eavesdrop="true"/>
  <allow receive_sender="*" eavesdrop="true"/>
  <allow own="*"/>
 </policy>
</busconfig>
'''
def bus_command(command,runtime,address,config):
 expected=['/usr/bin/dbus-daemon','--session','--nofork','--address='+address]
 if list(map(str,command))!=expected:raise RuntimeError('Exact inherited private bus invocation required')
 root=original.qa.verify_runtime(runtime)
 if address!='unix:path='+str(root/'bus') or config.parent!=root or config.name!='browser-session-bus.conf':raise RuntimeError('Exact private bus config/socket selectors required')
 return ['/usr/bin/dbus-daemon','--config-file='+str(config),'--nofork','--address='+address]
class BrowserWestonHost(accepted.ReviewedWestonHost):
 def launch(self,name,command,env=None):
  if name=='privateBus':
   root=original.qa.verify_runtime(self.runtime);address=self.env['DBUS_SESSION_BUS_ADDRESS'];config=root/'browser-session-bus.conf'
   new=bus_command(command,root,address,config)
   data=BUS_TEMPLATE.replace('@PRIVATE_BUS_ADDRESS@',escape(address)).encode('utf-8')
   fd=os.open(config,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
   with os.fdopen(fd,'wb') as stream:stream.write(data)
   self.evidence['privateBusActivationPolicy']={'config':str(config),'sha256':hashlib.sha256(data).hexdigest(),'actualConfigXml':data.decode('utf-8'),'serviceDirectories':[],'includes':[],'mainBusChanges':False,'scope':'Only this owned private fixture bus; no portal/VFS/accessibility service functionality claimed'}
   return super().launch(name,new,env)
  return super().launch(name,command,env)
 def wait_socket(self,name,proc):
  result=super().wait_socket(name,proc)
  if name!='bus':return result
  original.qa.require_qa_scope();root=original.qa.verify_runtime(self.runtime);path=root/'bus'
  rows=[r for p,r in self.processes if p is proc and r['name']=='privateBus']
  if len(rows)!=1 or not original.same_process(rows[0]) or proc.poll() is not None:raise RuntimeError('Exact live registered bus process required')
  before=original.socket_identity(path,root)
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as conn:
   conn.settimeout(2);conn.connect(str(path));pid,uid,gid=struct.unpack('3i',conn.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
   if pid!=proc.pid or uid!=os.getuid():raise RuntimeError('Private bus kernel peer mismatch')
  # A real read-only bus query tests the effective daemon policy, not just XML.
  cmd=['/usr/bin/gdbus','call','--address',self.env['DBUS_SESSION_BUS_ADDRESS'],'--dest','org.freedesktop.DBus','--object-path','/org/freedesktop/DBus','--method','org.freedesktop.DBus.ListActivatableNames']
  reply=subprocess.run(cmd,env=dict(self.env,GIO_USE_VFS='local'),capture_output=True,text=True,timeout=6)
  if reply.returncode:raise RuntimeError('Private activation policy query failed:'+reply.stderr)
  parsed=ast.literal_eval(reply.stdout.strip().replace('@as ',''))
  if not isinstance(parsed,tuple) or len(parsed)!=1 or parsed[0]!=['org.freedesktop.DBus']:raise RuntimeError('Private bus unexpectedly permits activation:'+reply.stdout)
  if before!=original.socket_identity(path,root) or not original.same_process(rows[0]) or proc.poll() is not None:raise RuntimeError('Private bus identity changed across query')
  self.evidence['privateBusActivationPolicy'].update(peer={'pid':pid,'uid':uid,'gid':gid},socket=before,activatableNames=parsed[0],query=cmd,queryReply=reply.stdout,queryExit=reply.returncode)
  return result
class PrivateHyprSession(accepted.PrivateHyprSession):
 def __init__(self,output,main_env,width,height,nested_lua,dri_prime=None,mesa_vendor=False):
  super().__init__(output,main_env,width,height,nested_lua,dri_prime,mesa_vendor)
  self.host=BrowserWestonHost(output,main_env,width,height,dri_prime,mesa_vendor);self.evidence=self.host.evidence
