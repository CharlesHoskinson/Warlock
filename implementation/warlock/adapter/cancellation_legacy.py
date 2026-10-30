"""Locked legacy seams for the opt-in V7 store; no native transport.

Caller owns Journal's writer lock and ONE host_guard for every entry point.
Borrowed views never acquire/close locks, run legacy constructors, or graft an
object dictionary. All legacy file mutations are confined to first bootstrap.
"""
import copy
import hashlib
import json
import os
import stat
from admission_ledger import AdmissionLedger, storage_key
from cancellation_endpoint import CancellationEndpoint
from delivery_ledger import DeliveryLedger
from durable_ledger import encoded, key, normalize
from endpoint import Refused, exact, unique, canonical
from retirement_ledger import RetirementLedger, release_payload
from recovery_journal import validate

LIMIT = 1048576

class _Borrowed:
    def __init__(self, owner):
        self._owner = owner
    @property
    def fd(self): return self._owner.fd
    @property
    def target(self): return self._owner.target
    @property
    def poisoned(self): return self._owner.poisoned
    @poisoned.setter
    def poisoned(self, value): self._owner.poisoned = value
    def close(self): raise Refused('Borrowed legacy context cannot close owner')
    def host_guard(self): raise Refused('Locked helper cannot reacquire host guard')
    def atomic(self, name, raw):
        if len(raw) > 16384: raise Refused('Recovery metadata capacity')
        # Same marker semantics; use the existing complete-write/poison writer.
        return DeliveryLedger._delivery_write(self, name, raw)

class _V5(_Borrowed, AdmissionLedger):
    pass

class _V6(_Borrowed, DeliveryLedger):
    pass


def _healthy(owner):
    if owner.poisoned: raise Refused('V7 storage poisoned')


def _directory(owner, directory):
    _healthy(owner)
    actual = os.fstat(directory)
    expected = os.stat('admissions-v1', dir_fd=owner.fd, follow_symlinks=False)
    if (not stat.S_ISDIR(actual.st_mode) or actual.st_uid != os.getuid()
        or stat.S_IMODE(actual.st_mode) != 0o700
        or (actual.st_dev, actual.st_ino) != (expected.st_dev, expected.st_ino)):
        raise Refused('Exact locked admissions directory required')


def _decode(raw):
    if raw is None: raise Refused('Required legacy state missing')
    return json.loads(raw, object_pairs_hook=unique)


def _marker(view, name, expected, *, create=False):
    raw = view.raw(view.fd, name, 4096)
    if raw is None:
        if not create: raise Refused('Legacy initialization marker missing')
        view.atomic(name, encoded(expected))
    else:
        value = _decode(raw)
        if value != expected or type(value.get('schema')) is not int:
            raise Refused('Legacy initialization marker mismatch')


def _initialize_delivery(view, parent):
    name = 'release-deliveries-v1.json'
    marker = 'release-deliveries-v1.initialized'
    raw = view.raw(view.fd, name, LIMIT)
    mark = view.raw(view.fd, marker, 4096)
    if raw is None:
        if mark is not None: raise Refused('Delivery sidecar missing after initialization')
        view._delivery_write(name, encoded({'schema': 1, 'lifetime': view.target['lifetime'], 'certificates': []}))
    else:
        state = view._delivery_validate(_decode(raw), parent)
        if mark is None and state['certificates']:
            raise Refused('Populated delivery marker missing')
    expected = {'schema': 1, 'lifetime': view.target['lifetime'], 'kind': 'release-deliveries-initialized'}
    if mark is None: view._delivery_write(marker, encoded(expected))
    elif _decode(mark) != expected or type(_decode(mark).get('schema')) is not int:
        raise Refused('Delivery initialization marker')
    return view._delivery_load(parent)


