"""Read-only cancellation witnesses; no import-time operations or native writes."""
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
from context_provider import monitor_fingerprint
from recovery_intent import identity,positive,reconstruct,direction
from scene_controller import key
from service_runtime import RuntimeLease

FIELDS=('address','stableId','pid','mapped','at','size','pinned','workspace','monitor')

def projection(window):
    return {field:deepcopy(window.get(field,True if field=='mapped' else None)) for field in FIELDS}

def lease_proof(recovery):
    callback=recovery.lease_verify;lease=getattr(callback,'__self__',None)
    if type(lease) is not RuntimeLease or getattr(callback,'__func__',None) is not RuntimeLease.verify:
        raise ValueError('cancellation requires actual bound RuntimeLease verification')
    recovery.current();lease.verify()
    if lease.root!=Path(recovery.factory.root) or lease.session!=recovery.factory.guard.session or lease.owner['socket'] is not None:
        raise ValueError('cancellation requires exact startup runtime/session lease')
    return dict(root=str(lease.root),rootIdentity=list(lease.root_identity),lockIdentity=list(lease.lock_identity),owner=deepcopy(lease.owner))

def original(recovery,description):
    scope=description['scope'];intent=reconstruct(recovery.body['recoveryIntent'],scope,recovery.body['serial'])
    if intent.receipt!=positive(description['receipt']) or any(recovery.owners.get(identity(v))!=intent.receipt for v in scope):
        raise ValueError('cancellation original scope no longer owns exact latest receipt')
    return dict(receipt=intent.receipt,scope=deepcopy(scope),symbolic=json.loads(json.dumps(asdict(intent.direction))))

def observe_once(recovery,description):
    recovery.current();desktop=recovery.query_desktop()
    context=monitor_fingerprint(desktop.monitors())
    windows=desktop.clients();recovery.checked_clients(windows)
    by_address={window['address']:window for window in windows}
    classifications=[];families=[]
    for encoded in description['scope']:
        captured=identity(encoded);window=by_address.get(captured[0])
        state='absent' if window is None else 'reused' if key(window)!=captured else 'unmapped' if not window.get('mapped',True) else 'present'
        classifications.append(dict(identity=list(captured),state=state,current=projection(window) if window is not None else None))
        if state!='present':continue
        members,focus=desktop.family(window,windows,description['single'])
        if not isinstance(members,list) or not 1<=len(members)<=64:raise ValueError('complete bounded native cancellation family required')
        member_ids=[identity(key(member)) for member in members]
        if len(set(member_ids))!=len(member_ids) or captured not in member_ids or any(k[0] not in by_address or key(by_address[k[0]])!=k or not by_address[k[0]].get('mapped',True) for k in member_ids):
            raise ValueError('native cancellation family lacks exact current mapped members')
        if any(projection(member)!=projection(by_address[member['address']]) for member in members):raise ValueError('native cancellation family material differs from complete clients')
        focus_id=identity(key(focus))
        if focus_id not in member_ids:raise ValueError('native cancellation focus outside exact family')
        families.append(dict(captured=list(captured),members=[list(k) for k in member_ids],focus=list(focus_id)))
    if monitor_fingerprint(desktop.monitors())!=context:raise ValueError('outputs changed during recovery observation for cancellation')
    current=desktop.clients();recovery.checked_clients(current)
    values=lambda rows:sorted((projection(row) for row in rows),key=lambda row:row['address'])
    if values(current)!=values(windows):raise ValueError('complete client state changed during cancellation observation')
    recovery.current()
    return json.loads(json.dumps(dict(context=context,clients=values(windows),members=classifications,families=families),allow_nan=False))

def observe(recovery,description):
    first=observe_once(recovery,description);second=observe_once(recovery,description)
    if first!=second:raise ValueError('fresh cancellation observations differ')
    return [first,second]

def reason(description,observations,operation=None,focus=None):
    observed=observations[0]
    for member in observed['members']:
        if member['state']!='present':return 'member-'+member['state']
    native=next(f for f in observed['families'] if identity(f['captured'])==identity(description['captured']))
    if description['observedFamily'] and {identity(k) for k in native['members']}!={identity(k) for k in description['scope']}:return 'family-membership-changed'
    if operation=='restore' and focus is not None and identity(native['focus'])!=identity(focus):return 'family-focus-changed'
    return None

REASONS=('member-absent','member-reused','member-unmapped','family-membership-changed','family-focus-changed')

