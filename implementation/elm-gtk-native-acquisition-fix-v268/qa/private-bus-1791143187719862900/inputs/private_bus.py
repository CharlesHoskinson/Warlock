"""Private activation overlay; installation and desktop bus stay untouched."""
import configparser,hashlib,json,os,shlex,signal,socket,struct,time
from pathlib import Path
from xml.sax.saxutils import escape
from gi.repository import Gio,GLib
from activation_import import identity,live
class Refused(RuntimeError):pass

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
class Activations:
 def __init__(self,runtime,output):
  self.runtime=Path(runtime);self.output=Path(output);self.root=self.runtime/'activations';self.root.mkdir(mode=0o700);self.services=self.root/'services';self.services.mkdir(mode=0o700);self.journals=self.output/'activation-journals';self.journals.mkdir(mode=0o700);self.records=[];self.connection=None
 def install(self,definitions=None):
  # Definitions are captured installed files; no shell or Desktop Exec interpolation.
  if definitions is None:
   definitions={}
   for folder in [Path('/usr/local/share/dbus-1/services'),Path('/usr/share/dbus-1/services')]:
    for file in sorted(folder.glob('*.service')):
     parsed=configparser.ConfigParser(interpolation=None,strict=True);parsed.read(file)
     if 'D-BUS Service' not in parsed:raise Refused('service section')
     row=parsed['D-BUS Service'];name=row['Name'];argv=shlex.split(row['Exec'])
     if name not in definitions:definitions[name]=(argv,file)
  supervisor=Path(__file__).with_name('activation-supervisor.py')
  for name,(argv,source) in sorted(definitions.items()):
   if not name or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-' for c in name):raise Refused('service name')
   if not argv or not Path(argv[0]).is_absolute() or any('%' in a or '\0' in a for a in argv):raise Refused('actual closed Exec argv')
   descriptor=self.root/(name+'.json');record={'argv':argv,'binarySHA256':digest(argv[0])};descriptor.write_text(json.dumps(record));descriptor.chmod(0o600)
   journal=self.journals/name;journal.mkdir(mode=0o700)
   execargv=['/usr/bin/python3','-B',str(supervisor),str(descriptor),str(journal)]
   (self.services/(name+'.service')).write_text('[D-BUS Service]\nName='+name+'\nExec='+shlex.join(execargv)+'\n')
   self.records.append({'name':name,'source':str(source),'sourceSHA256':digest(source),'argv':argv,'binarySHA256':record['binarySHA256'],'descriptor':str(descriptor),'descriptorSHA256':digest(descriptor),'journalDirectory':str(journal)})
  source=Path('/usr/share/dbus-1/session.conf');body=source.read_text()
  if body.count('<standard_session_servicedirs />')!=1:raise Refused('owning session configuration shape')
  body=body.replace('<standard_session_servicedirs />','<servicedir>'+escape(str(self.services))+'</servicedir>')
  body=body.replace('>session.d<','>/usr/share/dbus-1/session.d<').replace('>contexts/dbus_contexts<','>/usr/share/dbus-1/contexts/dbus_contexts<')
  config=self.root/'session.conf';config.write_text(body)
  (self.output/'activation-inventory.json').write_text(json.dumps({'services':self.records,'supervisorSHA256':digest(supervisor),'configurationSource':str(source),'configurationSourceSHA256':digest(source),'configurationSHA256':digest(config)},indent=2)+'\n')
  return config
 def connect(self,busrow,deadline):
  path=self.runtime/'bus'
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
   s.settimeout(max(.001,min(3,deadline-time.monotonic())));s.connect(str(path));pid,uid,_=struct.unpack('3i',s.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
   if pid!=busrow['pid'] or uid!=os.getuid() or not live(busrow):raise Refused('exact private bus peer')
  self.connection=Gio.DBusConnection.new_for_address_sync('unix:path='+str(path),Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
  self.busrow=busrow
  self.busguid=self.call('GetId',(),'()',deadline)[0]
  if type(self.busguid)!=str or len(self.busguid)!=32 or any(c not in '0123456789abcdef' for c in self.busguid):raise Refused('private bus GUID')
 def call(self,member,args,signature,deadline):
  left=deadline-time.monotonic()
  if left<=0 or not live(self.busrow):raise Refused('original private bus deadline/identity')
  result=self.connection.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus',member,GLib.Variant(signature,args),None,Gio.DBusCallFlags.NONE,max(1,int(min(3,left)*1000)),None).unpack()
  if time.monotonic()>=deadline:raise Refused('original private bus deadline')
  return result
 def snapshots(self):
  found=[]
  for record in self.records:
   for path in sorted(Path(record['journalDirectory']).glob('*.jsonl')):
    raw=path.read_bytes()
    if len(raw)>1024*1024:raise Refused('activation journal bound')
    lines=raw.split(b'\n');rows=[json.loads(x) for x in lines[:-1] if x]
    if not rows or rows[0]['kind']!='supervisor-start' or [r['sequence'] for r in rows]!=list(range(1,len(rows)+1)):raise Refused('activation journal sequence')
    found.append((record,path,rows))
  return found
 def verify_wrapper(self,record,rows):
  wrapper=rows[0]['identity']
  if not live(wrapper):raise Refused('activation wrapper retired')
  expected=['/usr/bin/python3','-B',str(Path(__file__).with_name('activation-supervisor.py')),record['descriptor'],record['journalDirectory']]
  proc=Path('/proc')/str(wrapper['pid']);actual=(proc/'cmdline').read_bytes().split(b'\0')[:-1]
  if actual!=[x.encode() for x in expected]:raise Refused('exact pinned activation launcher argv')
  env=(proc/'environ').read_bytes().split(b'\0')
  if ('XDG_RUNTIME_DIR='+str(self.runtime)).encode() not in env or ('DBUS_SESSION_BUS_ADDRESS=unix:path='+str(self.runtime/'bus')+',guid='+self.busguid).encode() not in env:raise Refused('exact private activation environment')
  if rows[0]['descriptor']!=record['descriptor'] or rows[0]['descriptorSHA256']!=record['descriptorSHA256'] or rows[0]['argv']!=record['argv']:raise Refused('activation descriptor correlation')
  return wrapper
 def authenticate(self,name,deadline):
  owner=self.call('GetNameOwner',(name,),'(s)',deadline)[0];pid=self.call('GetConnectionUnixProcessID',(owner,),'(s)',deadline)[0];uid=self.call('GetConnectionUnixUser',(owner,),'(s)',deadline)[0]
  if uid!=os.getuid() or self.call('GetNameOwner',(name,),'(s)',deadline)[0]!=owner:raise Refused('service owner replaced')
  matches=[]
  for record,path,rows in self.snapshots():
   if record['name']!=name:continue
   wrapper=self.verify_wrapper(record,rows)
   for row in rows:
    if row['kind']=='owned-child' and row['identity']['pid']==pid and live(row['identity']):matches.append((path,row['identity']))
  if len(matches)!=1:raise Refused('unique authenticated actual service process')
  return {'name':name,'owner':owner,'identity':matches[0][1],'journal':str(matches[0][0])}
 def close(self,deadline):
  snapshots=self.snapshots()
  for record,_,rows in snapshots:
   wrapper=rows[0]['identity']
   if live(wrapper):
    wrapper=self.verify_wrapper(record,rows)
    os.kill(wrapper['pid'],signal.SIGTERM)
  while True:
   snapshots=self.snapshots();pending=[]
   for _,path,rows in snapshots:
    if rows[-1]['kind']!='terminal' or live(rows[0]['identity']):pending.append(path)
   if not pending:break
   if time.monotonic()>=deadline:raise Refused('original activation cleanup deadline')
   time.sleep(.01)
  result=[{'journal':str(path),'terminal':rows[-1]} for _,path,rows in snapshots]
  if any(row['terminal']['error'] is not None or row['terminal']['liveDescendants'] for row in result):raise Refused('activation failure preserved')
  if self.connection:self.connection.close_sync(None)
  (self.output/'activation-cleanup.json').write_text(json.dumps(result,indent=2)+'\n');return result
