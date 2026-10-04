"""Private activation overlay; installation and desktop bus stay untouched."""
import configparser,hashlib,json,os,shlex,signal,socket,struct,time,threading,math,stat
from pathlib import Path
from xml.sax.saxutils import escape
from gi.repository import Gio,GLib
from activation_import import identity,live
from journal import pairs,constant
class Refused(RuntimeError):pass

def bounded_gio(fn,deadline):
 left=deadline-time.monotonic()
 if left<=0:raise Refused('original private bus deadline')
 cancellable=Gio.Cancellable();timer=threading.Timer(min(3,left),cancellable.cancel);timer.start()
 try:
  result=fn(cancellable)
  if time.monotonic()>=deadline:raise Refused('original private bus deadline')
  return result
 except GLib.Error as error:raise Refused('bounded private bus transport: '+str(error)) from error
 finally:timer.cancel();timer.join()

def strict_json(raw):
 try:return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=constant)
 except (ValueError,UnicodeError,RecursionError) as error:raise Refused('strict activation journal JSON') from error

def validate_identity(row):
 if type(row)!=dict or set(row)!={'pid','start','pgid','ppid','uid'}:raise Refused('closed activation identity')
 for field in ('pid','pgid','ppid','uid'):
  if type(row[field])!=int or not 0<=row[field]<=2147483647 or (field in ('pid','pgid') and row[field]==0):raise Refused('canonical activation identity integer')
 if row['uid']!=os.getuid() or type(row['start'])!=str or not row['start'].isascii() or not row['start'].isdigit() or row['start'].startswith('0') or len(row['start'])>20:raise Refused('canonical activation start/UID')

