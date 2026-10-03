"""Transport/backend checks before public AT-SPI key APIs; never opens X."""
from pathlib import Path
import os,socket,stat,struct,urllib.parse,xml.etree.ElementTree as ET
MANAGER='org.freedesktop.a11y.Manager';PATH='/org/freedesktop/a11y/Manager';IFACE='org.freedesktop.a11y.KeyboardMonitor'

def private_bus_socket(address,root):
 if not address.startswith('unix:') or ';' in address:raise RuntimeError('Explicit private Unix D-Bus address required')
 fields=dict(part.split('=',1) for part in address[5:].split(','))
 if set(fields)-{'path','guid'} or 'path' not in fields:raise RuntimeError('Private bus requires filesystem path, not inherited/abstract socket')
 path=Path(urllib.parse.unquote(fields['path']));root=Path(root)
 if not path.is_absolute() or not path.resolve().is_relative_to(root.resolve()):raise RuntimeError('D-Bus socket outside private runtime')
 before=path.lstat()
 if not stat.S_ISSOCK(before.st_mode) or before.st_uid!=os.getuid():raise RuntimeError('Private bus socket must be owned nonsymlink socket')
 with socket.socket(socket.AF_UNIX) as connection:
  connection.settimeout(.5);connection.connect(str(path))
  pid,uid,gid=struct.unpack('3i',connection.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
  if uid!=os.getuid() or pid<=0:raise RuntimeError('Private bus server credentials invalid')
 after=path.lstat()
 if (before.st_dev,before.st_ino)!=(after.st_dev,after.st_ino):raise RuntimeError('Private bus socket changed')
 return {'path':str(path),'serverPID':pid,'socketIdentity':[before.st_dev,before.st_ino]}

class BackendGuard:
 def __init__(self,connection,owner,owner_query):self.connection=connection;self.owner=owner;self.owner_query=owner_query;self.device=None
 def check(self):
  if self.connection.is_closed():raise RuntimeError('Private session D-Bus disconnected before key operation')
  if self.owner_query()!=self.owner:raise RuntimeError('KeyboardMonitor owner changed before key operation')
 def attach(self,device):
  self.check()
  if device is None or device.__gtype__.name!='AtspiDeviceA11yManager':raise RuntimeError('Refuse X11/Legacy/unknown fallback before keysym/keycode API')
  self.device=device;return device
 def invoke(self,method,*args):
  self.check()
  if self.device is None:raise RuntimeError('No validated Manager device')
  return getattr(self.device,method)(*args)

def session_preflight(root,environment,Gio,GLib):
 socket_evidence=private_bus_socket(environment.get('DBUS_SESSION_BUS_ADDRESS',''),root)
 bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
 def call(dest,path,iface,method,signature='()',args=()):
  return bus.call_sync(dest,path,iface,method,GLib.Variant(signature,args),None,Gio.DBusCallFlags.NO_AUTO_START,2000,None).unpack()
 def owner():return call('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','GetNameOwner','(s)',(MANAGER,))[0]
 captured=owner()
 xml=call(captured,PATH,'org.freedesktop.DBus.Introspectable','Introspect')[0]
 interface=next((i for i in ET.fromstring(xml).findall('interface') if i.get('name')==IFACE),None)
 if interface is None:raise RuntimeError('Live owner lacks KeyboardMonitor interface')
 expected={'WatchKeyboard':[],'UnwatchKeyboard':[],'GrabKeyboard':[],'UngrabKeyboard':[],'SetKeyGrabs':[('in','au'),('in','a(uu)')]}
 for name,signature in expected.items():
  method=next((m for m in interface.findall('method') if m.get('name')==name),None)
  if method is None or [(a.get('direction','in'),a.get('type')) for a in method.findall('arg')]!=signature:raise RuntimeError('KeyboardMonitor method ABI mismatch:'+name)
 a11y={'requiredForDirectManagerABI':False,'autoactivation':False,'available':False}
 address=environment.get('AT_SPI_BUS_ADDRESS')
 if not address:
  has=call('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','NameHasOwner','(s)',('org.a11y.Bus',))[0]
  if has:address=call('org.a11y.Bus','/org/a11y/bus','org.a11y.Bus','GetAddress')[0]
 if address:
  transport=private_bus_socket(address,root)
  accessibility=Gio.DBusConnection.new_for_address_sync(address,Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
  accessibility.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','GetId',None,None,Gio.DBusCallFlags.NO_AUTO_START,2000,None)
  a11y.update(available=True,transport=transport);accessibility.close_sync(None)
 guard=BackendGuard(bus,captured,owner);guard.check()
 return guard,{'sessionBus':socket_evidence,'managerOwner':captured,'managerProtocolVerified':True,'a11yTransport':a11y,'xDisplayRequired':False,'xlibKeyConversions':False}
