"""Durable restart coordinator. Construct explicitly under the runtime lease."""
from copy import deepcopy
from dataclasses import asdict
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import threading
import uuid
from helper_supervisor import checked_keeper,await_terminal,Keeper
from recovery_intent import identity,positive,reconstruct,validate_ledger,direction
from recovery_resources import checked_renderer,dispose_directory,retire_renderer
from service_runtime import JournalStore
from scene_controller import key
from context_provider import monitor_fingerprint

class NativeRecovery:
    def __init__(self,factory,*,store=None,desktop=None,lease_verify=None,retire=retire_renderer,dispose=dispose_directory):
        self.lease_verify=lease_verify
        self.factory=factory;self.store=store or JournalStore(factory.root,factory.guard.session)
        self.desktop=desktop;self.retire=retire;self.dispose=dispose
        self.body=None;self.keeper=None
    def persist(self):
        if self.lease_verify is None:raise ValueError('actual acquired runtime lease binding required before recovery')
        self.lease_verify()
        self.body['snapshot']+=1
        self.store.write(self.body)
    def current(self):
        if self.lease_verify is None:raise ValueError('actual acquired runtime lease binding required before recovery')
        self.lease_verify()
        self.factory.guard.verify()
        if self.store.read()!=self.body:raise ValueError('durable recovery journal changed outside exclusive lease')
    def preflight(self,body):
        if body.get('recoveryVersion')!=1 or not isinstance(body.get('recoveryIntent'),dict):raise ValueError('legacy unresolved journal lacks full direction/resource provenance')
        if type(body.get('serial')) is not int or not 0<=body['serial']<2**63:raise ValueError('typed durable serial required')
        positive(body['snapshot'])
        if body.get('session')!=self.factory.guard.session:raise ValueError('recovery compositor session differs')
        resources=body.get('actorResources')
        if not isinstance(resources,list) or len(resources)>256:raise ValueError('complete bounded actor resource registry required')
        numbers=set();expected_parent=Path(self.factory.root)/'actors'
        environment={k:self.factory.guard.env[k] for k in ('XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY')}
        for row in resources:
            if not isinstance(row,dict) or set(row)-{'actor','phase','directory','renderer','outcome'}:raise ValueError('complete actor resource schema required')
            number=positive(row.get('actor'))
            if number in numbers:raise ValueError('duplicate actor resource identity')
            numbers.add(number)
            phase=row.get('phase')
            if phase not in ('reserved','directory','gated','launched','closed'):raise ValueError('explicit actor allocation phase required')
            directory=row.get('directory')
            if not isinstance(directory,dict) or set(directory)!={'path','parentIdentity','identity'}:raise ValueError('complete durable directory identity required')
            path=Path(directory['path'])
            if path.parent!=expected_parent or re.fullmatch(f'actor-{number}-[0-9a-f]{{32}}',path.name) is None:raise ValueError('actor path outside exact reserved private root')
            for field in ('parentIdentity','identity'):
                value=directory[field]
                if value is None and phase=='reserved' and field=='identity':continue
                if not isinstance(value,list) or len(value)!=2 or any(type(x) is not int or x<0 for x in value) or value[1]<1:raise ValueError('typed positive directory inode required')
            renderer=row.get('renderer')
            if phase in ('gated','launched') or renderer is not None:
                checked_renderer(renderer)
                if renderer['environment']!=environment or renderer['producer']['sha256']!=self.factory.producer_hash:raise ValueError('renderer selected session/producer provenance differs')
            elif phase not in ('reserved','directory','closed'):raise ValueError('missing renderer allocation ownership')
            if phase=='closed' and (not isinstance(row.get('outcome'),dict) or row['outcome'].get('oldLifetimeGone') is not True or row['outcome'].get('directoryGone') is not True):raise ValueError('durable terminal resource outcomes required')
        required=set()
        for field in ('liveActors','retiringActors'):
            rows=body.get(field)
            if not isinstance(rows,list) or len(rows)>256:raise ValueError('complete actor registry lifetimes required')
            required.update(positive(v) for v in rows)
        if not required<=numbers:raise ValueError('live/retiring actor has no durable resource ownership')
        # Parse the entire ledger before any resource mutation. A dummy fresh
        # family is not used to grant direction authority here.
        ledger=body['recoveryIntent']
        if set(ledger)!={'anchors','events','receipts'} or any(not isinstance(v,list) or len(v)>512 for v in ledger.values()):raise ValueError('complete bounded accepted intent ledger required')
        owners=validate_ledger(ledger,body['serial'])
        if body.get('receipts')!=ledger['receipts']:raise ValueError('manager/direction receipt ledgers differ')
        for pending in body['pending']:
            if not isinstance(pending,dict) or positive(pending['actor']) not in numbers or positive(pending['receipt'])>body['serial'] or pending.get('operation') not in ('minimize','restore','toggle','activate') or type(pending.get('single')) is not bool:raise ValueError('complete exact pending request provenance required')
            captured=identity(pending['captured']);scope=pending.get('scope');direction(pending['direction'])
            if not isinstance(scope,list) or not 1<=len(scope)<=64 or len({identity(v) for v in scope})!=len(scope) or captured not in {identity(v) for v in scope}:raise ValueError('complete pending accepted scope required')
        for scene in body['scenes']:
            if not isinstance(scene,dict) or positive(scene['actor']) not in numbers or positive(scene['profile']['managerReceipt'])>body['serial'] or type(scene.get('single')) is not bool:raise ValueError('complete exact scene provenance required')
            captured=identity(scene['requested']);members=scene['members'];direction(scene['direction'])
            if not isinstance(members,list) or len(members)>64 or len({identity(v) for v in members})!=len(members) or members and captured not in {identity(v) for v in members}:raise ValueError('complete previous native family scope required')
            if scene.get('focus') is not None and identity(scene['focus']) not in {identity(v) for v in members}:raise ValueError('captured scene focus outside exact family')
        helper=body.get('helperOwnership')
        if not isinstance(helper,dict) or set(helper)!={'keeper','jobs'} or not isinstance(helper['jobs'],list):raise ValueError('complete helper keeper ownership required before any recovery mutation')
        checked_keeper(helper['keeper'],root=self.factory.root,environment=environment)
        job_ids=set()
        for job in helper['jobs']:
            if not isinstance(job,dict) or job.get('phase') not in ('gated','released','closed'):raise ValueError('complete durable helper job phase required')
            if set(job)-{'groupEmpty'}!={'job','kind','actor','phase','ownership'} or not isinstance(job['job'],str) or re.fullmatch('[0-9a-f]{32}',job['job']) is None or job['job'] in job_ids or job['kind'] not in ('renderer','helper','native-export','native-effect'):raise ValueError('complete unique typed helper job required')
            job_ids.add(job['job']);positive(job['ownership']['pid']);positive(job['ownership']['start'])
            if job.get('kind')=='renderer':checked_renderer(job['ownership'])
            else:
                from owned_launch import checked_owned
                checked_owned(job['ownership'],environment=environment)
            if job['actor'] is not None and positive(job['actor']) not in numbers:raise ValueError('helper has no exact durable actor ownership')
            if job['kind']=='renderer':
                resource=next((v for v in resources if v['actor']==job['actor']),None)
                if resource is None or resource['renderer']!=job['ownership'] and not(resource['renderer'] is None and resource['phase']=='directory' and job['phase']=='gated'):raise ValueError('renderer keeper role differs from exact actor ownership')
            if job.get('kind') in ('native-export','native-effect') and job['phase']!='closed':raise ValueError('unfinished native export/effect has no durable completion boundary; quarantined')
        recovery=body.get('recovery')
        if recovery is not None:
            if not isinstance(recovery,dict) or recovery.get('state') not in ('closing-resources','prepared','settling','completed') or not isinstance(recovery.get('plans'),list):raise ValueError('complete durable recovery phase required')
            seen_plans=set()
            for plan in recovery['plans']:
                receipt=positive(plan['receipt']);scope=[identity(v) for v in plan['members']];order=[identity(v) for v in plan['order']]
                if receipt>body['serial'] or receipt in seen_plans or len(set(scope))!=len(scope) or set(order)!=set(scope) or len(order)!=len(scope) or identity(plan['captured']) not in scope or identity(plan['focus']) not in scope or type(plan['single']) is not bool:raise ValueError('exact bounded prepared recovery scope/order required')
                seen_plans.add(receipt)
                if recovery['state']!='completed':
                    intent=reconstruct(ledger,plan['members'],body['serial']);basis=plan['resolvedFrom']
                    if intent.receipt!=receipt or basis['symbolic']!=json.loads(json.dumps(asdict(intent.direction))) or type(basis['activeObserved']) is not bool or basis['activeObserved']!=(intent.direction.anchor=='activate'):raise ValueError('prepared symbolic direction differs from durable accepted ledger')
                    if intent.direction.constant:resolved=intent.direction.constant
                    else:
                        if type(basis['capturedMinimized']) is not bool:raise ValueError('durable original anchor observation required')
                        anchor=intent.direction.identity;active=identity(basis['active']) if basis['active'] is not None else None
                        resolved=intent.direction.resolve({'address':anchor[0],'workspace':{'name':'special:win-minimized' if basis['capturedMinimized'] else '1'}},active[0] if active is not None else '')
                    if plan['operation']!=resolved:raise ValueError('prepared constant endpoint changed after original resolution')
                results=plan['results'];identities=set()
                if not isinstance(results,list):raise ValueError('durable per-member native results required')
                for result in results:
                    member=identity(result['identity'])
                    if member not in scope or member in identities or result.get('operation')!=plan['operation'] or type(result.get('receipt')) is not int or result['receipt']!=receipt or result.get('guardedCoreReturned') is not True:raise ValueError('exact unique per-member native result required')
                    identities.add(member)
        self.owners=owners;self.environment=environment
    def close_helpers(self):
        terminal,jobs=await_terminal(self.body['helperOwnership']['keeper'])
        for job in self.body['helperOwnership']['jobs']:
            completed=jobs.get(job['job'])
            if completed is None or (completed['pid'],completed['start'])!=(job['ownership']['pid'],job['ownership']['start']):raise ValueError('durable helper job absent from exact keeper terminal closure')
            if job['phase']=='closed' and completed['normalCompletion'] is not True:raise ValueError('durable normal helper closure differs from keeper proof')
        self.body['helperOwnership']['keeper']['phase']='closed'
        self.body['helperOwnership']['keeper']['terminal']=terminal
        self.body['helperOwnership']['jobs']=[]
        self.persist()
    def query_desktop(self):
        if self.desktop is not None:return self.desktop
        # Query-only adapter: no actor directory, renderer or capture is created.
        from native_runtime import PinnedNativeDesktop
        source=Path(__file__).with_name('production_motion_6d9.py')
        if hashlib.sha256(source.read_bytes()).hexdigest()!='6d9a21114cfc9d8ed4a4669bb4c1a585375abd56bf27de2783e203926dcecbaa':raise ValueError('frozen recovery planner material changed')
        spec=importlib.util.spec_from_file_location('motion_recovery_query_'+uuid.uuid4().hex,source)
        production=importlib.util.module_from_spec(spec);spec.loader.exec_module(production);production.CORE=Path(self.factory.core)
        from owned_commands import OwnedCommands
        if self.keeper is None:
            def changed(body):self.body['helperOwnership']=body;self.persist()
            self.keeper=Keeper(self.factory.root,self.factory.guard.env,changed)
        commands=OwnedCommands(self.keeper,self.factory.guard.env)
        production.subprocess=commands
        d=PinnedNativeDesktop.__new__(PinnedNativeDesktop)
        d.commands=commands;d.production=production;d.base=production.Desktop();d.session_guard=self.factory.guard;d.core_hash=self.factory.core_hash
        d.family_query_lock=threading.RLock();d.family_query_local=threading.local()
        self.desktop=d;return d
    def observe(self,captured,single):
        self.current();d=self.query_desktop()
        before=monitor_fingerprint(d.monitors());windows=d.clients();self.checked_clients(windows)
        found=[w for w in windows if key(w)==captured and w.get('mapped',True)]
        if len(found)!=1:raise ValueError('captured recovery identity closed/reused')
        members,focus=d.family(found[0],windows,single)
        actual={identity(key(w)) for w in members}
        if not actual or len(actual)!=len(members) or captured not in actual:raise ValueError('complete exact fresh recovery family required')
        after=monitor_fingerprint(d.monitors())
        current=d.clients();self.checked_clients(current)
        if {key(w) for w in current}!={key(w) for w in windows}:raise ValueError('complete client identity set changed during recovery observation')
        lookup={key(w):w for w in current if w.get('mapped',True)}
        fields=('address','stableId','pid','at','size','pinned','workspace','monitor')
        if before!=after or any(key(w) not in lookup or any(w.get(k)!=lookup[key(w)].get(k) for k in fields) for w in members):raise ValueError('native family geometry/workspace/output changed during recovery observation')
        self.current();return members,identity(key(focus)),before
    def checked_clients(self,windows):
        from scene_controller import rectangle
        if not isinstance(windows,list) or len(windows)>4096:raise ValueError('complete bounded fresh client list required')
        seen=set()
        for window in windows:
            captured=identity(key(window))
            if captured[0] in seen or type(window.get('mapped',True)) is not bool:raise ValueError('duplicate address or untyped mapped client identity')
            seen.add(captured[0]);rectangle(window)
            if type(window.get('pinned')) is not bool or not isinstance(window.get('workspace'),dict) or not isinstance(window['workspace'].get('name'),str):raise ValueError('complete fresh geometry/workspace/pin observation required')
    def descriptions(self):
        records={}
        for row in self.body['scenes']:
            receipt=positive(row['profile']['managerReceipt']);captured=identity(row['requested'])
            single=row.get('single');scope=[identity(v) for v in row['members']]
            if type(single) is not bool:raise ValueError('durable scene family mode required')
            if self.owners.get(captured)==receipt:
                records[receipt]={'receipt':receipt,'captured':list(captured),'single':single,'scope':[list(v) for v in scope],
                    'focus':row.get('focus'),'observedFamily':bool(scope)}
        for row in self.body['pending']:
            receipt=positive(row['receipt']);captured=identity(row['captured']);single=row['single']
            if type(single) is not bool:raise ValueError('durable request family mode required')
            if self.owners.get(captured)==receipt:
                if receipt in records:continue
                records[receipt]={'receipt':receipt,'captured':list(captured),'single':single,'scope':[list(identity(v)) for v in row['scope']],
                    'focus':None,'observedFamily':False}
        return list(records.values())
    def prepare_plans(self):
        plans=[];covered=set()
        for description in sorted(self.descriptions(),key=lambda r:r['receipt'],reverse=True):
            captured=identity(description['captured']);receipt=description['receipt']
            if captured in covered:continue
            members,focus,context=self.observe(captured,description['single'])
            scope={key(w) for w in members}
            if description['observedFamily'] and scope!={identity(v) for v in description['scope']}:raise ValueError('previous complete recovery family changed; explicit cancellation policy required')
            if any(self.owners.get(k,0)>receipt for k in scope):raise ValueError('fresh family has newer receipt owner; recovery claim refused')
            # Same ordinary registry expansion rule: a fresh native family may
            # add unclaimed peers, only if no newer exact member receipt exists.
            for k in scope:self.owners[k]=receipt
            ledger=deepcopy(self.body['recoveryIntent'])
            ledger['receipts']=[[list(k),r] for k,r in sorted(self.owners.items())]
            intent=reconstruct(ledger,[list(k) for k in scope],self.body['serial'])
            active=None
            if intent.direction.anchor=='activate':
                address=self.query_desktop().active();current=self.query_desktop().clients()
                matches=[key(w) for w in current if w.get('mapped',True) and w['address']==address]
                if address and len(matches)!=1:raise ValueError('fresh active recovery identity unavailable')
                active=matches[0] if matches else None
            operation=intent.endpoint(members,active)
            if intent.receipt!=receipt:raise ValueError('fresh family direction differs from latest accepted receipt')
            captured_focus=identity(description['focus']) if description['focus'] is not None else focus
            if captured_focus not in scope:raise ValueError('exact captured recovery focus missing')
            # Preserve the original owner-before-descendant native ordering;
            # the native planner's deepest focus must remain an exact member.
            if operation=='restore' and captured_focus!=focus:raise ValueError('captured recovery focus differs from current native deepest focus')
            ordered=sorted(members,key=lambda w:operation=='restore' and key(w)==captured_focus)
            plans.append({**description,'members':[list(key(w)) for w in members],
                'order':[list(key(w)) for w in ordered],'focus':list(captured_focus),'operation':operation,'results':[],
                'resolvedFrom':{'symbolic':json.loads(json.dumps(asdict(intent.direction))),'capturedMinimized':next(w for w in members if key(w)==intent.direction.identity).get('workspace',{}).get('name')=='special:win-minimized' if intent.direction.identity is not None else None,'active':list(active) if active is not None else None,'activeObserved':intent.direction.anchor=='activate'}})
            covered.update(scope)
        unresolved={identity(v['captured']) for v in self.body['pending']}
        unresolved.update(identity(v['requested']) for v in self.body['scenes'])
        if any(k not in covered and k in self.owners for k in unresolved):raise ValueError('unresolved exact request lacks prepared complete outcome')
        if plans:self.body['recoveryIntent']=ledger;self.body['receipts']=ledger['receipts']
        return plans
    def _recover(self,previous):
        self.factory.guard.verify();self.preflight(previous);self.body=deepcopy(previous)
        self.current()
        if self.body.get('recovery',{}).get('state')=='completed' and not self.body.get('pending') and not self.body.get('scenes') and all(row['phase']=='closed' for row in self.body['actorResources']):
            self.close_helpers();return deepcopy(self.body)
        self.close_helpers()
        if 'recovery' not in self.body:
            self.body['recovery']={'state':'closing-resources','plans':[]};self.persist()
        recovery=self.body['recovery']
        if recovery['state'] not in ('closing-resources','prepared','settling','completed'):raise ValueError('invalid durable recovery phase')
        for row in self.body['actorResources']:
            if row['phase']=='closed':continue
            self.current()
            outcome=self.retire(row['renderer'],expected_environment=self.environment) if row['renderer'] is not None else {'oldLifetimeGone':True,'signaled':False,'forced':False}
            outcome.update(self.dispose(row['directory'],renderer_gone=outcome.get('oldLifetimeGone')))
            row['phase']='closed';row['outcome']=outcome;self.persist()
        if recovery['state']=='closing-resources':
            recovery['plans']=self.prepare_plans();recovery['state']='prepared';self.persist()
        recovery['state']='settling';self.persist()
        for plan in recovery['plans']:
            receipt=positive(plan['receipt']);captured=identity(plan['captured']);expected={identity(v) for v in plan['members']}
            if plan['operation'] not in ('minimize','restore'):raise ValueError('durable resolved recovery endpoint required')
            intent=reconstruct(self.body['recoveryIntent'],plan['members'],self.body['serial'])
            if intent.receipt!=receipt or any(self.owners.get(k)!=receipt for k in expected):raise ValueError('latest exact family recovery receipt changed')
            completed={identity(r['identity']) for r in plan['results']}
            for encoded in plan['order']:
                target=identity(encoded)
                if target in completed:continue
                members,focus,context=self.observe(captured,plan['single'])
                if {key(w) for w in members}!=expected:raise ValueError('prepared recovery family changed before guarded endpoint')
                if plan['operation']=='restore' and list(focus)!=plan['focus']:raise ValueError('prepared exact recovery focus changed')
                window=next(w for w in members if key(w)==target)
                self.current()
                self.query_desktop().commit(plan['operation'],window,False)
                plan['results'].append({'identity':list(target),'operation':plan['operation'],'receipt':receipt,'guardedCoreReturned':True})
                self.persist()
            members,_,_=self.observe(captured,plan['single'])
            if any((w.get('workspace',{}).get('name')=='special:win-minimized')!=(plan['operation']=='minimize') for w in members):raise ValueError('actual complete native recovery endpoint not observed')
            plan['endpointObserved']=True;self.persist()
        if self.keeper:self.keeper.stop()
        recovery['state']='completed'
        self.body['recoveryHistory']=(self.body.get('recoveryHistory',[])+[deepcopy(recovery)])[-32:]
        self.body.update(pending=[],scenes=[],liveActors=[],retiringActors=[],receipts=[],recoveryIntent={'anchors':[],'events':[],'receipts':[]})
        self.persist();return deepcopy(self.body)

    def recover(self,previous):
        try:return self._recover(previous)
        finally:
            if self.keeper is not None and not self.keeper.closed:
                self.keeper.detach()
                try:self.keeper.process.wait(timeout=5)
                finally:self.keeper.process.stderr.close()
