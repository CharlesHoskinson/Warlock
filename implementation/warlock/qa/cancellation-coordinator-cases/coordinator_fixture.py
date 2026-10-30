"""Actual coordinator + production store, strict schema response doubles only."""
import contextlib,copy,json,os,pathlib,stat,sys,tempfile
from unittest.mock import patch
D=pathlib.Path(__file__).parent
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path[0:0]=[str(ROOT/'adapter'),str(ROOT/'qa/cancellation-store-cases')]
from fixture import *
from cancellation_coordinator import CancellationCoordinator

CAPS={'observe':True,'effects':True,'minimizedState':True,'effectProtocol':1,'operations':['minimize','restore','activate'],'canonicalScene':False,'taskbarProjectionProtocol':1,'effectInvalidationProtocol':1}
BaseNative=Native
class Native(BaseNative):
 def __init__(self,events,depth):
  super().__init__();self.bound=None;self.pid=123;self.instance='coordinatorqa';self.events=events;self.depth=depth;self.reply_mode=None
 def request(self,payload):
  check(self.depth[0]==0,'native RPC outside host_guard '+payload['kind'])
  self.events.append('rpc:'+payload['kind'])
  if payload['kind']=='hello':
   self.calls.append(copy.deepcopy(payload))
   return {'protocolVersion':3,'kind':'attached','binding':copy.deepcopy(BOUND),'compositor':{'pid':self.pid,'instance':self.instance,'coreHash':'0'*64},'capabilities':copy.deepcopy(CAPS)}
  result=super().request(payload)
  if payload['kind']=='effect-commit' and self.reply_mode=='unknown':
   self.state='Unknown';result.update(status='Unknown',reason='effect-unproven')
  if payload['kind']=='effect-decision-request' and self.reply_mode=='prepared-after-unknown':
   result=copy.deepcopy(self.prepared)
  if payload['kind']=='effect-commit' and self.reply_mode=='binding-drift':self.bound={**BOUND,'frontend':'4'}
  return result

@contextlib.contextmanager
def fixture():
 with tempfile.TemporaryDirectory(prefix='warlock-coordinator-') as temporary:
  store=RecoveryStore(pathlib.Path(temporary),'coordinatorqa','1',cancellation=True);Navigation(store)
  events=[];depth=[0];original_guard=store.ledger.host_guard
  @contextlib.contextmanager
  def guard():
   with original_guard() as fd:
    depth[0]+=1
    check(depth[0]==1,'host_guard remains nonreentrant')
    try:yield fd
    finally:depth[0]-=1
  store.ledger.host_guard=guard
  original_writer=store.ledger._write_file_locked
  def writer(name,body,limit):
   result=original_writer(name,body,limit)
   if name=='ledger-v7.json':
    state=json.loads(body)
    if state['cancellations']:
     rec=state['cancellations'][-1];events.append('stored:'+rec['stage']+':'+rec['ackState']+':'+','.join(rec['attemptedKinds']))
   return result
  store.ledger._write_file_locked=writer
  native=Native(events,depth);hello=native.hello();coordinator=CancellationCoordinator(native,store,hello,settlement_sink=lambda frame:events.append('host-settlement:'+frame['ackState']))
  try:yield store,native,coordinator,events,depth,hello
  finally:coordinator.close();store.close()

def request(kind,wire=None):
 if kind=='effect-cancellation-negotiate':return {'protocolVersion':3,'kind':kind,'binding':copy.deepcopy(BOUND),'cancellationProtocol':1,'requestId':'1'}
 value={'protocolVersion':3,'kind':kind,'binding':copy.deepcopy(BOUND),'cancellationProtocol':1,'effectProtocol':1,'intent':intent(),'deadlineMonotonicNs':DEADLINE}
 if wire is not None:value['preparedId']=wire['preparedId']
 return value

def prepare(store,coordinator):
 coordinator.handle(request('effect-cancellation-negotiate'))
 cancellation_pending(store,intent())
 return coordinator.handle(request('effect-prepare'))

def count(native,kind):return sum(x['kind']==kind for x in native.calls)
