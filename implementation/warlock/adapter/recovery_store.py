"""Broker-facing bounded ledger. Recovery frames are informational only."""
import copy
from delivery_ledger import DeliveryLedger as Ledger
from recovery_journal import Journal,validate,effect_protocol
from endpoint import binding,exact,Refused
class RecoveryStore:
 namespace_path=staticmethod(Journal.namespace_path)
 def __init__(self,runtime,instance,lifetime,*,cancellation=False):
  if type(cancellation) is not bool:raise Refused('Cancellation selection type')
  if cancellation:
   from cancellation_ledger import CancellationLedger
   self.ledger=CancellationLedger(runtime,instance,lifetime)
  else:self.ledger=Ledger(runtime,instance,lifetime)
 @property
 def fd(self):return self.ledger.fd
 @property
 def path(self):return self.ledger.path
 def verify(self,fd):return self.ledger.verify(fd)
 def read(self,name='intent.json'):
  if name=='intent.json':return copy.deepcopy(self.ledger.snapshot()['latest'])
  if name=='host-intent.json':return self.ledger.read(name)
  raise Refused('Recovery filename')
 def begin(self,bound,intent,effectProtocol=1):return self.ledger.begin(bound,intent,effectProtocol)
 def settle(self,outcome):
  # Production daemon supplies the strict full native outcome. Minimal records
  # preserve the old internal Journal API only; they are never frontend routes.
  fields=set(outcome)
  if fields in [set(['binding','intent','status']),set(['binding','intent','status','effectProtocol'])]:
   r=validate({'schema':2,'binding':outcome['binding'],'intent':outcome['intent'],'status':outcome['status'],'effectProtocol':outcome.get('effectProtocol',1)})
   return self.ledger._settle_record(r)
  return self.ledger.settle(outcome)
 def recovery_frames(self,bound):
  binding(bound);self.ledger.synchronization_snapshot();dto=self.ledger.recover(bound)
  request=max([int(m['request']) for m in dto['watermarks']]+[0]);generation=max([int(m['generation']) for m in dto['watermarks']]+[0])
  frames=[{'protocolVersion':3,'kind':'host-recovery-watermarks','binding':copy.deepcopy(bound),'request':str(request),'generation':str(generation)}]
  for r in dto['entries']:
   frame={'protocolVersion':3,'kind':'host-reservation-unknown','binding':copy.deepcopy(bound),'record':copy.deepcopy(r)}
   frames.append(frame)
  return frames
 def settlement_frames(self,bound):
  binding(bound)
  if bound['lifetime']!=self.ledger.target['lifetime']:raise Refused('Settlement compositor lifetime')
  state=self.ledger.synchronization_snapshot()
  return [{'protocolVersion':3,'kind':'host-admission-settled','binding':copy.deepcopy(bound),'record':copy.deepcopy(r)} for r in state['settled']]
 def uncertain(self,bound):
  frames=self.recovery_frames(bound)[1:];return frames[0] if frames else None
 def cancellation_attach(self,bound):return self.ledger.cancellation_attach(bound)
 def cancellation_detach(self):return self.ledger.cancellation_detach()
 def cancellation_reserve(self,bound,intent,deadline):return self.ledger.cancellation_reserve(bound,intent,deadline)
 def cancellation_attempt(self,key,operation):return self.ledger.cancellation_attempt(key,operation)
 def cancellation_observe(self,key,evidence):return self.ledger.cancellation_observe(key,evidence)
 def cancellation_finish(self,key):return self.ledger.cancellation_finish(key)
 def cancellation_ack_pending(self,key):return self.ledger.cancellation_ack_pending(key)
 def cancellation_acknowledged(self,key,ack):return self.ledger.cancellation_acknowledged(key,ack)
 def cancellation_snapshot(self,bound):return self.ledger.cancellation_snapshot(bound)
 def cancellation_receipt_lookup(self,bound,intent,deadline,selection_id):return self.ledger.cancellation_receipt_lookup(bound,intent,deadline,selection_id)
 def cancellation_recovery_frames(self,bound):return self.ledger.cancellation_recovery_frames(bound)
 def cancellation_settlement_frames(self,bound):return self.ledger.cancellation_settlement_frames(bound)
 def close(self):self.ledger.close()
 def __enter__(self):return self
 def __exit__(self,*args):self.close()
