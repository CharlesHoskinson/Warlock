"""Staged family transaction coordinator; no native side effects on import.

Desktop/native operations are supplied explicitly. Renderer transport owns a
persistent pipe and delivers events on a separate thread. Metadata/captures run
on workers, so a retained-scene reversal is enqueued before native lookups.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import dataclass, field
import json
import re
import threading
import time
import uuid
from direction import compose, Direction
from visual_retirement import VisualRetirement

TOKEN = re.compile(r'[0-9a-f]{12}-[1-9][0-9]{0,14}')

def key(window):
    return (window['address'], str(window['stableId']), int(window['pid']))

def ids(members):
    return [{'stableId': str(m['stableId']), 'pid': int(m['pid'])} for m in members]

def rectangle(window):
    return dict(zip(('x', 'y', 'width', 'height'), (*window['at'], *window['size'])))

@dataclass
class Scene:
    token: str
    operation: str
    requested: tuple
    context: object
    members: list = field(default_factory=list)
    sources: list = field(default_factory=list)
    focus: tuple | None = None
    validated: bool = False
    visual: bool = False
    running: bool = False
    ready: bool = False
    accepted_operation: str | None = None
    previous: object = None
    profile: dict = field(default_factory=dict)
    results: list = field(default_factory=list)
    single: bool = False
    direction: Direction | None = None
    retirement: VisualRetirement | None = None

class SceneController:
    """One active exact family scene. Multiple families require separate actors.

    Acceptance returns a token immediately. Completion is observable in results;
    queued acceptance is not a claim of successful native completion.
    """
    def __init__(self, desktop, transport, *, journal=None, duration_ms=220):
        self.desktop = desktop
        self.transport = transport
        self.lock = threading.RLock()
        self.workers = ThreadPoolExecutor(max_workers=4, thread_name_prefix='motion-metadata')
        self.session = uuid.uuid4().hex[:12]
        self.serial = 0
        self.current = None
        self.history = []
        self.closing = False
        self.journal = journal or (lambda value: None)
        self.duration_ms = duration_ms
        transport.set_callback(self.event)

    def write_journal(self):
        record = self.current
        self.journal(None if record is None else {
            'token':record.token, 'operation':record.operation,
            'acceptedOperation':record.accepted_operation, 'validated':record.validated,
            'identities':[list(key(m)) for m in record.members], 'profile':record.profile,
            'results':record.results})

    def owns(self, record):
        return self.current is record

    def retirement_profile(self,record):
        record.profile['visualRetirement']=record.retirement.snapshot()

    def retirement_fault(self,record,error):
        record.retirement.uncertain=True
        record.retirement.error=str(error)
        self.retirement_profile(record)
        record.profile['visualRetirementFailure']=str(error)
        # A failed write cannot grant authority even if the storage fault is
        # later removed. Resource ownership stays attached to current Scene.
        try:self.write_journal()
        except Exception:pass

    def suppress_visual(self,record):
        if not self.owns(record) or record.retirement is not None:return
        binding=VisualRetirement(record.token,self.session,self.transport,record,
            record.profile.get('managerReceipt',0),deepcopy(record.members),deepcopy(record.sources))
        record.retirement=binding
        self.retirement_profile(record)
        try:
            if not binding.members or len(binding.members)!=len(binding.sources):
                raise ValueError('complete owned visual source/lifetime binding required')
            if ids(binding.members)!=[{k:s[k] for k in ('stableId','pid')} for s in binding.sources]:
                raise ValueError('ordered visual source/lifetime binding differs')
            self.write_journal() # durable reservation BEFORE cancel submission
            binding.attempted=True
            self.transport.send({'command':'cancel','token':binding.token,'identities':ids(binding.members)})
            binding.queued=True
            self.retirement_profile(record)
            self.write_journal()
        except Exception as error:self.retirement_fault(record,error)

    def may_prepare(self,record):
        if not self.owns(record) or record.profile.get('contextPending') or record.profile.get('requestTerminated'):return False
        if record.retirement is not None:return False
        if record.visual and not record.validated and self.desktop.reduced():
            self.suppress_visual(record)
            return False
        return True

    def after_retirement_replacement(self,old,new):
        """Managed ingress hook; caller holds the shared reservation lock."""
        return None

    def retirement_event(self,event):
        record=self.current
        binding=record.retirement if record else None
        if binding is None:return None
        if (event.get('event')!='cancelled' or event.get('token')!=binding.token
                or event.get('identities')!=ids(binding.members) or not binding.queued
                or binding.acknowledged):return False
        if (binding.transport is not self.transport or binding.session!=self.session
                or [key(m) for m in record.members]!=[key(m) for m in binding.members]
                or record.sources!=binding.sources):
            self.retirement_fault(record,'owned retirement source/channel binding changed')
            return False
        binding.acknowledged=True
        self.retirement_profile(record)
        record.profile['visualRetirementAckNs']=time.monotonic_ns()
        if binding.uncertain:
            try:self.write_journal()
            except Exception as error:self.retirement_fault(record,error)
            return False # observation is never a discharge of uncertainty
        try:
            self.write_journal() # exact ACK durable BEFORE disposal or replacement
            self.desktop.release_sources(binding.sources)
            record.profile['cleanupAckNs']=time.monotonic_ns()
            if self.closing or record.profile.get('requestTerminated') or not self.owns(record):
                record.previous=None;self.history.append(record);self.history=self.history[-128:]
                self.current=None;self.write_journal()
                return True
            retained={k:deepcopy(v) for k,v in record.profile.items() if k in
                ('receivedNs','reservedNs','ingressCommand','managerReceipt','contextPending','contextAcceptedNs')}
            retained['retiredVisualAck']=binding.snapshot()
            retained['visualRetirementFreshToken']=True
            self.serial+=1
            fresh=Scene(f'{self.session}-{self.serial}',record.operation,record.requested,record.context,
                profile=retained,results=deepcopy(record.results),single=record.single,direction=record.direction)
            record.previous=None;self.history.append(record);self.history=self.history[-128:]
            self.current=fresh
            self.after_retirement_replacement(record,fresh)
            self.write_journal() # fresh record + pending reference atomically durable
            if not fresh.profile.get('contextPending'):self.workers.submit(self.prepare,fresh)
            return True
        except Exception as error:
            # Never let a partially persisted replacement start native work.
            if self.current is not record:
                failed=self.current
                failed.retirement=binding;failed.sources=deepcopy(binding.sources);failed.members=deepcopy(binding.members)
                self.retirement_fault(failed,error)
            else:self.retirement_fault(record,error)
            return False

    def request(self, command, address, stable_id, pid, *, context, single=False, direction=None, defer_prepare=False):
        if command not in ('minimize','restore','toggle','activate'):
            raise ValueError('invalid motion operation')
        captured = (address, str(stable_id), int(pid))
        if captured[2] < 1 or not re.fullmatch(r'[0-9a-f]{1,16}',captured[1]):
            raise ValueError('invalid captured identity')
        with self.lock:
            previous = self.current
            if previous and captured != previous.requested and captured not in {key(m) for m in previous.members}:
                # One renderer scene cannot accidentally absorb an unrelated
                # same-process window. A service scene manager must route it.
                raise ValueError('actor belongs to a different captured family')
            if direction is None:
                prior=(Direction(previous.operation) if previous.operation in ('minimize','restore') else previous.direction) if previous else None
                direction=compose(command,prior,captured=captured)
            if not isinstance(direction,Direction):raise ValueError('invalid internal direction')
            operation=direction.constant or direction.anchor
            self.serial += 1
            record = Scene(f'{self.session}-{self.serial}', operation, captured, context,
                members=deepcopy(previous.members) if previous else [],
                sources=deepcopy(previous.sources) if previous and 'cleanupQueuedNs' not in previous.profile else [],
                focus=previous.focus if previous else None,
                accepted_operation=previous.accepted_operation if previous else None,
                previous=previous, single=single, direction=direction,
                retirement=previous.retirement if previous else None,
                profile={'receivedNs':time.monotonic_ns(),'reservedNs':time.monotonic_ns(),'ingressCommand':command,'contextPending':defer_prepare})
            if record.retirement is not None:self.retirement_profile(record)
            self.current = record # ALL member authority changes atomically here.
            self.write_journal()
            if previous and previous.visual and record.sources and context == previous.context and record.retirement is None:
                try:
                    self.transport.send({'command':'retarget','token':record.token,
                        'identities':ids(record.members),'operation':operation,
                        'durationMs':self.duration_ms})
                    record.visual = True
                    record.running = True # producer starts provisional retarget itself
                    record.profile['retargetQueuedNs'] = time.monotonic_ns()
                except Exception as error:
                    if not defer_prepare:raise
                    record.profile['provisionalQueueFailure']=str(error)
                self.write_journal()
            if not defer_prepare:self.workers.submit(self.prepare, record)
            return {'ok':True, 'accepted':True, 'token':record.token, 'completed':False}

    def fresh(self, record):
        windows = self.desktop.clients()
        lookup = {key(w):w for w in windows if w.get('mapped',True)}
        window = lookup.get(record.requested)
        if window is None:
            raise ValueError('captured identity closed or reused')
        members, focus = self.desktop.family(window, windows, record.single)
        actual = {key(m) for m in members}
        returned = {key(m):m for m in members}
        if record.members:
            if actual != {key(m) for m in record.members}:
                raise ValueError('fresh family scope changed; replacement scene required')
            members = [returned.get(key(m)) for m in record.members]
            if any(m is None for m in members):
                raise ValueError('family identity coverage incomplete')
        else:
            # Native family planner order is owner then descendants; keep it
            # stable for textures and immutable composite scene records.
            members = [returned[key(m)] for m in members]
        if record.sources:
            for member, source in zip(members, record.sources, strict=True):
                if rectangle(member) != source['nativeRect']:
                    raise ValueError('native geometry changed; replacement scene required')
        return members, key(focus)

    def validate_scope(self, record, members):
        """Hook for an explicit shared family ownership registry."""
        return None

    def reserve_retirement_scope(self,record,members):
        """Registry hook before irreversible gesture retirement; no native authority."""
        return None

    def direction_for(self,record,members):
        return record.direction

    def prepare(self, record):
        sources=[]
        try:
            record.profile['metadataStartNs'] = time.monotonic_ns()
            members, focus = self.fresh(record)
            with self.lock:
                if not self.may_prepare(record):return
                direction=self.direction_for(record,members)
            active=self.desktop.active() if direction.anchor=='activate' else None
            with self.lock:
                if not self.may_prepare(record):return
                retire=getattr(self.desktop,'retire_gestures',None)
                if retire is not None:
                    self.reserve_retirement_scope(record,members)
                    before_scope={key(m) for m in members}
                    record.profile['gestureRetirementScope']=[list(key(m)) for m in members]
                    record.profile['gestureRetirementStartNs']=time.monotonic_ns()
                    self.write_journal()
                    try:retired=retire(members)
                    except Exception as error:
                        record.profile['gestureRetirementFailure']=getattr(error,'evidence',str(error))
                        raise
                    record.profile['gestureRetirementReply']=retired
            # Read-only post-retirement relations must not hold the receipt
            # lock: an in-flight reply cannot delay a retained visual retarget.
            if retire is not None:
                with self.lock:
                    if not self.may_prepare(record):return
                members,focus=self.fresh(record)
                witness=getattr(self.desktop,'family_evidence',None)
                evidence=witness() if witness is not None else None
                with self.lock:
                    if not self.may_prepare(record):return
                    if {key(m) for m in members}!=before_scope:raise ValueError('exact family changed after gesture retirement')
                    record.profile['gestureRetirementFreshNs']=time.monotonic_ns()
                    record.profile['postRetirementFamily']=[{field:deepcopy(m.get(field)) for field in
                        ('address','stableId','pid','at','size','pinned','floating','fullscreen','parent','parentStableId','modal')} for m in members]
                    direction=self.direction_for(record,members)
                active=self.desktop.active() if direction.anchor=='activate' else None
            else:
                witness=getattr(self.desktop,'family_evidence',None)
                evidence=witness() if witness is not None else None
            with self.lock:
                if not self.may_prepare(record):return
                direction=self.direction_for(record,members)
                anchor=direction.identity or record.requested
                window=next((m for m in members if key(m)==anchor),None)
                if window is None:raise ValueError('relative direction anchor closed or left exact family')
                record.operation=direction.resolve(window,active)
                record.direction=Direction(record.operation)
                record.profile['resolvedDirection']=record.operation
                if witness is not None:record.profile['familyDrawEvidence']=evidence
                self.validate_scope(record, members)
                record.members=members;record.focus=focus
                self.write_journal()
            # Native adapters split slow metadata/refresh observations from
            # the existing atomic family focus effect. Generic adapters keep
            # their original synchronous effect API.
            planner=getattr(self.desktop,'plan_destination',None)
            plans=[]
            if record.operation=='restore' and planner is not None:
                if not callable(getattr(self.desktop,'apply_destination',None)) or not callable(getattr(self.desktop,'refresh_destination',None)):
                    raise ValueError('complete split destination capability required')
                for member in members:
                    if member.get('workspace',{}).get('name')!='special:win-minimized':continue
                    with self.lock:
                        if not self.may_prepare(record):return
                    plan=planner(member)
                    with self.lock:
                        if not self.may_prepare(record):return
                    plans.append((member,plan))
            with self.lock:
                if not self.may_prepare(record):return
                if record.operation=='restore':
                    if planner is not None:
                        for member,plan in plans:self.desktop.apply_destination(member,plan)
                    else:
                        for member in members:
                            if member.get('workspace',{}).get('name')=='special:win-minimized':self.desktop.select_destination(member)
            for member,plan in plans:
                with self.lock:
                    if not self.may_prepare(record):return
                self.desktop.refresh_destination(member,plan)
                with self.lock:
                    if not self.may_prepare(record):return
            reduced=self.desktop.reduced()
            with self.lock:
                if not self.may_prepare(record):return
                record.profile['metadataValidatedNs'] = time.monotonic_ns()
                record.validated = True
                record.accepted_operation = record.operation
                self.write_journal()
                endpoint_matches=all((m.get('workspace',{}).get('name')=='special:win-minimized')==(record.operation=='minimize') for m in members)
                if endpoint_matches and not record.visual and not (record.previous and record.previous.visual):
                    record.profile['nativeEndpointAlreadySatisfied']=True
                    self.settle(record,'native endpoint already satisfied')
                    return
                if reduced:
                    self.settle(record,'reduced motion')
                    return
                if not record.visual and record.previous and record.previous.visual and record.sources:
                    self.transport.send({'command':'retarget','token':record.token,
                        'identities':ids(record.members),'operation':record.operation,
                        'durationMs':self.duration_ms})
                    record.visual=True
                    record.running=True
                if record.visual:
                    self.transport.send({'command':'validate','token':record.token,
                        'identities':ids(record.members)})
                    record.profile['validationQueuedNs']=time.monotonic_ns()
                    self.write_journal()
                    return
            # First scene capture may take time. Reversals above never take this
            # path; their complete textures already belong to the renderer.
            for i,member in enumerate(members):
                with self.lock:
                    if not self.may_prepare(record):return
                sources.append(self.desktop.capture_source(member,record.token,i))
            with self.lock:
                if not self.may_prepare(record):return
            outputs=self.transport.ensure_outputs(force=bool(record.previous and 'cleanupQueuedNs' in record.previous.profile))
            with self.lock:
                if not self.may_prepare(record):return
            fresh, focus = self.fresh(record)
            witness=getattr(self.desktop,'family_evidence',None)
            evidence=witness() if witness is not None else None
            with self.lock:
                if not self.may_prepare(record):return
                if witness is not None:
                    if (not evidence or evidence.get('drawOrder')!=[list(key(m)) for m in fresh]
                            or [key(m) for m in fresh]!=[key(m) for m in members]):raise ValueError('native draw order changed during capture; replacement scene required')
                    record.profile['familyDrawEvidence']=evidence
                for member,source in zip(fresh,sources,strict=True):
                    if rectangle(member)!=source['nativeRect']:
                        raise ValueError('native geometry drifted during family capture')
                record.sources = sources
                record.visual = True
                self.transport.send({'command':'seed','token':record.token,
                    'operation':record.operation,'durationMs':self.duration_ms,
                    'members':sources,'outputs':outputs})
                self.transport.send({'command':'validate','token':record.token,
                    'identities':ids(record.members)})
                record.profile['seedQueuedNs']=time.monotonic_ns()
                self.write_journal()
        except Exception as error:
            with self.lock:
                if self.owns(record) and record.retirement is None:self.reject(record,str(error))
        finally:
            if sources and record.sources is not sources:
                self.desktop.release_sources(sources)

    def commit_members(self, record, operation, reason, observation=None):
        # Callback and reservation share this lock; latest intent cannot change
        # halfway through this transaction. Core still guards each exact ID/PID.
        if not self.owns(record):raise ValueError('native callback was superseded')
        if record.retirement is not None or record.profile.get('requestTerminated'):raise ValueError('pending visual retirement has no native authority')
        members, focus = observation if observation is not None else self.fresh(record)
        if {key(m) for m in members}!={key(m) for m in record.members}:raise ValueError('native observation scope changed')
        if self.desktop.reduced() and not record.validated:
            raise ValueError('unvalidated intent has no reduced-motion authority')
        ordered = sorted(members,key=lambda m:operation=='restore' and key(m)==focus)
        for member in ordered:
            self.desktop.commit(operation,member,bool(record.sources))
            record.results.append({'identity':list(key(member)),'operation':operation,
                'reason':reason,'committedNs':time.monotonic_ns()})
            self.write_journal()

    def event(self, event):
        with self.lock:
            retired=self.retirement_event(event)
            if retired is not None:return retired
            record = self.current
            if record is None:return False
            if event.get('token') != record.token:
                previous=record.previous
                if (previous and event.get('event')=='cancelled' and event.get('token')==previous.token
                        and 'cleanupQueuedNs' in previous.profile and event.get('identities')==ids(previous.members)):
                    current_paths={s['path'] for s in record.sources}
                    self.desktop.release_sources([s for s in previous.sources if s['path'] not in current_paths])
                    previous.profile['cleanupAckNs']=time.monotonic_ns()
                    previous.previous=None
                return False
            if event.get('identities') != ids(record.members):return False
            kind = event.get('event')
            expected_sources=[{k:s[k] for k in ('stableId','pid','digest')} for s in record.sources]
            if kind in ('ready','endpoint') and (not record.validated or not event.get('servicePromoted') or event.get('sourceDigests')!=expected_sources):return False
        # A presentation callback must not monopolize input reservation while
        # collecting slow native relations. Its observation has no authority.
        observation=None
        if kind in ('ready','endpoint'):
            try:observation=self.fresh(record)
            except Exception as error:
                with self.lock:
                    if self.owns(record):self.reject(record,str(error))
                return False
        with self.lock:
            if not self.owns(record):return False
            try:
                if kind=='ready':
                    if record.ready:return True
                    if record.operation=='minimize':self.commit_members(record,'minimize','presented ready',observation)
                    record.ready=True
                    if not record.running:
                        self.transport.send({'command':'start','token':record.token,'identities':ids(record.members)})
                        record.running=True
                    self.write_journal()
                elif kind=='endpoint':
                    if record.operation=='restore':self.commit_members(record,'restore','presented endpoint',observation)
                    self.cleanup(record,'native handover complete')
                elif kind=='cancelled':
                    if 'cleanupQueuedNs' in record.profile:self.finish_cleanup(record)
                    else:
                        record.visual=False
                        self.settle(record,'renderer cancelled')
                elif kind in ('fatal','rejected'):
                    record.visual=False
                    self.settle(record,kind)
                else:return False
                return True
            except Exception as error:
                self.reject(record,str(error))
                return False

    def cleanup(self, record, reason):
        if not self.owns(record):return
        if record.retirement is not None:
            record.profile['requestTerminated']=reason
            self.write_journal();return
        if record.visual:
            self.transport.send({'command':'cancel','token':record.token,'identities':ids(record.members)})
        record.profile['cleanupQueuedNs']=time.monotonic_ns()
        # ACK completes visual cleanup. Keep retained sources until ACK so a
        # rapid request during native/visual handover can reuse them.
        record.profile['settlementReason']=reason
        self.write_journal()

    def settle(self, record, reason):
        if not self.owns(record):return
        if record.retirement is not None:
            self.cleanup(record,reason);return
        operation = record.operation if record.validated else record.accepted_operation
        if operation:
            self.commit_members(record,operation,reason)
        self.cleanup(record,reason)
        if not record.visual:self.finish_cleanup(record)

    def reject(self, record, error):
        record.profile['failure']=error
        try:self.settle(record,'request rejected: '+error)
        except Exception as settlement_error:
            record.profile['settlementFailure']=str(settlement_error)
            self.cleanup(record,'safe rejection')
            if not record.visual:self.finish_cleanup(record)

    def finish_cleanup(self, record):
        if not self.owns(record):return
        if record.retirement is not None:return
        record.profile['cleanupAckNs']=time.monotonic_ns()
        self.desktop.release_sources(record.sources)
        record.previous=None
        self.history.append(record)
        self.history=self.history[-128:]
        self.current=None
        self.write_journal()

    def watchdog(self):
        with self.lock:
            record=self.current
            if not record or 'cleanupQueuedNs' in record.profile:return
            try:
                if record.retirement is not None:
                    if time.monotonic_ns()-record.profile['receivedNs']>2000000000:self.cleanup(record,'controller deadline')
                    return
                if self.desktop.reduced():
                    if record.validated:self.settle(record,'reduced during motion')
                    elif record.visual:self.suppress_visual(record)
                    elif time.monotonic_ns()-record.profile['receivedNs']>2000000000:self.settle(record,'controller deadline')
                elif time.monotonic_ns()-record.profile['receivedNs']>2000000000:self.settle(record,'controller deadline')
            except Exception as error:self.reject(record,str(error))

    def transport_failure(self, reason):
        with self.lock:
            record=self.current
            if record:
                if record.retirement is not None:
                    self.retirement_fault(record,'renderer connection failed: '+reason);return
                record.visual=False
                try:self.settle(record,'renderer connection failed: '+reason)
                except Exception as error:self.reject(record,str(error))

    def close(self):
        with self.lock:
            self.closing=True
            if self.current and self.current.retirement and self.current.retirement.uncertain:
                raise RuntimeError('uncertain visual retirement retains owned resources')
            if self.current:self.settle(self.current,'service shutdown')
        self.workers.shutdown(wait=True,cancel_futures=True)
