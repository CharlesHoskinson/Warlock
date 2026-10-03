"""Staged multi-family registry. Explicit factory only; no native launch on import."""
from dataclasses import dataclass
import re
import threading
import time
from scene_controller import SceneController, ids, key
from direction import Direction, compose

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
    def direction_for(self,record,members):
        return self.manager.intent_for({key(m) for m in members},record.profile['managerReceipt'])
    def validate_scope(self,record,members):
        self.manager.claim(self,record,members)
    def reserve_retirement_scope(self,record,members):
        self.manager.claim(self,record,members,compress=False)
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
    def watchdog(self):
        with self.lock:
            if self.current and self.current.profile.get('contextPending'):return
        return super().watchdog()
    def transport_failure(self,reason):
        with self.lock:
            if self.current and self.current.profile.get('contextPending'):
                self.current.visual=False
                self.retire(self.current,'provisional transport failure: '+reason)
                return
        return super().transport_failure(reason)
    def event(self,event):
        with self.lock:
            current=self.current
            if (current and current.profile.get('contextPending')
                    and event.get('token')==current.token and event.get('identities')==ids(current.members)
                    and event.get('event') in ('cancelled','fatal','rejected')):
                current.visual=False
                self.retire(current,'provisional renderer refused before context')
                return True
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
    def __init__(self,factory,*,persist=None,max_actors=64,**controller_options):
        if isinstance(max_actors,bool) or not isinstance(max_actors,int) or not 1<=max_actors<=256:raise ValueError('bounded actor limit required')
        self.factory=factory
        self.persist=persist or (lambda:None)
        self.persistence_failed=False
        self.options=controller_options
        self.lock=threading.RLock()
        self.serial=0
        self.actors=[]
        self.retiring=[]
        self.actor_serial=0
        self.max_actors=max_actors
        self.resource_errors=[]
        self.owners={}
        self.receipts={}
        self.closed=False
        self.pending={}
        self.ingress_history=[]
        self.intent_events={}
        self.intent_anchors={}
        self.max_direction_events=512
    def intent_for(self,scope,receipt):
        anchors={r:d for k,(r,d) in self.intent_anchors.items() if k in scope and r<=receipt}
        if len(anchors)>1:
            raise ValueError('previous accepted family scopes require atomic replacement')
        baseline=max(anchors,default=0)
        direction=anchors.get(baseline)
        for r,event in sorted(self.intent_events.items()):
            if baseline<r<=receipt and event['captured'] in scope:
                direction=compose(event['command'],direction,captured=event['captured'])
        if direction is None:raise ValueError('accepted family direction is unavailable')
        return direction
    def compress_intent(self,scope,receipt,direction):
        # Only called after complete fresh native relation/receipt validation.
        for k in scope:self.intent_anchors[k]=(receipt,direction)
        for r,event in list(self.intent_events.items()):
            if r<=receipt and event['captured'] in scope:del self.intent_events[r]
    def discard_intent(self,scope,receipt):
        for k in scope:
            if self.intent_anchors.get(k,(0,None))[0]<=receipt:self.intent_anchors.pop(k,None)
        for r,event in list(self.intent_events.items()):
            if r<=receipt and event['captured'] in scope:del self.intent_events[r]
    def source_paths(self):
        return {s['path'] for a in self.actors+self.retiring if a.controller.current for s in a.controller.current.sources}
    def owns(self,controller,record):
        receipt=record.profile.get('managerReceipt',0)
        scope={key(m) for m in record.members} or {record.requested}
        return not self.persistence_failed and receipt>0 and all(self.receipts.get(k,0)<=receipt for k in scope)
    def claim(self,controller,record,members,*,compress=True):
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
        if compress:self.compress_intent(scope,receipt,Direction(record.operation))
    def reserve(self,command,address,stable_id,pid,*,single=False):
        if (command not in ('minimize','restore','toggle','activate') or not isinstance(address,str)
                or re.fullmatch(r'0x[0-9a-f]{1,16}',address) is None
                or re.fullmatch(r'[0-9a-f]{1,16}',str(stable_id)) is None
                or not isinstance(pid,int) or isinstance(pid,bool) or pid<1):
            raise ValueError('invalid captured request')
        captured=(address,str(stable_id),pid)
        with self.lock:
            if self.closed:raise RuntimeError('scene manager closed')
            if len(self.intent_events)>=self.max_direction_events:raise RuntimeError('unresolved accepted direction queue full')
            controller=self.owners.get(captured)
            if controller is None:
                if len(self.actors)+len(self.retiring)>=self.max_actors:raise RuntimeError('live/retiring family actor capacity exhausted')
                self.actor_serial+=1;number=self.actor_serial
                desktop,transport=self.factory(number)
                controller=ManagedController(self,desktop,transport,**self.options)
                bind=getattr(transport,'bind_controller',None)
                if bind:bind(controller)
                self.actors.append(Actor(number,controller))
                self.owners[captured]=controller
            self.serial+=1
            scope={k for k,c in self.owners.items() if c is controller}|{captured}
            if controller.current is None and not any(p['controller'] is controller for p in self.pending.values()):
                # A completed/failed actor supplies no pending native direction;
                # the next relative command observes current native state.
                for k in scope:self.intent_anchors.pop(k,None)
            self.intent_events[self.serial]={'captured':captured,'command':command}
            direction=self.intent_for(scope,self.serial)
            for k in scope:self.receipts[k]=self.serial
            actor=next(a.number for a in self.actors if a.controller is controller)
            ingress={'receipt':self.serial,'actor':actor,'controller':controller,
                'command':command,'direction':direction,'captured':captured,'single':single,'scope':scope,
                'receivedNs':time.monotonic_ns()}
            self.pending[self.serial]=ingress
            self.persist() # acceptance is returned only after durable receipt ownership
            previous=controller.current
            if (previous and previous.visual and previous.sources
                    and 'cleanupQueuedNs' not in previous.profile
                    and direction.constant is not None and previous.single==single):
                controller.accepting_receipt=self.serial
                provisional=controller.request(command,*captured,context=previous.context,
                    single=single,direction=direction,defer_prepare=True)
                ingress['provisional']=controller.current
                ingress['provisionalContext']=previous.context
                ingress['provisionalToken']=provisional['token']
                self.persist()
            return {'ok':True,'accepted':True,'completed':False,'contextPending':True,
                'receipt':self.serial,'actor':actor}
    def finish_ingress(self,ingress,**result):
        self.pending.pop(ingress['receipt'],None)
        self.ingress_history.append({'receipt':ingress['receipt'],'actor':ingress['actor'],
            'identity':list(ingress['captured']),'receivedNs':ingress['receivedNs'],
            'finishedNs':time.monotonic_ns(),**result})
        self.ingress_history=self.ingress_history[-128:]
        self.persist()
    def activate(self,receipt,*,context):
        with self.lock:
            ingress=self.pending.get(receipt)
            if ingress is None:return {'ok':False,'accepted':False,'superseded':True,'receipt':receipt}
            if self.closed or any(self.receipts.get(k,0)!=receipt for k in ingress['scope']):
                self.finish_ingress(ingress,superseded=True)
                return {'ok':False,'accepted':False,'superseded':True,'receipt':receipt}
            controller=ingress['controller'];controller.accepting_receipt=receipt
            captured=ingress['captured']
            try:
                provisional=ingress.get('provisional')
                if provisional is not None:
                    if controller.current is not provisional or not controller.owns(provisional):
                        raise ValueError('provisional scene superseded')
                    if context!=ingress['provisionalContext']:
                        raise ValueError('retained visual context changed; replacement scene required')
                    provisional.context=context
                    provisional.profile['contextPending']=False
                    provisional.profile['contextAcceptedNs']=time.monotonic_ns()
                    controller.workers.submit(controller.prepare,provisional)
                    result={'ok':True,'accepted':True,'token':provisional.token,'completed':False}
                else:
                    result=controller.request(ingress['command'],*captured,context=context,single=ingress['single'],direction=ingress['direction'])
            except Exception as error:
                self.fail_ingress(receipt,str(error))
                raise
            result.update(receipt=receipt,actor=ingress['actor'],contextPending=False)
            self.finish_ingress(ingress,token=result['token'],activated=True)
            return result
    def fail_ingress(self,receipt,reason):
        with self.lock:
            ingress=self.pending.get(receipt)
            if ingress is None:return False
            latest=all(self.receipts.get(k,0)==receipt for k in ingress['scope'])
            if latest and ingress['controller'].current:
                ingress['controller'].retire(ingress['controller'].current,'context request failed: '+reason)
            if latest:self.discard_intent(ingress['scope'],receipt)
            self.finish_ingress(ingress,failed=latest,superseded=not latest,reason=reason)
            return latest
    def request(self,command,address,stable_id,pid,*,context,single=False):
        reserved=self.reserve(command,address,stable_id,pid,single=single)
        return self.activate(reserved['receipt'],context=context)
    def state(self):
        with self.lock:
            return [{'actor':a.number,'token':a.controller.current.token if a.controller.current else None,
                'receipt':a.controller.current.profile.get('managerReceipt') if a.controller.current else None,
                'identities':ids(a.controller.current.members) if a.controller.current else [],
                'retiredTokens':list(a.controller.retired)} for a in self.actors]
    def watchdog(self):
        with self.lock:
            expired=[r for r,p in self.pending.items() if time.monotonic_ns()-p['receivedNs']>2000000000]
        for receipt in expired:self.fail_ingress(receipt,'context deadline')
        for a in list(self.actors):a.controller.watchdog()
    def reap_idle(self):
        detached=[]
        with self.lock:
            if self.closed:return []
            for actor in list(self.actors):
                c=actor.controller
                if c.current is not None or c.retired or any(p['controller'] is c for p in self.pending.values()):continue
                scope={k for k,owner in self.owners.items() if owner is c}
                for k in scope:self.owners.pop(k,None)
                self.discard_intent(scope,self.serial)
                self.actors.remove(actor);self.retiring.append(actor);detached.append((actor,scope,self.serial))
            if detached:self.persist()
        completed=[]
        for actor,scope,receipt in detached:
            try:
                actor.controller.close()
                close=getattr(actor.controller.transport,'close',None)
                if close:close()
                dispose=getattr(actor.controller.desktop,'dispose',None)
                if dispose:dispose()
                retired=getattr(self.factory,'retired',None)
                if retired:retired(actor.number,actor.controller.desktop)
                with self.lock:
                    self.retiring.remove(actor)
                    for identity in scope:
                        if (identity not in self.owners and self.receipts.get(identity,0)<=receipt
                                and not any(identity in p['scope'] for p in self.pending.values())):
                            self.receipts.pop(identity,None)
                    self.persist()
                completed.append(actor.number)
            except Exception as error:
                # Occupied slot remains quarantined. Do not infer normal surface
                # destruction or delete private files after a failed close.
                with self.lock:
                    self.resource_errors.append({'actor':actor.number,'error':str(error)});self.resource_errors=self.resource_errors[-128:]
                    self.persist()
        return completed
    def begin_close(self):
        # Revoke admission before the frontend drains context workers. A worker
        # that returns late can only finish a superseded ingress, never activate.
        failures=[]
        with self.lock:
            self.closed=True
            for receipt in list(self.pending):
                try:self.fail_ingress(receipt,'service shutdown')
                except Exception as error:failures.append({'receipt':receipt,'reason':str(error)})
        if failures:raise RuntimeError('ingress shutdown failures: '+str(failures))
    def close(self):
        failures=[]
        try:self.begin_close()
        except Exception as error:failures.append(str(error))
        with self.lock:
            # Keep records and receipts through callback drain, but prevent an
            # idle registry from claiming completion while surfaces still live.
            self.retiring.extend(self.actors);self.actors=[];self.owners.clear()
            self.intent_events.clear();self.intent_anchors.clear()
            try:self.persist()
            except Exception as error:failures.append(str(error))
            remaining=list(self.retiring)
        for actor in remaining:
            problems=[]
            try:actor.controller.close()
            except Exception as error:problems.append('controller: '+str(error))
            close=getattr(actor.controller.transport,'close',None)
            if close:
                try:close()
                except Exception as error:problems.append('renderer: '+str(error))
            if not problems:
                try:
                    with self.lock:
                        c=actor.controller
                        records=([c.current] if c.current else [])+list(c.retired.values())
                        # Normal renderer exit plus callback drain establishes
                        # visual absence even if no final cancel ACK was sent.
                        for record in records:
                            record.profile['shutdownRendererClosedNs']=time.monotonic_ns()
                            c.desktop.release_sources(record.sources)
                            record.previous=None;c.history.append(record)
                        c.history=c.history[-128:];c.current=None;c.retired.clear()
                    dispose=getattr(c.desktop,'dispose',None)
                    if dispose:dispose()
                    retired=getattr(self.factory,'retired',None)
                    if retired:retired(actor.number,c.desktop)
                    with self.lock:
                        self.retiring.remove(actor)
                        if not self.retiring:self.receipts.clear()
                        self.persist()
                except Exception as error:problems.append('disposal/completion: '+str(error))
            if problems:
                with self.lock:
                    self.resource_errors.append({'actor':actor.number,'error':'; '.join(problems)})
                    self.resource_errors=self.resource_errors[-128:]
                    try:self.persist()
                    except Exception as error:problems.append('error journal: '+str(error))
                failures.append({'actor':actor.number,'reason':'; '.join(problems)})
        if failures:raise RuntimeError('actor shutdown failures: '+str(failures))
