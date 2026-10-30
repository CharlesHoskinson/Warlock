"""Actual candidate main selection/unwind with real store and inert service doubles."""
from coordinator_fixture import *
import builtins,importlib.util
spec=importlib.util.spec_from_file_location('candidate_daemon',ROOT/'adapter/daemon.py');daemon=importlib.util.module_from_spec(spec);spec.loader.exec_module(daemon)
class StopAtPublish(Exception):pass
class Context:
 def __enter__(self):return self
 def __exit__(self,*args):pass
class Catalog:
 def __init__(self,client,roots):self.authority=object()
class DaemonNative(Native):
 def request(self,payload):
  if payload['kind']=='workspace-navigation-attach':
   self.calls.append(copy.deepcopy(payload));return {'protocolVersion':3,'kind':'workspace-navigation-attached','workspaceProtocol':1,'binding':copy.deepcopy(self.bound),'existingEmptyOnly':True,'historyCapacity':64}
  return super().request(payload)
for mode in ['omitted',False,True,'output-failure',0,1,None,'true',[],{}]:
 with tempfile.TemporaryDirectory(prefix='warlock-coordinator-main-') as temporary:
  config={'runtime':temporary,'instance':'coordinatorqa'}
  if mode!='omitted':config['cancellationOptIn']=True if mode=='output-failure' else mode
  path=pathlib.Path(temporary)/'config.json';path.write_text(json.dumps(config))
  events=[];depth=[0];native=DaemonNative(events,depth);constructs=[];stores=[];imports=[]
  enabled=mode is True or mode=='output-failure'
  class Store(RecoveryStore):
   def __init__(self,*args,**kwargs):
    constructs.append(kwargs.copy());super().__init__(*args,**kwargs);stores.append(self)
   def cancellation_detach(self):events.append('detach');return super().cancellation_detach()
   def close(self):events.append('store-close');return super().close()
  endpoint_calls=[]
  def endpoint(**config):endpoint_calls.append(config);check('cancellationOptIn' not in config,'internal option removed before Endpoint construction');return native
  def publish(client,hello,recovery,cancellation=None):
   check((cancellation is not None)==enabled,'main chooses coordinator only for explicit true')
   check((type(recovery.ledger).__name__=='CancellationLedger')==enabled,'main selects actual V7 only for explicit true')
   if enabled:
    check(recovery.ledger._live_cancellation_binding==BOUND,'strict selected hello attaches exact current binding')
    check(cancellation.startup()==[],'main-stage startup is local/read-only')
   if mode=='output-failure':raise daemon.OutputFailure('injected output failure after attach')
   raise StopAtPublish()
  real_import=builtins.__import__
  def imported(name,*args,**kwargs):
   if name=='cancellation_coordinator':imports.append(name)
   return real_import(name,*args,**kwargs)
  invalid=mode!='omitted' and mode!='output-failure' and type(mode) is not bool
  with contextlib.ExitStack() as stack:
   for target,replacement in [('Endpoint',endpoint),('CatalogTransport',Catalog),('NotificationService',Context),('SystemMenu',Context),('Explorer',Context),('JumpLists',lambda *args:Context()),('Journal',Store),('event_socket',lambda client:contextlib.nullcontext(object())),('publish_startup',publish)]:stack.enter_context(patch.object(daemon,target,replacement))
   stack.enter_context(patch.object(daemon.selectors,'DefaultSelector',Context));stack.enter_context(patch.object(sys,'argv',['daemon.py',str(path)]));stack.enter_context(patch('builtins.__import__',imported))
   try:daemon.main()
   except Refused:
    check(invalid or mode=='output-failure','only invalid option/output failure raises Refused here')
   except StopAtPublish:check(not invalid,'valid configuration reaches actual startup selection')
   else:raise AssertionError('unexpected main return')
  if invalid:
   check(endpoint_calls==[] and constructs==[],'invalid non-Boolean option refuses before Endpoint/store')
  else:
   check(len(endpoint_calls)==1 and constructs==([{'cancellation':True}] if enabled else [{}]),'actual store constructor option/default preserved')
   check(bool(imports)==enabled,'disabled default never imports coordinator')
   if enabled:check(events.index('detach')<events.index('store-close'),'ExitStack detaches coordinator before closing real store')
   else:check('detach' not in events,'legacy default never invokes cancellation detach')
   check(count(native,'effect-prepare')==0 and count(native,'effect-commit')==0 and count(native,'effect-decision-ack')==0,'configuration/startup/unwind never submit native cancellation effects')
print(json.dumps({'passed':True,'checks':len(checks),'nativeAcceptance':False,'scope':'Actual candidate daemon main config selection/unwind, real V6/V7 stores and strict hello/attach response doubles; services/event I/O inert, no real native/C/Elm journey.'}))