def initialize_v6_locked(owner, admissions_fd):
    """First activation only: complete exact old initialization, freeze return.

    Returns schema6 state, matching its actual file bytes. No active V7 can
    exist; caller writes its V7 envelope/marker before any effect is enabled.
    """
    _directory(owner, admissions_fd)
    try:
        if owner.raw(owner.fd, 'ledger-v7.json', LIMIT) is not None or owner.raw(owner.fd, 'ledger-v7.initialized', 4096) is not None:
            raise Refused('V6 bootstrap forbidden after V7 publication')
        v6 = _V6(owner)
        raw6 = v6.raw(v6.fd, 'ledger-v6.json', LIMIT)
        if raw6 is None:
            if v6.raw(v6.fd, 'ledger-v6.initialized', 4096) is not None:
                raise Refused('Retirement ledger missing')
            v5 = _V5(owner)
            raw5 = v5.raw(v5.fd, 'ledger-v5.json', LIMIT)
            if raw5 is None:
                if v5.raw(v5.fd, 'ledger-v5.initialized', 4096) is not None:
                    raise Refused('Predecessor missing')
                v5._bootstrap()
            else:
                v5._validate(_decode(raw5))
            v5._ensure_marker()
            state = v5._load()
            raw5 = v5.raw(v5.fd, 'ledger-v5.json', LIMIT)
            history = copy.deepcopy(state['settled'])
            latest = state['latest']
            if latest is not None and latest['status'] in ('Committed', 'Refused') and not any(key(r) == key(latest) for r in history):
                history.append(copy.deepcopy(latest))
            state.update(schema=6, v5SHA256=hashlib.sha256(raw5).hexdigest(), releases=[], settlementHistory=history)
            v6._save(state)
        else:
            v6._validate(_decode(raw6))
        _marker(v6, 'ledger-v6.initialized', {'schema': 1, 'lifetime': v6.target['lifetime'], 'kind': 'retirement-ledger-initialized'}, create=True)
        state = v6._sync(admissions_fd)
        changed = False
        for row in state['entries']:
            if row['status'] == 'Pending': row['status'] = 'Unknown'; changed = True
        if state['latest'] is not None and state['latest']['status'] == 'Pending':
            state['latest']['status'] = 'Unknown'; changed = True
        if changed: v6._save(state)
        _initialize_delivery(v6, state)
        os.fsync(owner.fd)
        persisted = _decode(v6.raw(v6.fd, 'ledger-v6.json', LIMIT))
        if persisted != state: raise Refused('V6 bootstrap bytes/state differ')
        return copy.deepcopy(state)
    except BaseException:
        owner.poisoned = True
        raise


def validate_delivery_locked(owner, legacy):
    """Read-only structural validation plus recovery durability barrier."""
    _healthy(owner)
    try:
        return copy.deepcopy(_V6(owner)._delivery_load(legacy))
    except BaseException:
        owner.poisoned = True
        raise


def _certified_records(owner, legacy, records):
    """Derive permitted destinations only from complete correlated certificates.

    Records remain ordinary Pending/Unknown in all legacy validators. A native
    Cancelled is never passed to normalize/validate or disguised as Refused.
    """
    if type(records) is not list or len(records) > 64:
        raise Refused('Cancellation record capacity')
    retired = {}
    seen = set()
    for record in records:
        # Exact complete V7 shape/attempt/ACK validation from its one schema owner.
        owner._validate_record(record)
        admission = record['admission']
        identity = key(admission)
        if identity in seen: raise Refused('Duplicate cancellation admission')
        seen.add(identity)
        matches = [r for r in legacy['entries'] if key(r) == identity]
        if record['stage'] != 'AdmissionRetired':
            if len(matches) != 1 or matches[0] != dict(admission, status=matches[0]['status']) or matches[0]['status'] not in ('Pending', 'Unknown'):
                raise Refused('Active cancellation must own exact live reservation')
        elif matches:
            raise Refused('Retired cancellation cannot remain live')
        cert = record['certificate']
        if cert is None: continue
        if 'prepare' not in record['attemptedKinds']:
            raise Refused('Native terminal without durable preparation attempt')
        response = cert['response']
        canonical(record['deadlineMonotonicNs'])
        prepared = record['prepared']
        prepared_id = prepared['preparedId'] if prepared is not None else response.get('preparedId')
        value = CancellationEndpoint._cancellation_wire(copy.deepcopy(response), admission['binding'], admission['intent'], record['deadlineMonotonicNs'], prepared_id)
        if value['kind'] != 'effect-outcome' or value['status'] not in ('Committed', 'Refused', 'Cancelled'):
            raise Refused('Complete native terminal certificate required')
        if cert['sha256'] != hashlib.sha256(encoded(value)).hexdigest():
            raise Refused('Cancellation certificate bytes changed')
        mark = next((m for m in legacy['watermarks'] if m['binding'] == admission['binding']), None)
        if mark is None or int(mark['request']) < int(admission['intent']['request']) or int(mark['generation']) < int(admission['intent']['generation']):
            raise Refused('Cancellation allocation watermark missing')
        if record['stage'] == 'AdmissionRetired': retired[identity] = record
    return retired


