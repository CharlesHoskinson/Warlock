"""Actual native session-bus producers: exact unicast, expiry and reused IDs."""
import copy, json, os, pathlib, subprocess, sys, time
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from notification_service import Service, NAME, PATH
from endpoint import Refused
import gi
gi.require_version('Gio','2.0');from gi.repository import Gio,GLib
checks=[]
def check(name,value):
 assert value,name
 checks.append(name)
class Client:
 bound={'lifetime':'1','session':'1','frontend':'1'}
 def verify_process(self):pass
 def verify_paths(self):pass
def wait(fn):
 end=time.monotonic()+2
 while time.monotonic()<end:
  while GLib.MainContext.default().pending():GLib.MainContext.default().iteration(False)
  result=fn()
  if result:return result
  time.sleep(.005)
 raise AssertionError('Notification fixture deadline')
def producer(address):return Gio.DBusConnection.new_for_address_sync(address,Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
def notify(connection,label,replaces=0,timeout=0,hints=None):
 return connection.call_sync(NAME,PATH,NAME,'Notify',GLib.Variant('(susssasa{sv}i)',('Fixture',replaces,'',label,'Notification body',['open','Open item'],hints or {},timeout)),GLib.VariantType.new('(u)'),0,2000,None).unpack()[0]
def capture(service,identifier,verb='invoke'):
 snapshot=service.snapshot();row=next(r for r in snapshot['entries'] if r['id']==str(identifier))
 return {'service':snapshot['service'],'id':row['id'],'incarnation':row['incarnation'],'producer':row['producer'],'action':'open' if verb=='invoke' else '', 'verb':verb}
serial=10
def effect(service,intent):
 global serial
 serial+=1
 return service.effect({'protocolVersion':3,'kind':'notification-effect','binding':Client.bound,'requestId':str(serial),'intent':intent},Client())
bus=subprocess.Popen(['dbus-daemon','--session','--nofork','--print-address=1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
first=None;second=None
try:
 address=bus.stdout.readline().strip();assert address.startswith('unix:');os.environ['DBUS_SESSION_BUS_ADDRESS']=address
 first=producer(address);second=producer(address);signals=[[],[]]
 for index,connection in enumerate([first,second]):
  connection.signal_subscribe(None,NAME,None,PATH,None,0,lambda *args,index=index:signals[index].append((args[4],args[5].unpack())))
 with Service() as service:
  check('Private native bus acquired',service.available)
  a=notify(first,'First producer');b=notify(second,'Second producer');intent=capture(service,a)
  result=effect(service,intent);wait(lambda:signals[0]);check('Current producer gets exactly requested action',result['status']=='Dispatched' and signals[0]==[('ActionInvoked',(a,'open'))]);check('Other producer receives no action',signals[1]==[])
  check('Second invocation is refused',effect(service,intent)['status']=='Refused');check('Consumed incarnation has no action targets',next(r for r in service.snapshot()['entries'] if r['id']==str(a))['actions']==[])
  wait(lambda:len(service.snapshot()['entries'])==2)
  expiring=notify(first,'Expires while center is open',timeout=40);old=capture(service,expiring)
  wait(lambda:next(r for r in service.snapshot()['entries'] if r['id']==str(expiring))['state']=='expired')
  wait(lambda:any(name=='NotificationClosed' and value==(expiring,1) for name,value in signals[0]));before=copy.deepcopy(signals)
  check('Expiry removes all action targets',next(r for r in service.snapshot()['entries'] if r['id']==str(expiring))['actions']==[])
  expired_receipt=effect(service,old);check('Expired queued action refused',expired_receipt['status']=='Refused');check('Expired refusal has exact native reason',expired_receipt['reason']=='expired')
  reused=notify(first,'New native incarnation',replaces=expiring);new=capture(service,reused)
  check('Replaced numeric ID keeps new native incarnation',reused==expiring and new['incarnation']!=old['incarnation'])
  reused_receipt=effect(service,old);check('Old queued action rejected after ID reuse',reused_receipt['status']=='Refused');check('Replacement cannot erase exact expired-target fact',reused_receipt['reason']=='expired');check('Native expiry facts stay bounded',len(service.expired)<=64)
  check('Replacement and unrelated producer unaffected',signals==before and next(r for r in service.snapshot()['entries'] if r['id']==str(b))['state']=='live')
  check('New incarnation action dispatches',effect(service,new)['status']=='Dispatched');wait(lambda:any(name=='ActionInvoked' and value==(reused,'open') for name,value in signals[0]))
  check('Old and new each dispatch at most once',sum(name=='ActionInvoked' for name,value in signals[0])==2)
  victim=notify(second,'Foreign producer');foreign=capture(service,victim);foreign['producer']=first.get_unique_name();substitution=effect(service,foreign);check('Producer substitution is refused',substitution['status']=='Refused');check('Foreign producer never inherits expired-target reason',substitution['reason']!='expired')
  failed=False
  try:notify(first,'Foreign replacement',replaces=victim)
  except GLib.Error:failed=True
  check('Foreign producer cannot replace ID',failed)
  disappeared=capture(service,victim);second.close_sync(None);second=None
  wait(lambda:next(r for r in service.snapshot()['entries'] if r['id']==str(victim))['state']=='disconnected')
  check('Disconnected producer withdraws targets',effect(service,disappeared)['status']=='Refused')
  dismissal=notify(first,'Dismiss explicitly');check('Dismiss exact current incarnation',effect(service,capture(service,dismissal,'dismiss'))['status']=='Dispatched')
  wait(lambda:any(name=='NotificationClosed' and value==(dismissal,2) for name,value in signals[0]))
  with Service() as occupied:check('Existing service is preserved without replacement',not occupied.available and service.available)
  check('Original bus owner still answers after occupied probe',notify(first,'Still owned')>0)
  wrong={**capture(service,notify(first,'Old host token')),'service':'1'};check('Old service incarnation refused',effect(service,wrong)['status']=='Refused')
  from unittest.mock import patch
  uncertain=notify(first,'Uncertain native dispatch');uncertain_target=capture(service,uncertain)
  with patch.object(service,'emit',side_effect=Refused('Controlled signal delivery failure')):uncertain_result=effect(service,uncertain_target)
  check('Native delivery uncertainty is Unknown',uncertain_result['status']=='Unknown')
  check('Unknown target has no actions',next(r for r in service.snapshot()['entries'] if r['id']==str(uncertain))['state']=='unknown' and next(r for r in service.snapshot()['entries'] if r['id']==str(uncertain))['actions']==[])
  check('Unknown signal is never replayed',effect(service,uncertain_target)['status']=='Refused' and not any(name=='ActionInvoked' and value==(uncertain,'open') for name,value in signals[0]))
  check('Non-expiring entries do not poll an idle timer',service.expiry_source is None)
  bad={'protocolVersion':3,'kind':'notification-request','binding':Client.bound,'requestId':'1','path':'/tmp/foreign'}
  rejected=False
  try:service.read(bad,Client())
  except Refused:rejected=True
  check('Frontend path cannot select notification authority',rejected)
  for value in (0,1,2):
   identifier=notify(first,'Urgency '+str(value),hints={'urgency':GLib.Variant('y',value)})
   check('Native BYTE urgency retained '+str(value),next(row for row in service.snapshot()['entries'] if row['id']==str(identifier))['urgency']==value)
  critical=notify(first,'Critical retains attention until explicitly closed',timeout=40,hints={'urgency':GLib.Variant('y',2)})
  time.sleep(.06)
  check('Native critical notification never expires automatically',next(row for row in service.snapshot()['entries'] if row['id']==str(critical))['state']=='live')
  for hint in [GLib.Variant('s','critical'),GLib.Variant('i',2),GLib.Variant('b',True),GLib.Variant('y',255)]:
   identifier=notify(first,'Malformed urgency',hints={'urgency':hint})
   check('Malformed urgency cannot elevate '+hint.get_type_string()+str(hint.unpack()),next(row for row in service.snapshot()['entries'] if row['id']==str(identifier))['urgency']==1)

 # A second actual name owner fixture: read/observation/effect routes never
 # replace it. Only an authenticated explicit read retries a never-owned empty
 # service after the existing owner exits normally.
 read={'protocolVersion':3,'kind':'notification-request','binding':Client.bound,'requestId':'201'}
 external=Service()
 try:
  with Service() as recovering:
   recovering.thread.join(3)
   check('Occupied empty service remains unavailable',not recovering.available and recovering.serial==0 and not recovering.rows)
   old_thread=recovering.thread;identity=recovering.service
   recovering.observation(Client());check('Observation cannot retry occupied service',recovering.thread is old_thread)
   occupied_read=recovering.read(read,Client());recovering.thread.join(3)
   check('Explicit read preserves occupied owner',not occupied_read['snapshot']['available'] and external.available and notify(first,'Owner preserved through explicit read')>0)
   check('Retry cannot replay an action or alias producer identity',recovering.service==identity and recovering.serial==0 and recovering.last_effect==0 and not recovering.rows)
   # Release through the original context manager's normal shutdown protocol.
   external.__exit__(None,None,None)
   recovered=recovering.read({**read,'requestId':'202'},Client())
   check('Explicit read acquires released name',recovered['snapshot']['available'] and recovering.ever_owned and recovered['snapshot']['service']==identity)
   check('Recovery has no replayed entries or effects',recovered['snapshot']['entries']==[] and recovering.serial==0 and recovering.last_effect==0)
   live=notify(first,'Recovered native service')
   check('Recovered service serves actual native producer',live>0 and len(recovering.snapshot()['entries'])==1)
   recovering.connection.close_sync(None)
   wait(lambda:not recovering.available)
   recovering.thread.join(3);old_thread=recovering.thread
   recovery_after_loss=recovering.read({**read,'requestId':'203'},Client())
   check('Established service loss cannot restart producer custody',not recovery_after_loss['snapshot']['available'] and recovering.thread is old_thread and recovering.ever_owned)
 finally:
  if not external.stopping:external.__exit__(None,None,None)


finally:
 for connection in [first,second]:
  if connection:
   try:connection.close_sync(None)
   except GLib.Error:pass
 bus.terminate();bus.communicate(timeout=3)
print(json.dumps({'passed':True,'checks':checks,'scenarios':['ux-031','notification-valid','notification-reused'],'evidenceScope':'Actual private native D-Bus producers; no GUI/AT acceptance'}))
