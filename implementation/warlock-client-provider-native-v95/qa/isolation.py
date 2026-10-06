"""Import-safe private accessibility isolation; no bus/AT init at import."""
import json,os,re,socket,stat,struct,time
from pathlib import Path
class Refused(RuntimeError):pass
DROP={'AT_SPI_BUS_ADDRESS','GTK_A11Y','NO_AT_BRIDGE','GTK_MODULES','GTK_PATH','QT_ACCESSIBILITY_ALWAYS_ON','DBUS_SESSION_BUS_ADDRESS','DBUS_SESSION_BUS_PID','DBUS_STARTER_ADDRESS','DBUS_STARTER_BUS_TYPE','DISPLAY','XAUTHORITY','PYTHONPATH','PYTHONHOME','LD_PRELOAD','LD_AUDIT','GIO_EXTRA_MODULES','IBUS_ADDRESS','ATSPI_DBUS_IMPLEMENTATION','DESKTOP_AUTOSTART_ID','GTK_IM_MODULE','QT_IM_MODULE','XMODIFIERS','FCITX_DBUS_ADDRESS','FCITX_SOCKET_PATH','DBUS_SYSTEM_BUS_ADDRESS'}
def exact(d,keys):
 if type(d) is not dict or set(d)!=set(keys):raise Refused('Exact schema')
def process(pid):
 if type(pid) is not int or pid<=0:raise Refused('Positive PID')
 p=Path('/proc')/str(pid);s=p.stat()
 if s.st_uid!=os.getuid():raise Refused('Foreign process UID')
 f=(p/'stat').read_text().rsplit(')',1)[1].split()
 return {'pid':pid,'start':f[19],'pgid':int(f[2])}
def current(row):
 exact(row,('pid','start','pgid'))
 if process(row['pid'])!=row:raise Refused('Process incarnation changed')
 return row

def directory(p):
 p=Path(p)
 if not p.is_absolute() or p.resolve(strict=True)!=p:raise Refused('Canonical private directory')
 s=p.lstat()
 if not stat.S_ISDIR(s.st_mode) or s.st_uid!=os.getuid() or stat.S_IMODE(s.st_mode)!=0o700:raise Refused('Directory UID/mode')
 return p

def address_path(address,runtime):
 runtime=directory(runtime)
 if type(address) is not str or not address.startswith('unix:path=') or ';' in address or '%' in address or '\x00' in address:raise Refused('Single literal Unix path address')
 parts=address[10:].split(',')
 if len(parts)>2 or (len(parts)==2 and re.fullmatch(r'guid=[0-9a-f]{32}',parts[1]) is None):raise Refused('Closed bus address fields')
 p=Path(parts[0])
 if not p.is_absolute() or p.resolve(strict=True)!=p or not p.is_relative_to(runtime) or p==runtime:raise Refused('Private bus socket escapes runtime')
 cursor=p.parent
 while cursor!=runtime:
  directory(cursor);cursor=cursor.parent
 s=p.lstat()
 if not stat.S_ISSOCK(s.st_mode) or s.st_uid!=os.getuid():raise Refused('Owned socket required')
 return p

def peer(address,runtime,expected):
 current(expected);p=address_path(address,runtime);before=p.lstat()
 with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as stream:
  stream.settimeout(1);stream.connect(str(p));pid,uid,gid=struct.unpack('3i',stream.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
 after=p.lstat()
 if (before.st_dev,before.st_ino)!=(after.st_dev,after.st_ino) or uid!=os.getuid() or pid!=expected['pid']:raise Refused('Socket peer/incarnation mismatch')
 current(expected)
 return {'path':str(p),'device':after.st_dev,'inode':after.st_ino,'pid':pid,'uid':uid,'gid':gid,'start':expected['start']}

def child_env(base,runtime,session_address,at_address=None):
 runtime=directory(runtime);address_path(session_address,runtime)
 env={k:v for k,v in base.items() if k not in DROP and not k.startswith(('AT_SPI_','QT_ACCESSIBILITY_','FCITX_','IBUS_'))}
 for key in ('HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME'):
  p=directory(env[key])
  if not p.is_relative_to(runtime):raise Refused('Private child home/config escape')
 env.update(GIO_USE_VFS='local',XDG_RUNTIME_DIR=str(runtime),DBUS_SESSION_BUS_ADDRESS=session_address,GSETTINGS_BACKEND='memory',GTK_USE_PORTAL='0',GDK_BACKEND='wayland')
 if at_address is not None:
  address_path(at_address,runtime);env.update(AT_SPI_BUS_ADDRESS=at_address,GTK_A11Y='atspi',NO_AT_BRIDGE='0')
 return env

def read_private(path):
 p=Path(path)
 if not p.is_absolute() or p.resolve(strict=True)!=p:raise Refused('Canonical config')
 fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
 try:
  s=os.fstat(fd)
  if not stat.S_ISREG(s.st_mode) or s.st_uid!=os.getuid() or s.st_nlink!=1 or stat.S_IMODE(s.st_mode)!=0o600:raise Refused('Private single-link config')
  raw=os.read(fd,16385)
  if len(raw)>16384:raise Refused('Config capacity')
 finally:os.close(fd)
 def unique(rows):
  d={}
  for k,v in rows:
   if k in d:raise Refused('Duplicate config field')
   d[k]=v
  return d
 return json.loads(raw,object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(Refused('Nonfinite config')))

def write_private(path,value):
 raw=json.dumps(value,ensure_ascii=True,allow_nan=False).encode();fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'wb') as out:out.write(raw);out.flush();os.fsync(out.fileno())

