"""Bounded native notification lifecycle inside the existing authority process.

Gio owns the session-bus connection on one GLib context/thread. Its observations
wake the broker's existing selector; no listener/automation daemon is introduced.
Elm selects an exact producer/service/id/incarnation, never a shell command.
"""
import copy, math, secrets, socket, threading, time
from endpoint import Refused, binding, canonical, exact

NAME = 'org.freedesktop.Notifications'
PATH = '/org/freedesktop/Notifications'
XML = '''<node><interface name="org.freedesktop.Notifications">
<method name="GetCapabilities"><arg type="as" direction="out"/></method>
<method name="GetServerInformation"><arg type="s" direction="out"/><arg type="s" direction="out"/><arg type="s" direction="out"/><arg type="s" direction="out"/></method>
<method name="Notify"><arg type="s" direction="in"/><arg type="u" direction="in"/><arg type="s" direction="in"/><arg type="s" direction="in"/><arg type="s" direction="in"/><arg type="as" direction="in"/><arg type="a{sv}" direction="in"/><arg type="i" direction="in"/><arg type="u" direction="out"/></method>
<method name="CloseNotification"><arg type="u" direction="in"/></method>
<signal name="ActionInvoked"><arg type="u"/><arg type="s"/></signal>
<signal name="NotificationClosed"><arg type="u"/><arg type="u"/></signal>
</interface></node>'''

def text(value, maximum, empty=True):
 if not isinstance(value,str) or len(value.encode("utf-8"))>maximum or (not empty and not value) or any(ord(c)<32 and c not in '\n\t' for c in value):raise Refused('Notification text')
 return value