# V6 validator extraction; only certified destination coverage/collision additions.
def _validate_extended_v6(self, state, retired):
    fields=['schema','lifetime','entries','watermarks','bootstrapHashes','latest','predecessorName','predecessorSHA256','settled','v5SHA256','releases','settlementHistory']
    exact(state,fields)
    if type(state['schema']) is not int or state['schema'] != 6: raise Refused('Retirement ledger schema')
    raw5=self.raw(self.fd,'ledger-v5.json',LIMIT)
    if raw5 is None or state['v5SHA256'] != hashlib.sha256(raw5).hexdigest(): raise Refused('Predecessor producer changed')
    predecessor=AdmissionLedger._validate(self,json.loads(raw5,object_pairs_hook=unique))
    releases=state['releases']
    if not isinstance(releases,list) or len(releases)>64: raise Refused('Historical release capacity')
    seen=set(); live={key(r):r for r in state['entries']}
    for release in releases:
        exact(release,['id','record','proof','observation','phase'])
        value=release_payload(release['record'],release['proof'],release['observation'])
        if release['id'] != hashlib.sha256(encoded(value)).hexdigest() or key(value['record']) in seen: raise Refused('Historical release identity')
        seen.add(key(value['record']))
        if release['phase'] not in ['Prepared','Released']: raise Refused('Release phase')
        old=live.get(key(value['record']))
        if release['phase']=='Prepared' and old != value['record']: raise Refused('Prepared must remain reserved')
        if release['phase']=='Released' and old is not None: raise Refused('Released cannot remain live')
        mark=next((m for m in state['watermarks'] if m['binding']==value['record']['binding']),None)
        if mark is None or int(mark['request'])<int(value['record']['intent']['request']) or int(mark['generation'])<int(value['record']['intent']['generation']): raise Refused('Historical allocation watermark')
    if set(retired) & (set(live) | seen): raise Refused('Cancellation/legacy disposition collision')
    history=state['settlementHistory']
    if not isinstance(history,list) or len(history)>64: raise Refused('Definitive history capacity')
    definitive={}
    for r in history:
        validate(r)
        if r['schema']!=2 or r['status'] not in ['Committed','Refused'] or r['binding']['lifetime']!=state['lifetime'] or key(r) in seen or key(r) in live or key(r) in definitive:
            raise Refused('Historical outcome consistency')
        definitive[key(r)]=r
        mark=next((m for m in state['watermarks'] if m['binding']==r['binding']),None)
        if mark is None or int(mark['request'])<int(r['intent']['request']) or int(mark['generation'])<int(r['intent']['generation']): raise Refused('Definitive allocation watermark')
    if set(retired) & set(definitive): raise Refused('Cancellation/legacy definitive collision')
    for r in state['settled']:
        if key(r) in seen or definitive.get(key(r))!=r: raise Refused('Settlement must match definitive history')
    if any(key(r) not in set(live)|seen|set(definitive)|set(retired) for r in predecessor['entries']): raise Refused('Migrated reservation lost')
    for r in predecessor['settled']+([predecessor['latest']] if predecessor['latest'] is not None and predecessor['latest']['status'] in ['Committed','Refused'] else []):
        if definitive.get(key(r))!=r: raise Refused('Migrated definitive history lost')
    for prior in predecessor['watermarks']:
        mark=next((m for m in state['watermarks'] if m['binding']==prior['binding']),None)
        if mark is None or int(mark['request'])<int(prior['request']) or int(mark['generation'])<int(prior['generation']): raise Refused('Migrated watermark decreased')
    view={k:copy.deepcopy(state[k]) for k in fields if k not in ['v5SHA256','releases','settlementHistory']}; view['schema']=5
    latest=state['latest']
    if latest is not None and latest['status'] in ['Committed','Refused'] and definitive.get(key(latest))!=latest: raise Refused('Latest definitive history correlation')
    if latest is not None and any(r['phase']=='Released' and r['record']==latest for r in releases): view['latest']=None
    AdmissionLedger._validate(self,view)
    if len(encoded(state))>LIMIT: raise Refused('Retirement byte capacity')
    return state


