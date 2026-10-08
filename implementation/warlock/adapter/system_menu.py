"""Capability observations and one-shot changes in the existing broker.

Native environment selects audio/bus endpoints. Frontend values select only a
typed operation and bounded value on the current service/revision, never paths,
commands, D-Bus destinations or session IDs. Native uncertainty never retries.
"""
import copy, json, os, pathlib, secrets, selectors, socket, stat, struct, subprocess, time, threading
from endpoint import Refused, binding, canonical, exact, start_time, unique

OPERATIONS={'volume-set','volume-mute','network-enable','suspend','reboot','poweroff','session-lock','session-logout'}
NM='org.freedesktop.NetworkManager';NM_PATH='/org/freedesktop/NetworkManager'
LOGIN='org.freedesktop.login1';LOGIN_PATH='/org/freedesktop/login1';MANAGER=LOGIN+'.Manager'

class Uncertain(RuntimeError):pass

def safe_text(value,limit=128):
 if not isinstance(value,str):raise Refused('Native system text')
 return ' '.join(value.split())[:limit]

def command(args,deadline):
 """Fixed executable/argv, bounded output and absolute native deadline."""
 if args[0]!='/usr/bin/pactl':raise Refused('Native audio executable')
 process=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={**os.environ,'LC_ALL':'C'},start_new_session=True)
 raw=bytearray();errors=bytearray()
 try:
  with selectors.DefaultSelector() as selector:
   for stream,label in [(process.stdout,'out'),(process.stderr,'error')]:os.set_blocking(stream.fileno(),False);selector.register(stream,selectors.EVENT_READ,label)
   while selector.get_map():
    left=deadline-time.monotonic()
    if left<=0:raise Uncertain('Native audio response not confirmed')
    for key,_ in selector.select(left):
     data=os.read(key.fileobj.fileno(),8192)
     if not data:selector.unregister(key.fileobj);continue
     target=raw if key.data=='out' else errors;target.extend(data)
     if len(target)>(262144 if key.data=='out' else 4096):raise Uncertain('Native audio response capacity')
  process.wait(timeout=max(.001,deadline-time.monotonic()))
  if process.returncode:raise Refused('Audio server refused request')
  return bytes(raw)
 finally:
  if process.poll() is None:process.terminate()
  try:process.wait(timeout=.3)
  except subprocess.TimeoutExpired:process.kill();process.wait()
  process.stdout.close();process.stderr.close()