def validate_collector(cfg,env):
 exact(cfg,('runtime','sessionAddress','sessionPeer','atAddress','atPeer','registry','allowedApplications'))
 if env.get('XDG_RUNTIME_DIR')!=cfg['runtime'] or env.get('DBUS_SESSION_BUS_ADDRESS')!=cfg['sessionAddress'] or env.get('AT_SPI_BUS_ADDRESS')!=cfg['atAddress']:raise Refused('Collector private environment mismatch')
 if env.get('GSETTINGS_BACKEND')!='memory' or env.get('GTK_A11Y')!='atspi' or env.get('NO_AT_BRIDGE')!='0':raise Refused('Collector bridge environment')
 for key in DROP-{'DBUS_SESSION_BUS_ADDRESS','AT_SPI_BUS_ADDRESS','GTK_A11Y','NO_AT_BRIDGE'}:
  if key in env:raise Refused('Inherited bridge/activation settings '+key)
 for key in env:
  if key.startswith(('AT_SPI_','QT_ACCESSIBILITY_','FCITX_','IBUS_')) and key!='AT_SPI_BUS_ADDRESS':raise Refused('Inherited AT setting '+key)
 for key in ('HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME'):
  p=directory(env[key])
  if not p.is_relative_to(Path(cfg['runtime'])):raise Refused('Collector home/config escape')
 if cfg['sessionAddress']==cfg['atAddress']:raise Refused('Separate session/accessibility buses')
 session=peer(cfg['sessionAddress'],cfg['runtime'],cfg['sessionPeer']);at=peer(cfg['atAddress'],cfg['runtime'],cfg['atPeer']);current(cfg['registry'])
 apps=cfg['allowedApplications']
 if type(apps) is not list or not 1<=len(apps)<=16:raise Refused('Application bound')
 for row in apps:current(row)
 if len({r['pid'] for r in apps})!=len(apps):raise Refused('Duplicate application')
 return {'session':session,'accessibility':at,'registry':cfg['registry']}

def no_activation_xml(uid):
 if type(uid) is not int or uid<0:raise Refused('UID')
 return ('<busconfig><type>accessibility</type><auth>EXTERNAL</auth>'
  '<policy context="default"><allow user="'+str(uid)+'"/><allow own="*"/>'
  '<allow send_destination="*"/><allow receive_sender="*"/>'
  '<deny send_destination="org.freedesktop.systemd1"/></policy></busconfig>')

def owned_descendant(pid,root):
 current(root);seen=set()
 while pid not in seen and pid>1:
  if pid==root['pid']:return process(pid)
  seen.add(pid);p=Path('/proc')/str(pid)
  if p.stat().st_uid!=os.getuid():raise Refused('Foreign descendant UID')
  pid=int((p/'stat').read_text().rsplit(')',1)[1].split()[1])
 raise Refused('Not an owned descendant')

def decode_request(raw):
 if type(raw) is not bytes or not raw or len(raw)>16384:raise Refused('JSON request bound')
 def unique(rows):
  d={}
  for k,v in rows:
   if k in d:raise Refused('Duplicate request field')
   d[k]=v
  return d
 return json.loads(raw,object_pairs_hook=unique,parse_constant=lambda _:(_ for _ in ()).throw(Refused('Nonfinite JSON')))