def _history_transition(before, after, retired):
    """Original V6 save invariants plus exact typed cancellation destinations."""
    releases = {r['id']: r for r in after['releases']}
    for row in before['releases']:
        new = releases.get(row['id'])
        if new is None or {k: v for k, v in new.items() if k != 'phase'} != {k: v for k, v in row.items() if k != 'phase'} or (row['phase'] == 'Released' and new['phase'] != 'Released'):
            raise Refused('Release history cannot disappear or regress')
    history = {key(r): r for r in after['settlementHistory']}
    if any(history.get(key(r)) != r for r in before['settlementHistory']):
        raise Refused('Definitive history cannot disappear')
    destinations = {key(r) for r in after['entries'] + after['settlementHistory']} | {key(r['record']) for r in after['releases'] if r['phase'] == 'Released'} | set(retired)
    if any(key(r) not in destinations for r in before['entries']):
        raise Refused('Live reservation cannot disappear without disposition')
    for row in before['entries']:
        cert = retired.get(key(row))
        if cert is not None and dict(row, status='Pending') != cert['admission']:
            raise Refused('Certificate does not dispose exact historical reservation')
    for prior in before['watermarks']:
        mark = next((m for m in after['watermarks'] if m['binding'] == prior['binding']), None)
        if mark is None or int(mark['request']) < int(prior['request']) or int(mark['generation']) < int(prior['generation']):
            raise Refused('Allocation watermark cannot decrease')


def validate_v7_legacy_locked(owner, legacy_v6_dict, predecessor_v6_bytes, cancellation_records):
    _healthy(owner)
    try:
        view = _V6(owner)
        actual = view.raw(view.fd, 'ledger-v6.json', LIMIT)
        if actual is None or actual != predecessor_v6_bytes:
            raise Refused('Frozen V6 predecessor differs')
        _marker(view, 'ledger-v6.initialized', {'schema': 1, 'lifetime': owner.target['lifetime'], 'kind': 'retirement-ledger-initialized'})
        predecessor = _decode(actual)
        typed = {key(row['admission']) for row in cancellation_records}
        if any(key(row['record']) in typed for row in legacy_v6_dict['releases']):
            raise Refused('Legacy release collides with typed cancellation custody')
        # Unmodified original validator on the actual predecessor, always.
        RetirementLedger._validate(view, predecessor)
        retired = _certified_records(owner, legacy_v6_dict, cancellation_records)
        _validate_extended_v6(view, legacy_v6_dict, retired)
        _history_transition(predecessor, legacy_v6_dict, retired)
        view._delivery_load(legacy_v6_dict)
        return copy.deepcopy(legacy_v6_dict)
    except BaseException:
        owner.poisoned = True
        raise


