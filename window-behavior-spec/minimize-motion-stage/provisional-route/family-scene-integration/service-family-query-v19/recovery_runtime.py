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
import recovery_cancel as cancellation

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
            if phase not in ('reserved','directory','gated','launched','retired','closed'):raise ValueError('explicit actor allocation phase required')
            directory=row.get('directory')
            if not isinstance(directory,dict) or set(directory)!={'path','parentIdentity','identity'}:raise ValueError('complete durable directory identity required')
            path=Path(directory['path'])
            if path.parent!=expected_parent or re.fullmatch(f'actor-{number}-[0-9a-f]{{32}}',path.name) is None:raise ValueError('actor path outside exact reserved private root')
            for field in ('parentIdentity','identity'):
                value=directory[field]
                if value is None and field=='identity' and (phase=='reserved' or phase in ('retired','closed') and row.get('outcome',{}).get('allocationPhase')=='reserved' and row.get('renderer') is None):continue
                if not isinstance(value,list) or len(value)!=2 or any(type(x) is not int or x<0 for x in value) or value[1]<1:raise ValueError('typed positive directory inode required')
            renderer=row.get('renderer')
            if phase in ('gated','launched') or renderer is not None:
                checked_renderer(renderer)
                if renderer['environment']!=environment or renderer['producer']['sha256']!=self.factory.producer_hash:raise ValueError('renderer selected session/producer provenance differs')
            elif phase not in ('reserved','directory','retired','closed'):raise ValueError('missing renderer allocation ownership')
            if phase=='retired' and (not isinstance(row.get('outcome'),dict) or row['outcome'].get('oldLifetimeGone') is not True or row['outcome'].get('directoryGone') is not False):raise ValueError('retired actor authority requires retained source outcome')
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
                if receipt>body['serial'] or receipt in seen_plans or len(set(scope))!=len(scope) or plan.get('operation')!='cancel' and (set(order)!=set(scope) or len(order)!=len(scope)) or identity(plan['captured']) not in scope or identity(plan['focus']) not in scope or type(plan['single']) is not bool:raise ValueError('exact bounded prepared recovery scope/order required')
                seen_plans.add(receipt)
                if plan.get('operation')=='cancel':
                    proof=cancellation.validate(plan,ledger,body['serial'],recovery['state']=='completed')
                    cancellation.checked_lease(proof['lease'],self.factory.root,self.factory.guard.session)
                    for observation in proof['observations']:cancellation.checked_observation(self,plan,observation)
                    for refresh in proof['refreshes']:
                        if not isinstance(refresh,dict) or set(refresh)!={'lease','observations','helperClosures'}:raise ValueError('complete fresh cancellation authority required')
                        cancellation.checked_lease(refresh['lease'],self.factory.root,self.factory.guard.session)
                        if any(refresh['lease'][k]!=proof['lease'][k] for k in ('root','rootIdentity','lockIdentity')):raise ValueError('cancellation refresh changed runtime/root/lock')
                        if len(refresh['observations'])!=2 or refresh['observations'][0]!=refresh['observations'][1]:raise ValueError('fresh complete cancellation pair required')
                        for observation in refresh['observations']:cancellation.checked_observation(self,plan,observation)
                        self.check_closures(refresh['helperClosures'],environment)
                    self.check_closures(proof['helperClosures'],environment)
                    if not proof['helperClosures'] or proof['helperClosures']!=body.get('helperClosureArchive',[])[:len(proof['helperClosures'])]:raise ValueError('cancellation must retain exact old helper closure archive')
                    if not isinstance(proof['resources'],list) or len(proof['resources'])!=len(resources) or any(v['phase'] not in ('retired','closed') or v['outcome'].get('oldLifetimeGone') is not True for v in proof['resources']):raise ValueError('complete acknowledged resource terminal authority required')
                    if any(v['actor']!=w['actor'] or v['directory']!=w['directory'] or v['renderer']!=w['renderer'] for v,w in zip(proof['resources'],resources)):raise ValueError('acknowledged actor/source ownership changed')
                    if plan['results']!=plan.get('priorResults'):raise ValueError('cancelled intent must preserve exact prior returned results')
                    continue
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
        self.check_closures(body.get('helperClosureArchive',[]),environment)
        self.owners=owners;self.environment=environment
    def check_closures(self,archive,environment):
        if not isinstance(archive,list) or len(archive)>64:raise ValueError('bounded exact helper closure archive required')
        seen=set()
        for record in archive:
            if not isinstance(record,dict) or set(record)!={'ownership','terminal'}:raise ValueError('complete retained helper closure required')
            helper=record['ownership']
            if not isinstance(helper,dict) or set(helper)!={'keeper','jobs'} or not isinstance(helper['jobs'],list):raise ValueError('exact retained helper ownership required')
            row=checked_keeper(helper['keeper'],root=self.factory.root,environment=environment)
            if row['nonce'] in seen:raise ValueError('duplicate archived keeper lifetime')
            seen.add(row['nonce']);terminal,jobs=await_terminal(row)
            if terminal!=record['terminal']:raise ValueError('archived terminal differs from actual old helper proof')
            jobids=set()
            if len(helper['jobs'])>512:raise ValueError('bounded old helper closure jobs required')
            for job in helper['jobs']:
                if not isinstance(job,dict) or set(job)-{'groupEmpty'}!={'job','kind','actor','phase','ownership'} or job['phase'] not in ('gated','released','closed') or job['kind'] not in ('renderer','helper','native-export','native-effect') or not isinstance(job['job'],str) or re.fullmatch('[0-9a-f]{32}',job['job']) is None:raise ValueError('exact archived helper job schema required')
                if job['actor'] is not None:positive(job['actor'])
                if job['kind'] in ('native-export','native-effect') and job['phase']!='closed':raise ValueError('unfinished native effect cannot be archived as cancellation safety')
                from owned_launch import checked_owned
                if job['kind']=='renderer':checked_renderer(job['ownership'])
                else:checked_owned(job['ownership'],environment=environment)
                completed=jobs.get(job['job'])
                if job['job'] in jobids or completed is None or (completed['pid'],completed['start'])!=(job['ownership']['pid'],job['ownership']['start']) or job['phase']=='closed' and not completed['normalCompletion']:raise ValueError('archive lacks exact helper job terminal proof')
                jobids.add(job['job'])
    def close_helpers(self):
        terminal,jobs=await_terminal(self.body['helperOwnership']['keeper'])
        for job in self.body['helperOwnership']['jobs']:
            completed=jobs.get(job['job'])
            if completed is None or (completed['pid'],completed['start'])!=(job['ownership']['pid'],job['ownership']['start']):raise ValueError('durable helper job absent from exact keeper terminal closure')
            if job['phase']=='closed' and completed['normalCompletion'] is not True:raise ValueError('durable normal helper closure differs from keeper proof')
        closure={'ownership':deepcopy(self.body['helperOwnership']),'terminal':deepcopy(terminal)}
        archive=self.body.setdefault('helperClosureArchive',[])
        if not any(row['ownership']['keeper']['nonce']==closure['ownership']['keeper']['nonce'] for row in archive):
            if len(archive)>=64:raise ValueError('bounded exact helper closure archive exceeded')
            archive.append(closure)
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
            # An unplanned scene has no observed scope; the exact accepted
            # pending record carries its provenance and must not be shadowed.
            if not scope:continue
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
    def finish_queries(self):
        if self.keeper is not None:
            self.keeper.stop();self.close_helpers();self.keeper=None;self.desktop=None
    def cancellation_candidate(self,description,prepared=None):
        # Observe malformed/unstable material as refusal; never translate an
        # arbitrary planning exception into permission to cancel.
        original=cancellation.original(self,description)
        observations=cancellation.observe(self,description)
        operation=prepared['operation'] if prepared else direction(original['symbolic']).constant
        focus=prepared['focus'] if prepared else description.get('focus')
        cause=cancellation.reason(description,observations,operation,focus)
        if cause is None:return None
        if cause=='family-focus-changed' and getattr(self.lease_verify,'__self__',None) is None:raise ValueError('captured recovery focus differs; cancellation requires actual lease')
        lease=cancellation.lease_proof(self)
        self.finish_queries();self.current()
        for row in self.body['actorResources']:dispose_directory(row['directory'],renderer_gone=row['outcome'].get('oldLifetimeGone'),inspection_only=True)
        resources=deepcopy(self.body['actorResources'])
        if any(row['phase'] not in ('retired','closed') or row['outcome'].get('oldLifetimeGone') is not True for row in resources):raise ValueError('cancellation requires terminal old actor authority')
        proof=dict(outcome='non-settlement',acknowledged=True,reason=cause,original=original,
            prepared={'operation':prepared['operation'],'resolvedFrom':deepcopy(prepared['resolvedFrom'])} if prepared else None,
            lease=lease,observations=observations,helperClosures=deepcopy(self.body['helperClosureArchive']),resources=resources,refreshes=[])
        results=deepcopy(prepared['results']) if prepared else []
        return {**description,'members':deepcopy(description['scope']),'order':[],'focus':deepcopy(description['captured']),
            'previousFocus':deepcopy(focus),'operation':'cancel','results':results,'priorResults':deepcopy(results),'cancellation':proof}
    def refresh_cancellation(self,plan):
        proof=cancellation.validate(plan,self.body['recoveryIntent'],self.body['serial'])
        cancellation.original(self,plan)
        lease=cancellation.lease_proof(self)
        if any(lease[k]!=proof['lease'][k] for k in ('root','rootIdentity','lockIdentity')):raise ValueError('acknowledged cancellation runtime/root/lock changed')
        for row in self.body['actorResources']:
            if row['renderer'] is not None:
                from recovery_resources import renderer_terminal_state
                if renderer_terminal_state(row['renderer'])['oldLifetimeGone'] is not True:raise ValueError('cancelled old renderer lifetime remains live')
        for row in self.body['actorResources']:dispose_directory(row['directory'],renderer_gone=row['outcome'].get('oldLifetimeGone'),inspection_only=True)
        observations=cancellation.observe(self,plan)
        self.finish_queries();self.current()
        if len(proof['refreshes'])>=32:raise ValueError('bounded cancellation restart observations exceeded')
        proof['refreshes'].append(dict(lease=lease,observations=observations,helperClosures=deepcopy(self.body['helperClosureArchive'])))
        self.persist()
    def prepare_plans(self):
        plans=[];covered=set();ledger=deepcopy(self.body['recoveryIntent'])
        for description in sorted(self.descriptions(),key=lambda r:r['receipt'],reverse=True):
            captured=identity(description['captured']);receipt=description['receipt']
            if captured in covered:continue
            cancelled=self.cancellation_candidate(description)
            if cancelled is not None:
                plans.append(cancelled);covered.update(identity(k) for k in description['scope']);continue
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
            if row['phase'] in ('retired','closed') and row['renderer'] is not None:
                from recovery_resources import renderer_terminal_state
                if renderer_terminal_state(row['renderer'])['oldLifetimeGone'] is not True:raise ValueError('durable terminal actor still has old live renderer lifetime')
            if row['phase'] in ('retired','closed'):continue
            self.current()
            outcome=self.retire(row['renderer'],expected_environment=self.environment) if row['renderer'] is not None else {'oldLifetimeGone':True,'signaled':False,'forced':False}
            if outcome.get('oldLifetimeGone') is not True:raise ValueError('old renderer authority is not proven terminal')
            row['outcome']={**outcome,'directoryGone':False,'allocationPhase':row['phase']};row['phase']='retired';self.persist()
        for row in self.body['actorResources']:
            self.current();dispose_directory(row['directory'],renderer_gone=row['outcome'].get('oldLifetimeGone'),inspection_only=True)
        if recovery['state']=='closing-resources':
            recovery['plans']=self.prepare_plans();recovery['state']='prepared';self.persist()
        for plan in recovery['plans']:
            if plan['operation']=='cancel':self.refresh_cancellation(plan)
        recovery['state']='settling';self.persist()
        for plan in recovery['plans']:
            receipt=positive(plan['receipt']);captured=identity(plan['captured']);expected={identity(v) for v in plan['members']}
            if plan['operation']=='cancel':continue
            if plan['operation'] not in ('minimize','restore'):raise ValueError('durable resolved recovery endpoint required')
            intent=reconstruct(self.body['recoveryIntent'],plan['members'],self.body['serial'])
            if intent.receipt!=receipt or any(self.owners.get(k)!=receipt for k in expected):raise ValueError('latest exact family recovery receipt changed')
            completed={identity(r['identity']) for r in plan['results']}
            for encoded in plan['order']:
                target=identity(encoded)
                if target in completed:continue
                cancelled=self.cancellation_candidate({**plan,'scope':plan['members'],'observedFamily':True},plan)
                if cancelled is not None:
                    plan.clear();plan.update(cancelled);self.persist();break
                members,focus,context=self.observe(captured,plan['single'])
                if {key(w) for w in members}!=expected:raise ValueError('prepared recovery family changed before guarded endpoint')
                if plan['operation']=='restore' and list(focus)!=plan['focus']:raise ValueError('prepared exact recovery focus changed')
                window=next(w for w in members if key(w)==target)
                self.current()
                self.query_desktop().commit(plan['operation'],window,False)
                plan['results'].append({'identity':list(target),'operation':plan['operation'],'receipt':receipt,'guardedCoreReturned':True})
                self.persist()
            if plan['operation']=='cancel':continue
            cancelled=self.cancellation_candidate({**plan,'scope':plan['members'],'observedFamily':True},plan)
            if cancelled is not None:
                plan.clear();plan.update(cancelled);self.persist();continue
            members,_,_=self.observe(captured,plan['single'])
            if any((w.get('workspace',{}).get('name')=='special:win-minimized')!=(plan['operation']=='minimize') for w in members):raise ValueError('actual complete native recovery endpoint not observed')
            plan['endpointObserved']=True;self.persist()
        self.finish_queries()
        if any(plan['operation']=='cancel' for plan in recovery['plans']):
            for plan in recovery['plans']:
                if plan['operation']=='cancel':self.refresh_cancellation(plan)
        for row in self.body['actorResources']:
            if row['phase']=='closed':continue
            self.current()
            outcome=deepcopy(row['outcome']);outcome.update(self.dispose(row['directory'],renderer_gone=outcome.get('oldLifetimeGone')))
            row['phase']='closed';row['outcome']=outcome;self.persist()
        recovery['helperClosures']=deepcopy(self.body.get('helperClosureArchive',[]))
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
