"""Staged multi-family registry. Explicit factory only; no native launch on import."""
from dataclasses import dataclass
import re
import threading
import time
from scene_controller import SceneController, ids, key

@dataclass
class Actor:
    number:int
    controller:object

class ManagedController(SceneController):
    def __init__(self, manager, desktop, transport, **options):
        self.manager=manager
        self.accepting_receipt=0
        self.retired={}
        super().__init__(desktop,transport,**options)
        # One reservation lock also covers complete per-member native effects.
        # No registry/controller lock inversion and no half-family reservation.
        self.lock=manager.lock
    def write_journal(self):
        if self.current and 'managerReceipt' not in self.current.profile:
            self.current.profile['managerReceipt']=self.accepting_receipt
        super().write_journal()
    def owns(self,record):
        return super().owns(record) and self.manager.owns(self,record)
    def validate_scope(self,record,members):
        self.manager.claim(self,record,members)
    def retire(self,record,reason):
        if self.current is not record:return
        record.profile['registryRetiredNs']=time.monotonic_ns()
        record.profile['registryRetiredReason']=reason
        self.current=None
        if record.visual:
            self.retired[record.token]=record
            try:self.transport.send({'command':'cancel','token':record.token,'identities':ids(record.members)})
            except Exception as error:record.profile['cancelQueueFailure']=str(error)
        else:
            self.desktop.release_sources(record.sources)
            record.previous=None
            self.history.append(record)
            self.history=self.history[-128:]
        self.write_journal()
    def event(self,event):
        with self.lock:
            record=self.retired.get(event.get('token'))
            if record is not None:
                if event.get('event')!='cancelled' or event.get('identities')!=ids(record.members):return False
                protected=self.manager.source_paths()
                self.desktop.release_sources([s for s in record.sources if s['path'] not in protected])
                record.profile['cleanupAckNs']=time.monotonic_ns()
                record.previous=None
                self.history.append(record);self.history=self.history[-128:]
                del self.retired[record.token]
                return True
        return super().event(event)

class SceneManager:
    """factory(actor_number) -> (desktop, transport); caller owns launch policy.

    Context is supplied by a trusted integration caller for now. This registry
    does not promote it into native workspace/output evidence.
    """
    def __init__(self,factory,**controller_options):
        self.factory=factory
        self.options=controller_options
        self.lock=threading.RLock()
        self.serial=0
        self.actors=[]
        self.owners={}
        self.receipts={}
        self.closed=False
    def source_paths(self):
        return {s['path'] for a in self.actors if a.controller.current for s in a.controller.current.sources}
    def owns(self,controller,record):
        receipt=record.profile.get('managerReceipt',0)
        scope={key(m) for m in record.members} or {record.requested}
        return receipt>0 and all(self.receipts.get(k,0)<=receipt for k in scope)
    def claim(self,controller,record,members):
        if controller.current is not record:raise ValueError('obsolete actor family claim')
        scope={key(m) for m in members}
        receipt=record.profile['managerReceipt']
        if record.requested not in scope or not scope:raise ValueError('fresh scope excludes captured identity')
        if any(self.receipts.get(k,0)>receipt for k in scope):
            controller.retire(record,'newer exact peer reservation')
            raise ValueError('newer family receipt prohibits obsolete claim')
        collisions={self.owners[k] for k in scope if k in self.owners and self.owners[k] is not controller}
        # Native relation evidence, not shared PID, is the only merger proof.
        # Revoke complete old actors before any current destination/native effect.
        for k in scope:self.receipts[k]=receipt
        for other in collisions:
            if other.current:other.retire(other.current,'fresh overlapping family claim')
        for k,c in list(self.owners.items()):
            if c is controller and k not in scope:del self.owners[k]
        for k in scope:self.owners[k]=controller
    def request(self,command,address,stable_id,pid,*,context,single=False):
        if (command not in ('minimize','restore','toggle','activate') or not isinstance(address,str)
                or re.fullmatch(r'0x[0-9a-f]{1,16}',address) is None
                or re.fullmatch(r'[0-9a-f]{1,16}',str(stable_id)) is None
                or not isinstance(pid,int) or isinstance(pid,bool) or pid<1):
            raise ValueError('invalid captured request')
        captured=(address,str(stable_id),pid)
        with self.lock:
            if self.closed:raise RuntimeError('scene manager closed')
            controller=self.owners.get(captured)
            if controller is None:
                number=len(self.actors)+1
                desktop,transport=self.factory(number)
                controller=ManagedController(self,desktop,transport,**self.options)
                self.actors.append(Actor(number,controller))
                self.owners[captured]=controller
            self.serial+=1
            scope={k for k,c in self.owners.items() if c is controller}|{captured}
            for k in scope:self.receipts[k]=self.serial
            controller.accepting_receipt=self.serial
            result=controller.request(command,address,stable_id,pid,context=context,single=single)
            result['receipt']=self.serial
            result['actor']=next(a.number for a in self.actors if a.controller is controller)
            return result
    def state(self):
        with self.lock:
            return [{'actor':a.number,'token':a.controller.current.token if a.controller.current else None,
                'receipt':a.controller.current.profile.get('managerReceipt') if a.controller.current else None,
                'identities':ids(a.controller.current.members) if a.controller.current else [],
                'retiredTokens':list(a.controller.retired)} for a in self.actors]
    def watchdog(self):
        for a in list(self.actors):a.controller.watchdog()
    def close(self):
        with self.lock:self.closed=True
        failures=[]
        for a in self.actors:
            try:a.controller.close()
            except Exception as error:failures.append({'actor':a.number,'reason':str(error)})
            close=getattr(a.controller.transport,'close',None)
            if close:
                try:close()
                except Exception as error:failures.append({'actor':a.number,'reason':str(error)})
        if failures:raise RuntimeError('actor shutdown failures: '+str(failures))