class Menu:
 def __init__(self,system_address=None):
  self.service=str(secrets.randbelow(2**64-1)+1);self.revision=0;self.last=None;self.identity=None
  self.connection=None;self.system_address=system_address;self.spent=set();self.last_binding=None;self.last_request=0
  self.audio=None;self.network=None;self.login=None;self.session=None
 def __enter__(self):return self
 def __exit__(self,*_):
  if self.connection:
   try:self.connection.close_sync(None)
   except Exception:pass
 def remaining(self,deadline):
  left=deadline-time.monotonic()
  if left<=0:raise Uncertain('Native system response not confirmed')
  return max(1,min(1000,int(left*1000)))
 def bus(self,deadline):
  if self.connection and not self.connection.is_closed():return self.connection
  import gi
  gi.require_version('Gio','2.0');from gi.repository import Gio
  # A refusing QA system address remains refusing: no session/default fallback.
  address=self.system_address or os.environ.get('DBUS_SYSTEM_BUS_ADDRESS') or 'unix:path=/run/dbus/system_bus_socket'
  cancel=Gio.Cancellable();timer=threading.Timer(min(.5,max(.001,deadline-time.monotonic())),cancel.cancel);timer.start()
  try:self.connection=Gio.DBusConnection.new_for_address_sync(address,Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,cancel)
  finally:timer.cancel();timer.join()
  self.connection.set_exit_on_close(False);return self.connection
 def call(self,destination,path,interface,method,signature,values,reply,deadline,effect=False):
  from gi.repository import Gio,GLib
  flags=Gio.DBusCallFlags.NO_AUTO_START | (Gio.DBusCallFlags.ALLOW_INTERACTIVE_AUTHORIZATION if effect else Gio.DBusCallFlags.NONE)
  try:
   return self.bus(deadline).call_sync(destination,path,interface,method,GLib.Variant(signature,values),GLib.VariantType.new(reply),flags,self.remaining(deadline),None).unpack()
  except GLib.Error as error:
   name=Gio.DBusError.get_remote_error(error) or ''
   if any(name.endswith('.'+suffix) for suffix in ['AccessDenied','AuthFailed','ServiceUnknown','NameHasNoOwner','UnknownObject','UnknownMethod','NotSupported','PermissionDenied']):raise Refused('Native system operation unavailable or refused') from error
   raise Uncertain('Native system response not confirmed') from error
 def owner(self,name,deadline):return self.call('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','GetNameOwner','(s)',(name,),'(s)',deadline)[0]
 def properties(self,owner,path,interface,deadline):return self.call(owner,path,'org.freedesktop.DBus.Properties','GetAll','(s)',(interface,),'(a{sv})',deadline)[0]
 def audio_peer(self):
  selected=os.environ.get('PULSE_SERVER') or 'unix:'+str(pathlib.Path(os.environ.get('XDG_RUNTIME_DIR','/run/user/'+str(os.getuid())))/'pulse/native')
  if not selected.startswith('unix:') or ';' in selected:raise Refused('Local audio endpoint unavailable')
  path=pathlib.Path(selected[5:])
  if not path.is_absolute() or path.resolve()!=path:raise Refused('Native audio endpoint ancestry')
  before=path.lstat()
  if not stat.S_ISSOCK(before.st_mode) or before.st_uid!=os.getuid():raise Refused('Native audio endpoint ownership')
  with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as stream:
   stream.settimeout(.2);stream.connect(str(path));pid,uid,_=struct.unpack('3i',stream.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
  after=path.lstat()
  if uid!=os.getuid() or (before.st_dev,before.st_ino)!=(after.st_dev,after.st_ino):raise Refused('Native audio endpoint changed')
  return {'server':selected,'pid':pid,'start':start_time(pid),'device':after.st_dev,'inode':after.st_ino}
 def audio_read(self,deadline):
  peer=self.audio_peer();args=['/usr/bin/pactl','--server='+peer['server'],'--format=json']
  info=json.loads(command(args+['info'],deadline),object_pairs_hook=unique);rows=json.loads(command(args+['list','sinks'],deadline),object_pairs_hook=unique)
  if not isinstance(rows,list) or len(rows)>128:raise Refused('Native audio sink capacity')
  row=next((r for r in rows if r.get('name')==info.get('default_sink_name')),None)
  if not row or type(row.get('mute')) is not bool or type(row.get('index')) is not int or not 0<=row['index']<2**32:raise Refused('Native audio default sink unavailable')
  volumes=row.get('volume');values=[item.get('value') for item in volumes.values()] if isinstance(volumes,dict) else []
  if not values or len(values)>32 or any(type(v) is not int or not 0<=v<=65536*16 for v in values):raise Refused('Native audio volume unavailable')
  if self.audio_peer()!=peer:raise Refused('Native audio peer changed')
  self.audio={**peer,'index':row['index'],'name':row['name'],'raw':values}
  return {'percent':round(max(values)*100/65536),'muted':row['mute'],'label':safe_text(row.get('description') or row['name'])}
 def observe(self,deadline=None):
  deadline=deadline or time.monotonic()+2
  result={'volume':None,'network':None,'power':None,'session':None};identities={}
  self.audio=None;self.network=None;self.login=None;self.session=None
  try:result['volume']=self.audio_read(deadline);identities['audio']=self.audio
  except (OSError,ValueError,Refused,Uncertain):pass
  try:
   owner=self.owner(NM,deadline);props=self.properties(owner,NM_PATH,NM,deadline)
   permissions=self.call(owner,NM_PATH,NM,'GetPermissions','()',(),'(a{ss})',deadline)[0]
   enabled=props.get('NetworkingEnabled');state=props.get('State')
   if type(enabled) is not bool or type(state) is not int:raise Refused('Native network state')
   access=permissions.get('org.freedesktop.NetworkManager.enable-disable-network','no')
   if access not in ('yes','no','auth'):access='no'
   self.network=owner;identities['network']=owner
   result['network']={'enabled':enabled,'state':{0:'Unknown',10:'Sleeping',20:'Disconnected',30:'Disconnecting',40:'Connecting',50:'Local connection',60:'Site connection',70:'Connected'}.get(state,'Unknown'),'permission':access}
  except Exception:pass
  try:
   owner=self.owner(LOGIN,deadline);caps={}
   for key,method in [('suspend','CanSuspend'),('reboot','CanReboot'),('poweroff','CanPowerOff')]:
    value=self.call(owner,LOGIN_PATH,MANAGER,method,'()',(),'(s)',deadline)[0]
    if value not in ('yes','no','na','challenge'):raise Refused('Native power capability')
    caps[key]=value
   self.login=owner;identities['login']=owner;result['power']=caps
   path=self.call(owner,LOGIN_PATH,MANAGER,'GetSessionByPID','(u)',(os.getpid(),),'(o)',deadline)[0]
   props=self.properties(owner,path,LOGIN+'.Session',deadline)
   identifier=props.get('Id');name=props.get('Name');state=props.get('State');locked=props.get('LockedHint');user=props.get('User')
   if not isinstance(identifier,str) or not identifier or not isinstance(user,tuple) or user[0]!=os.getuid() or type(locked) is not bool:raise Refused('Native session identity')
   self.session={'owner':owner,'path':path,'id':identifier};identities['session']=self.session
   result['session']={'name':safe_text(name),'state':safe_text(state,32),'locked':locked}
  except Exception:pass
  if result!=self.last or identities!=self.identity:
   if self.revision>=2**64-1:raise Refused('Native system revision exhausted')
   self.revision+=1;self.last=copy.deepcopy(result);self.identity=copy.deepcopy(identities)
   self.spent={key for key in self.spent if key[0]>=self.revision-32}
  return {'service':self.service,'revision':str(self.revision),**result}
 def verify(self,request,client,write):
  exact(request,['protocolVersion','kind','binding','requestId',*(['intent'] if write else [])]);canonical(request['requestId'])
  if request['kind']!=('system-menu-effect' if write else 'system-menu-request'):raise Refused('Native system request kind')
  if type(request['protocolVersion']) is not int or request['protocolVersion']!=3 or binding(request['binding'])!=client.bound:raise Refused('Native system binding')
  client.verify_process();client.verify_paths()
 def read(self,request,client):
  self.verify(request,client,False);snapshot=self.observe();self.verify(request,client,False)
  return {'protocolVersion':3,'kind':'system-menu-snapshot','binding':client.bound,'requestId':request['requestId'],'snapshot':snapshot}
 def available(self,operation,value,current):
  if operation=='volume-set':return current['volume'] is not None and current['volume']['percent']!=value
  if operation=='volume-mute':return current['volume'] is not None and current['volume']['muted']!=(value==1)
  if operation=='network-enable':return current['network'] is not None and current['network']['permission'] in ('yes','auth') and current['network']['enabled']!=(value==1)
  if operation in ('suspend','reboot','poweroff'):return current['power'] is not None and current['power'][operation] in ('yes','challenge')
  if operation=='session-lock':return current['session'] is not None and not current['session']['locked']
  if operation=='session-logout':return current['session'] is not None and current['session']['state']!='closing'
  return False
 def effect(self,request,client):
  self.verify(request,client,True);intent=request['intent'];exact(intent,['service','revision','operation','value'])
  canonical(intent['service']);canonical(intent['revision']);operation=intent['operation'];value=intent['value']
  if operation not in OPERATIONS or type(value) is not int or not 0<=value<=100 or (operation in ('volume-mute','network-enable') and value not in (0,1)) or (operation not in ('volume-set','volume-mute','network-enable') and value!=0):raise Refused('Native system operation/value')
  deadline=time.monotonic()+3;current=self.observe(deadline);scope=client.bound
  if scope!=self.last_binding:self.last_binding=copy.deepcopy(scope);self.last_request=0
  number=int(request['requestId']);key=(int(intent['revision']),operation,value);status='Refused'
  if number>self.last_request:
   self.last_request=number
   if intent['service']==self.service and intent['revision']==current['revision'] and key not in self.spent and self.available(operation,value,current):
    self.spent.add(key)
    try:
     if operation.startswith('volume-'):
      if self.audio_peer()!={k:v for k,v in self.audio.items() if k not in ('index','name','raw')}:raise Refused('Audio peer changed before submission')
      audio=copy.deepcopy(self.audio);args=['/usr/bin/pactl','--server='+audio['server']]
      command(args+(['set-sink-volume',str(audio['index']),str(value)+'%'] if operation=='volume-set' else ['set-sink-mute',str(audio['index']),str(value)]),deadline)
      readback=self.audio_read(deadline)
      if self.audio['pid']!=audio['pid'] or self.audio['start']!=audio['start'] or self.audio['index']!=audio['index'] or self.audio['name']!=audio['name']:raise Uncertain('Audio target changed after submission')
      if (readback['percent']==value if operation=='volume-set' else readback['muted']==(value==1)):status='Committed'
      else:raise Uncertain('Audio change not observed')
     elif operation=='network-enable':
      owner=self.network;self.call(owner,NM_PATH,NM,'Enable','(b)',(value==1,),'()',deadline,True)
      props=self.properties(owner,NM_PATH,NM,deadline)
      if self.owner(NM,deadline)==owner and props.get('NetworkingEnabled')==(value==1):status='Committed'
      else:raise Uncertain('Network change not observed')
     elif operation=='session-lock':
      session=copy.deepcopy(self.session);self.call(session['owner'],session['path'],LOGIN+'.Session','Lock','()',(),'()',deadline,True)
      props=self.properties(session['owner'],session['path'],LOGIN+'.Session',deadline)
      status='Committed' if props.get('LockedHint') is True else 'Submitted'
     elif operation=='session-logout':self.call(self.session['owner'],LOGIN_PATH,MANAGER,'TerminateSession','(s)',(self.session['id'],),'()',deadline,True);status='Submitted'
     else:
      method={'suspend':'Suspend','reboot':'Reboot','poweroff':'PowerOff'}[operation]
      self.call(self.login,LOGIN_PATH,MANAGER,method,'(b)',(True,),'()',deadline,True);status='Submitted'
    except Refused:status='Refused'
    except Exception:status='Unknown'
  try:snapshot=self.observe(deadline)
  except Exception:snapshot=current;status='Unknown' if status in ('Committed','Submitted') else status
  self.verify(request,client,True)
  return {'protocolVersion':3,'kind':'system-menu-outcome','binding':client.bound,'requestId':request['requestId'],'status':status,'snapshot':snapshot}