def _validate_v7_transition_locked(owner, before, after):
    """MANDATORY before every replacement of a populated V7, not just bootstrap.

    Both envelopes must already pass owner._validate_v7_locked. This function
    does no writes and preserves intermediate V7 history absent from frozen V6.
    """
    _healthy(owner)
    old = owner.raw(owner.fd, 'ledger-v6.json', LIMIT)
    owner._validate_v7_locked(before, old)
    owner._validate_v7_locked(after, old)
    retired = _certified_records(owner, after['legacy'], after['cancellations'])
    _history_transition(before['legacy'], after['legacy'], retired)
    new = {r['key']: r for r in after['cancellations']}
    for prior in before['cancellations']:
        row = new.get(prior['key'])
        if row is None: raise Refused('Cancellation history cannot disappear')
        for field in ('admission', 'deadlineMonotonicNs'):
            if row[field] != prior[field]: raise Refused('Cancellation original identity changed')
        if not set(prior['attemptedKinds']).issubset(row['attemptedKinds']) or (prior['commitAttempted'] and not row['commitAttempted']):
            raise Refused('Mutation attempt history cannot regress')
        if prior['prepared'] is not None and row['prepared'] != prior['prepared']:
            raise Refused('Preparation identity cannot change')
        if prior['certificate'] is not None and row['certificate'] != prior['certificate']:
            raise Refused('Terminal certificate cannot change')
        if prior['stage'] == 'AdmissionRetired' and row['stage'] != 'AdmissionRetired':
            raise Refused('Retired admission cannot reopen')
        rank = {'NotSent': 0, 'Pending': 1, 'Acknowledged': 2}
        if rank[row['ackState']] < rank[prior['ackState']]: raise Refused('ACK state cannot regress')
        if prior['acknowledgement'] is not None and row['acknowledgement'] != prior['acknowledgement']:
            raise Refused('Stored ACK cannot change')


def validate_v7_transition_locked(owner, before, after):
    try:
        return _validate_v7_transition_locked(owner, before, after)
    except BaseException:
        owner.poisoned = True
        raise


def finish_certificate_locked(owner, admissions_fd, identifier):
    """Finish ONLY a certificate already durably stored in actual active V7.

    No native call or ACK. Caller must hold host_guard once. The V7 writer must
    include validate_v7_transition_locked; returning means BOTH directory
    barriers completed. The durable certificate remains after any failure.
    """
    _directory(owner, admissions_fd)
    try:
        state = owner._current_v7_locked()
        rows = [r for r in state['cancellations'] if r['key'] == identifier]
        if len(rows) != 1 or rows[0]['stage'] not in ('TerminalStored', 'AdmissionRetired') or rows[0]['certificate'] is None:
            raise Refused('Durable exact terminal certificate required')
        record = rows[0]
        # Revalidate certificate/state, then reestablish durable envelope before
        # unlink even when its rename was only visible after an interruption.
        validate_v7_legacy_locked(owner, state['legacy'], owner.raw(owner.fd, 'ledger-v6.json', LIMIT), state['cancellations'])
        os.fsync(owner.fd)
        admission = record['admission']
        name = storage_key(admission) + '.json'
        raw = owner.raw(admissions_fd, name, 4096)
        if raw is not None:
            value = normalize(_decode(raw))
            if value != admission or value['status'] != 'Pending':
                raise Refused('Exact certified admission retirement correlation')
            os.unlink(name, dir_fd=admissions_fd)
        os.fsync(admissions_fd)
        if record['stage'] == 'TerminalStored':
            old = copy.deepcopy(state)
            legacy = state['legacy']
            legacy['entries'] = [r for r in legacy['entries'] if key(r) != key(admission)]
            if legacy['latest'] is not None and key(legacy['latest']) == key(admission):
                legacy['latest'] = None
            record['stage'] = 'AdmissionRetired'
            validate_v7_transition_locked(owner, old, state)
            owner._write_v7_locked(state)
        return copy.deepcopy(state)
    except BaseException:
        owner.poisoned = True
        raise