def validate(plan,ledger,serial,completed=False):
    proof=plan.get('cancellation')
    if not isinstance(proof,dict) or set(proof)!={'outcome','acknowledged','reason','original','prepared','lease','observations','helperClosures','resources','refreshes'}:
        raise ValueError('complete durable cancellation acknowledgment required')
    if proof['outcome']!='non-settlement' or proof['acknowledged'] is not True or proof['reason'] not in REASONS or plan.get('endpointObserved') is not None:
        raise ValueError('cancellation must be explicit non-settlement, never endpoint success')
    if plan['operation']!='cancel' or plan['members']!=plan['scope'] or plan['order'] or plan['focus']!=plan['captured']:
        raise ValueError('cancellation cannot carry native settlement ordering')
    original=proof['original']
    if not isinstance(original,dict) or set(original)!={'receipt','scope','symbolic'} or type(original['receipt']) is not int or original['receipt']!=plan['receipt'] or original['scope']!=plan['scope']:raise ValueError('exact original cancellation intent required')
    symbolic=direction(original['symbolic'])
    if symbolic.identity is not None and symbolic.identity not in {identity(k) for k in plan['scope']}:raise ValueError('original cancellation anchor outside old family')
    if not completed:
        intent=reconstruct(ledger,plan['scope'],serial)
        expected=dict(receipt=intent.receipt,scope=plan['scope'],symbolic=json.loads(json.dumps(asdict(intent.direction))))
        if proof['original']!=expected:raise ValueError('cancellation original exact receipt/direction changed')
    if not isinstance(proof['observations'],list) or len(proof['observations'])!=2 or proof['observations'][0]!=proof['observations'][1]:raise ValueError('two identical complete cancellation observations required')
    prepared=proof['prepared']
    if prepared is not None:
        if not isinstance(prepared,dict) or set(prepared)!={'operation','resolvedFrom'} or prepared['operation'] not in ('minimize','restore') or not isinstance(prepared['resolvedFrom'],dict):raise ValueError('original prepared endpoint must be retained')
        basis=prepared['resolvedFrom']
        if set(basis)!={'symbolic','capturedMinimized','active','activeObserved'} or basis['symbolic']!=original['symbolic'] or type(basis['activeObserved']) is not bool or basis['activeObserved']!=(symbolic.anchor=='activate'):raise ValueError('cancelled prepared direction/anchor observation changed')
        if symbolic.constant:resolved=symbolic.constant
        else:
            if type(basis['capturedMinimized']) is not bool:raise ValueError('cancelled prepared original workspace anchor required')
            anchor=symbolic.identity;active=identity(basis['active']) if basis['active'] is not None else None
            resolved=symbolic.resolve({'address':anchor[0],'workspace':{'name':'special:win-minimized' if basis['capturedMinimized'] else '1'}},active[0] if active is not None else '')
        if prepared['operation']!=resolved:raise ValueError('cancelled prepared constant endpoint changed')
    if not completed and reason(plan,proof['observations'],prepared['operation'] if prepared else direction(proof['original']['symbolic']).constant,plan.get('previousFocus'))!=proof['reason']:
        raise ValueError('durable cancellation reason differs from exact original observation')
    results=plan['results'];seen=set()
    if not isinstance(results,list) or (prepared is None and results):raise ValueError('exact prior returned native results required')
    for result in results:
        member=identity(result['identity'])
        if member not in {identity(k) for k in plan['scope']} or member in seen or result.get('operation')!=prepared['operation'] or type(result.get('receipt')) is not int or result['receipt']!=plan['receipt'] or result.get('guardedCoreReturned') is not True:raise ValueError('exact prior returned native result required')
        seen.add(member)
    if not isinstance(proof['refreshes'],list) or len(proof['refreshes'])>32:raise ValueError('bounded cancellation refresh history required')
    return proof

def checked_lease(proof,root,session):
    import re
    if not isinstance(proof,dict) or set(proof)!={'root','rootIdentity','lockIdentity','owner'} or proof['root']!=str(root):raise ValueError('exact cancellation runtime lease proof required')
    for field in ('rootIdentity','lockIdentity'):
        row=proof[field]
        if not isinstance(row,list) or len(row)!=2 or any(type(n) is not int or n<0 for n in row) or row[1]<1:raise ValueError('typed cancellation root/lock inode required')
    owner=proof['owner']
    if not isinstance(owner,dict) or set(owner)!={'pid','start','nonce','session','socket'} or owner['session']!=session or owner['socket'] is not None or not isinstance(owner['nonce'],str) or re.fullmatch('[0-9a-f]{32}',owner['nonce']) is None:raise ValueError('exact cancellation startup owner nonce/session required')
    positive(owner['pid']);positive(owner['start'])
    return proof

def checked_observation(recovery,description,observation):
    if not isinstance(observation,dict) or set(observation)!={'context','clients','members','families'}:raise ValueError('complete cancellation observation schema required')
    recovery.checked_clients(observation['clients'])
    if not isinstance(observation['context'],list) or not observation['context']:raise ValueError('complete cancellation output context required')
    if not isinstance(observation['members'],list) or len(observation['members'])!=len(description['scope']) or not isinstance(observation['families'],list):raise ValueError('complete old member classification required')
    clients={row['address']:row for row in observation['clients']};present=set()
    for encoded,member in zip(description['scope'],observation['members']):
        captured=identity(encoded)
        if not isinstance(member,dict) or set(member)!={'identity','state','current'} or identity(member['identity'])!=captured:raise ValueError('exact ordered old member classification required')
        current=clients.get(captured[0]);state='absent' if current is None else 'reused' if key(current)!=captured else 'unmapped' if not current['mapped'] else 'present'
        if member['state']!=state or member['current']!=current:raise ValueError('old member status differs from complete current clients')
        if state=='present':present.add(captured)
    seen=set()
    for family in observation['families']:
        if not isinstance(family,dict) or set(family)!={'captured','members','focus'}:raise ValueError('complete native family context required')
        captured=identity(family['captured']);members=[identity(k) for k in family['members']]
        if captured not in present or captured in seen or not 1<=len(members)<=64 or len(set(members))!=len(members) or captured not in members or identity(family['focus']) not in members or any(k[0] not in clients or key(clients[k[0]])!=k or not clients[k[0]]['mapped'] for k in members):raise ValueError('native family context differs from exact complete current clients')
        seen.add(captured)
    if seen!=present:raise ValueError('every exact surviving old member needs native context')