class Service:
 def __init__(self):
  self.lock=threading.RLock();self.wake,self.writer=socket.socketpair()
  self.wake.setblocking(False);self.writer.setblocking(False)
  self.service=str(secrets.randbelow(2**64-1)+1);self.revision=1;self.serial=0;self.next_id=0
  self.rows=[];self.available=False;self.reason='Notification service unavailable.'
  self.connection=None;self.loop=None;self.context=None;self.expiry_source=None;self.stopping=False
  self.last_binding=None;self.last_effect=0;self.ready=threading.Event()
  self.thread=threading.Thread(target=self._run,name='warlock-notifications',daemon=True);self.thread.start()
  if not self.ready.wait(3):self.reason='Notification connection did not become ready.'
 def __enter__(self):return self
 def __exit__(self,*_):
  self.stopping=True
  if self.loop:self.loop.quit()
  if self.context:self.context.wakeup()
  self.thread.join(3)
  self.wake.close();self.writer.close()
 def changed(self):
  if self.revision>=2**64-1:
   self.available=False;self.reason='Notification identity exhausted.'
   for row in self.rows:row['state']='unavailable';row['actions']=[]
  else:self.revision+=1
  try:self.writer.send(b'1')
  except (BlockingIOError,OSError):pass
 def drain(self):
  try:
   while self.wake.recv(4096):pass
  except BlockingIOError:pass
 def snapshot(self):
  with self.lock:
   self.expire()
   return {'service':self.service,'revision':str(self.revision),'available':self.available,'reason':self.reason,
           'entries':[{k:copy.deepcopy(v) for k,v in row.items() if k!='deadline'} for row in reversed(self.rows)]}
 def emit(self,row,signal,signature,values):
  from gi.repository import GLib
  # A unique bus name cannot transfer to a different producer. Signals are
  # destination-bound; a numeric notification ID alone is never authority.
  if not self.connection or not self.connection.emit_signal(row['producer'],PATH,NAME,signal,GLib.Variant(signature,values)):raise Refused('Notification signal not queued')
 def close(self,row,state,reason,signal=True):
  row['state']=state;row['actions']=[];row['deadline']=None
  self.changed() # invalidate all action targets before any native signal
  self.schedule_expiry()
  if signal:
   try:self.emit(row,'NotificationClosed','(uu)',(int(row['id']),reason))
   except Exception:pass # already withdrawn; never repeat an effect
 def expire(self):
  now=time.monotonic()
  for row in self.rows:
   if row['state']=='live' and row['deadline'] is not None and now>=row['deadline']:self.close(row,'expired',1)
 def notify(self,sender,app,replaces,icon,summary,body,actions,hints,timeout):
  with self.lock:
   self.expire()
   text(app,128);text(summary,256);text(body,1024);text(icon,1024)
   if len(actions)>16 or len(actions)%2 or timeout < -1:raise Refused('Notification bounds')
   pairs=[]
   for index in range(0,len(actions),2):
    key=text(actions[index],64,False);label=text(actions[index+1],128,False)
    if any(p['key']==key for p in pairs):raise Refused('Duplicate notification action')
    pairs.append({'key':key,'label':label})
   if not isinstance(sender,str) or not sender.startswith(':'):raise Refused('Notification producer')
   previous=next((r for r in self.rows if int(r['id'])==replaces),None) if replaces else None
   if previous is not None and previous['producer']!=sender:raise Refused('Foreign notification replacement')
   if not self.available or self.serial>=2**64-1:raise Refused('Notification service unavailable')
   if previous is None:
    if len(self.rows)>=32:
     retired=next((r for r in self.rows if r['state']!='live'),None)
     if retired is None:raise Refused('Notification capacity')
     self.rows.remove(retired)
    # IDs are monotonic until UINT32 exhaustion; incarnation still protects
    # replacement/reuse and the service token protects whole-host restart.
    if self.next_id>=2**32-1:raise Refused('Notification ID exhausted')
    self.next_id+=1;identifier=self.next_id
   else:
    identifier=replaces;self.rows.remove(previous)
   self.serial+=1
   urgency=hints.get('urgency',1) if type(hints.get('urgency',1)) is int and hints.get('urgency',1) in (0,1,2) else 1
   duration=5000 if timeout==-1 else timeout
   self.rows.append({'id':str(identifier),'incarnation':str(self.serial),'producer':sender,'app':app or 'Application',
                     'summary':summary,'body':body,'state':'live','actions':pairs,
                     'urgency':urgency,
                     'deadline':None if urgency==2 or duration==0 else time.monotonic()+duration/1000})
   self.changed();self.schedule_expiry();return identifier
 def effect(self,request,client):
  exact(request,['protocolVersion','kind','binding','requestId','intent'])
  canonical(request['requestId']);scope=binding(request['binding'])
  if request['requestId']=='0':raise Refused('Notification request identity')
  if type(request['protocolVersion']) is not int or request['protocolVersion']!=3 or scope!=client.bound:raise Refused('Notification binding')
  client.verify_process();client.verify_paths()
  intent=request['intent'];exact(intent,['service','id','incarnation','producer','action','verb'])
  for key in ['service','id','incarnation']:
   canonical(intent[key])
   if intent[key]=='0':raise Refused('Notification zero identity')
  if int(intent['id'])>2**32-1:raise Refused('Notification ID bound')
  text(intent['producer'],128,False);text(intent['action'],64)
  if intent['verb'] not in ('invoke','dismiss') or (intent['verb']=='dismiss' and intent['action']!=''):raise Refused('Notification verb')
  with self.lock:
   self.expire()
   if scope!=self.last_binding:self.last_binding=scope;self.last_effect=0
   number=int(request['requestId']);status='Refused'
   if number>self.last_effect:
    self.last_effect=number
    row=next((r for r in self.rows if r['id']==intent['id'] and r['incarnation']==intent['incarnation'] and r['producer']==intent['producer']),None)
    valid=self.available and intent['service']==self.service and row is not None and row['state']=='live'
    valid=valid and (intent['verb']=='dismiss' or any(p['key']==intent['action'] for p in row['actions']))
    if valid:
     from gi.repository import GLib
     try:
      present=self.connection.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','NameHasOwner',GLib.Variant('(s)',(row['producer'],)),GLib.VariantType.new('(b)'),0,1000,None).unpack()[0]
      if not present:self.close(row,'disconnected',4,False)
      elif intent['verb']=='dismiss':self.close(row,'dismissed',2);status='Dispatched'
      else:
       # Consume before emission. Any signal/receipt uncertainty is terminal
       # for this incarnation and must never become an automatic retry.
       row['state']='invoked';row['actions']=[];row['deadline']=None;self.changed();self.schedule_expiry()
       self.emit(row,'ActionInvoked','(us)',(int(row['id']),intent['action']));status='Dispatched'
     except Exception:
      if row['state']!='live':row['state']='unknown';status='Unknown';self.changed()
   client.verify_process();client.verify_paths()
   return {'protocolVersion':3,'kind':'notification-outcome','binding':scope,'requestId':request['requestId'],
           'status':status,'snapshot':self.snapshot()}
 def read(self,request,client):
  exact(request,['protocolVersion','kind','binding','requestId']);canonical(request['requestId'])
  if request['requestId']=='0':raise Refused('Notification request identity')
  if type(request['protocolVersion']) is not int or request['protocolVersion']!=3 or binding(request['binding'])!=client.bound:raise Refused('Notification binding')
  client.verify_process();client.verify_paths()
  return {'protocolVersion':3,'kind':'notification-snapshot','binding':client.bound,'requestId':request['requestId'],'snapshot':self.snapshot()}
 def observation(self,client):
  client.verify_process();client.verify_paths()
  return {'protocolVersion':3,'kind':'notification-update','binding':client.bound,'snapshot':self.snapshot()}
 def _method(self,connection,sender,path,interface,method,parameters,invocation):
  from gi.repository import GLib
  try:
   if method=='GetCapabilities':result=GLib.Variant('(as)',(['actions','body'],))
   elif method=='GetServerInformation':result=GLib.Variant('(ssss)',('Warlock','Warlock contributors','1','1.3'))
   elif method=='Notify':
    args=list(parameters.unpack());hints=dict(args[6])
    urgency=parameters.get_child_value(6).lookup_value('urgency',None)
    # Only the standard BYTE hint can elevate urgency. Malformed hints remain
    # ordinary; producers never choose DND or interruption permission.
    if urgency is not None and urgency.get_type_string()!='y':hints.pop('urgency',None)
    args[6]=hints;result=GLib.Variant('(u)',(self.notify(sender,*args),))
   elif method=='CloseNotification':
    with self.lock:
     self.expire();identifier=parameters.unpack()[0]
     row=next((r for r in self.rows if int(r['id'])==identifier and r['state']=='live' and r['producer']==sender),None)
     if row is None:raise Refused('Notification no longer exists or producer mismatch')
     self.close(row,'closed',3)
    result=GLib.Variant('()',())
   else:raise Refused('Notification method')
   invocation.return_value(result)
  except Exception as error:invocation.return_dbus_error('org.freedesktop.Notifications.Error.Invalid',str(error) if isinstance(error,Refused) else 'Notification request unavailable')
 def _owners(self,connection,sender,path,interface,signal,parameters,*_):
  name,old,new=parameters.unpack()
  if name.startswith(':') and old and not new:
   with self.lock:
    for row in self.rows:
     if row['producer']==name and row['state']=='live':self.close(row,'disconnected',4,False)
 def schedule_expiry(self):
  from gi.repository import GLib
  if self.expiry_source:self.expiry_source.destroy();self.expiry_source=None
  deadlines=[r['deadline'] for r in self.rows if r['state']=='live' and r['deadline'] is not None]
  if not deadlines or self.stopping:return
  self.expiry_source=GLib.timeout_source_new(max(1,math.ceil((min(deadlines)-time.monotonic())*1000)))
  self.expiry_source.set_callback(lambda *_:self._tick());self.expiry_source.attach(self.context)
 def _tick(self):
  with self.lock:
   self.expiry_source=None;self.expire();self.schedule_expiry()
  return False
 def _lost(self,*_):
  if self.stopping:return
  with self.lock:
   self.available=False;self.reason='Notification bus disconnected. No action will be repeated.'
   for row in self.rows:
    if row['state']=='live':self.close(row,'disconnected',4,False)
   self.changed()
 def _run(self):
  registered=None;subscription=None;acquired=False;source=None
  try:
   import gi
   gi.require_version('Gio','2.0');from gi.repository import Gio,GLib
   self.context=GLib.MainContext.new();self.context.push_thread_default()
   address=Gio.dbus_address_get_for_bus_sync(Gio.BusType.SESSION,None)
   self.connection=Gio.DBusConnection.new_for_address_sync(address,Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
   self.connection.set_exit_on_close(False);self.connection.connect('closed',self._lost)
   result=self.connection.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','RequestName',GLib.Variant('(su)',(NAME,4)),GLib.VariantType.new('(u)'),0,2000,None).unpack()[0]
   acquired=result==1
   if not acquired:
    self.reason='Another notification service is running. Warlock cannot read its private notifications.';self.ready.set();return
   registered=self.connection.register_object(PATH,Gio.DBusNodeInfo.new_for_xml(XML).interfaces[0],self._method,None,None)
   subscription=self.connection.signal_subscribe('org.freedesktop.DBus','org.freedesktop.DBus','NameOwnerChanged','/org/freedesktop/DBus',None,0,self._owners)
   self.loop=GLib.MainLoop.new(self.context,False)
   with self.lock:self.available=True;self.reason='';self.changed()
   self.ready.set()
   if not self.stopping:self.loop.run()
  except Exception:
   with self.lock:self.available=False;self.reason='Notification bus unavailable.';self.changed()
   self.ready.set()
  finally:
   if self.expiry_source:self.expiry_source.destroy()
   if self.connection:
    if subscription:self.connection.signal_unsubscribe(subscription)
    if registered:self.connection.unregister_object(registered)
    if acquired:
     try:self.connection.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','ReleaseName',GLib.Variant('(s)',(NAME,)),None,0,1000,None)
     except Exception:pass
    try:self.connection.close_sync(None)
    except Exception:pass
   if self.context:self.context.pop_thread_default()