def journal_bytes(path):
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
 with os.fdopen(fd,'rb') as stream:
  before=os.fstat(stream.fileno())
  if not stat.S_ISREG(before.st_mode) or before.st_uid!=os.getuid() or before.st_size>1024*1024:raise Refused('bounded owned regular journal')
  raw=stream.read(1024*1024+1);after=os.fstat(stream.fileno())
  if len(raw)>1024*1024 or after.st_size>1024*1024:raise Refused('activation journal exceeded bounded prefix')
  return raw

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
  self.connection=bounded_gio(lambda c:Gio.DBusConnection.new_for_address_sync('unix:path='+str(path),Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,c),deadline)
  self.busrow=busrow
  self.busguid=self.connection.get_guid()
  if type(self.busguid)!=str or len(self.busguid)!=32 or any(c not in '0123456789abcdef' for c in self.busguid):raise Refused('private bus GUID')
 def call(self,member,args,signature,deadline):
  left=deadline-time.monotonic()
  if left<=0 or not live(self.busrow):raise Refused('original private bus deadline/identity')
  result=bounded_gio(lambda c:self.connection.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus',member,GLib.Variant(signature,args),None,Gio.DBusCallFlags.NONE,max(1,int(min(3,left)*1000)),c),deadline).unpack()
  if time.monotonic()>=deadline:raise Refused('original private bus deadline')
  return result
 def snapshots(self):
  found=[];self.snapshotRaw={}
  for record in self.records:
   for path in sorted(Path(record['journalDirectory']).glob('*.jsonl')):
    raw=journal_bytes(path);self.snapshotRaw[str(path)]=raw
    lines=raw.split(b'\n')
    if lines[-1]:
     try:tail=strict_json(lines[-1])
     except Refused:tail=None
     if type(tail)==dict and tail.get('kind')=='terminal':raise Refused('terminal journal requires newline completion')
    if any(not x for x in lines[:-1]):raise Refused('blank activation journal record')
    rows=[strict_json(x) for x in lines[:-1]]
    if not rows or type(rows[0])!=dict or rows[0].get('kind')!='supervisor-start':raise Refused('activation journal header')
    for index,row in enumerate(rows,1):
     if type(row)!=dict or type(row.get('sequence'))!=int or row['sequence']!=index or type(row.get('monotonic')) not in (int,float) or abs(row['monotonic'])>1e12 or not math.isfinite(row['monotonic']):raise Refused('canonical activation journal sequence/time')
     kind=row.get('kind')
     shapes={'supervisor-start':{'identity','argv','descriptor','descriptorSHA256'},'owned-child':{'identity'},'child-exit':{'identity','waitStatus','exitCode'},'shutdown-request':set(),'signal':{'identity','signal'},'supervisor-failure':{'error'},'unobserved-child-exit':{'pid','status'},'terminal':{'childExitCode','cancelled','fallback','allWaitStatuses','liveDescendants','error'}}
     if kind not in shapes or set(row)!={'sequence','kind','monotonic'}|shapes[kind]:raise Refused('closed activation journal event')
     if kind=='supervisor-start' and (row['argv']!=record['argv'] or row['descriptor']!=record['descriptor'] or row['descriptorSHA256']!=record['descriptorSHA256']):raise Refused('journal pinned descriptor')
     for field in ('waitStatus','exitCode','signal','pid','status'):
      if field in row and (type(row[field])!=int or not -64<=row[field]<=4294967295):raise Refused('canonical journal integer')
     if kind=='child-exit':
      try:code=os.waitstatus_to_exitcode(row['waitStatus'])
      except ValueError as error:raise Refused('invalid actual wait status') from error
      if code!=row['exitCode']:raise Refused('actual wait-status consistency')
     if kind=='signal' and row['signal'] not in (signal.SIGTERM,signal.SIGKILL):raise Refused('closed cancellation signal')
     if 'identity' in row:validate_identity(row['identity'])
     if kind=='terminal':
      if row['error'] is not None and (type(row['error'])!=str or len(row['error'])>4096):raise Refused('typed terminal error')
      if index!=len(rows) or lines[-1] or type(row.get('cancelled'))!=bool or type(row.get('fallback'))!=bool or type(row.get('liveDescendants'))!=list or type(row.get('allWaitStatuses'))!=list or type(row.get('childExitCode')) not in (int,type(None)):raise Refused('complete canonical terminal journal')
      for item in row['allWaitStatuses']:
       if type(item)!=dict or set(item)!={'identity','exitCode'} or type(item['exitCode'])!=int:raise Refused('actual wait status journal')
       validate_identity(item['identity'])
      for item in row['liveDescendants']:validate_identity(item)
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
   if record['name']!=name or not live(rows[0]['identity']):continue
   wrapper=self.verify_wrapper(record,rows)
   for row in rows:
    if row['kind']=='owned-child' and row['identity']['pid']==pid and live(row['identity']):matches.append((path,row['identity']))
  if len(matches)!=1:raise Refused('unique authenticated actual service process')
  return {'name':name,'owner':owner,'identity':matches[0][1],'journal':str(matches[0][0])}
 def close(self,deadline):
  signalled=set();authenticated=[];quiet=None
  while True:
   if time.monotonic()>=deadline:raise Refused('original activation cleanup deadline')
   snapshots=self.snapshots();pending=[]
   for record,path,rows in snapshots:
    wrapper=rows[0]['identity'];key=(wrapper['pid'],wrapper['start'])
    if live(wrapper) and key not in signalled:
     wrapper=self.verify_wrapper(record,rows)
     if self.call('NameHasOwner',(record['name'],),'(s)',deadline)[0] is True:authenticated.append(self.authenticate(record['name'],deadline))
     os.kill(wrapper['pid'],signal.SIGTERM);signalled.add(key)
    if rows[-1]['kind']!='terminal' or live(wrapper):pending.append(str(path))
   state=tuple(str(path) for _,path,_ in snapshots)
   if not pending:
    if quiet==state:break
    quiet=state
   else:quiet=None
   # Iterate discovery; a late activation remains visible to inherited census too.
   time.sleep(min(.01,max(0,deadline-time.monotonic())))
  result=[{'journal':str(path),'terminal':rows[-1]} for _,path,rows in snapshots]
  (self.output/'activation-authenticated.json').write_text(json.dumps(authenticated,indent=2)+'\n')
  (self.output/'activation-cleanup.json').write_text(json.dumps(result,indent=2)+'\n')
  for row in result:
   terminal=row['terminal'];codes=[item['exitCode'] for item in terminal['allWaitStatuses']]
   if terminal['error'] is not None or terminal['liveDescendants'] or terminal['fallback'] is True or type(terminal['childExitCode'])!=int or not codes or terminal['childExitCode'] not in (0,-15) or any(code not in (0,-15) for code in codes):raise Refused('activation fallback/nonzero/unproven cleanup preserved')
  if self.connection:
   bounded_gio(lambda c:self.connection.close_sync(c),deadline);self.connection=None
  (self.output/'activation-cleanup.json').write_text(json.dumps(result,indent=2)+'\n');return result

 def final_after_retirement(self,busrow):
  report={'passed':False,'busIdentity':busrow,'records':[]}
  try:
   validate_identity(busrow)
   if live(busrow):raise Refused('private bus must retire before final activation proof')
   if not hasattr(self,'busrow') or any(busrow[k]!=self.busrow[k] for k in ('pid','start','uid')):raise Refused('exact recorded bus identity')
   snapshots=self.snapshots()
   for record,path,rows in snapshots:
    wrapper=rows[0]['identity'];terminal=rows[-1]
    captured=self.snapshotRaw[str(path)]
    if journal_bytes(path)!=captured:raise Refused('journal changed after bounded parsed snapshot')
    saved={'journal':str(path),'sha256':hashlib.sha256(captured).hexdigest(),'wrapper':wrapper,'terminal':terminal};report['records'].append(saved)
    if terminal['kind']!='terminal' or live(wrapper):raise Refused('complete retired activation wrapper')
    owned={};exited={}
    for row in rows:
     if row['kind']=='owned-child':
      key=(row['identity']['pid'],row['identity']['start'])
      if key in owned:raise Refused('duplicate owned activation child')
      owned[key]=row['identity']
     if row['kind']=='child-exit':
      key=(row['identity']['pid'],row['identity']['start'])
      if key in exited or owned.get(key)!=row['identity']:raise Refused('actual unique owned child wait status')
      exited[key]=row['exitCode']
    declared={}
    for item in terminal['allWaitStatuses']:
     key=(item['identity']['pid'],item['identity']['start'])
     if key in declared or owned.get(key)!=item['identity']:raise Refused('terminal actual owned status identity')
     declared[key]=item['exitCode']
    if not owned or set(owned)!=set(exited) or declared!=exited or any(live(child) for child in owned.values()):raise Refused('every owned child actually reaped and retired')
    if terminal['childExitCode']!=exited[next(iter(owned))]:raise Refused('primary actual child wait status')
    if terminal['error'] is not None or terminal['fallback'] or terminal['liveDescendants'] or terminal['childExitCode'] not in (0,-15) or any(code not in (0,-15) for code in exited.values()):raise Refused('no fallback/nonzero/unproven final cleanup')
    saved['exitClasses']={str(pid)+':'+start:('normal' if code==0 else 'SIGTERM-cancellation') for (pid,start),code in exited.items()}
   report['passed']=True;return report
  except BaseException as error:report['error']=repr(error);raise
  finally:(self.output/'activation-post-retirement.json').write_text(json.dumps(report,indent=2)+'\n')
