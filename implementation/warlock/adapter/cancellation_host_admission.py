"""Private strict companion reader proposal. No locks, writes, sends or replay.

Caller holds the existing host_guard ONCE. `owner.raw` is production Journal.raw.
Existing legacy validators are reused unchanged; this is not a V6 exception.
"""
import copy
import json
import re
from endpoint import Refused, binding, canonical, exact, unique
from recovery_journal import validate
from admission_ledger import storage_key
from cancellation_endpoint import CancellationEndpoint

DIRECTORY = 'cancellation-admissions-v1'
MAX_BYTES = 8192
MAX_RECORDS = 64
BUDGET_NS = 2_000_000_000


def decode(raw):
    if type(raw) is not bytes or not raw or len(raw) > MAX_BYTES or b'\0' in raw:
        raise Refused('Cancellation host record bytes')
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=unique,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError('constant')))
    except (UnicodeError, ValueError, RecursionError) as error:
        raise Refused('Cancellation host record JSON') from error
    def visit(node, depth=0):
        if depth > 6:
            raise Refused('Cancellation host record depth')
        if isinstance(node, dict):
            for key, child in node.items():
                if '\0' in key: raise Refused('Cancellation host record NUL')
                visit(child, depth+1)
        elif isinstance(node, list):
            raise Refused('Cancellation host record array')
        elif isinstance(node, str) and '\0' in node:
            raise Refused('Cancellation host record NUL')
    visit(value)
    return value


def validate_companion(value, *, submitted=True):
    exact(value, ('schema','kind','state','key','admission','selection'))
    if (type(value['schema']) is not int or value['schema'] != 1 or
            value['kind'] != 'host-cancellation-admission' or
            value['state'] not in ('Reserved','Submitted') or
            (submitted and value['state'] != 'Submitted')):
        raise Refused('Cancellation host companion state')
    admission = validate(value['admission'])
    if admission['schema'] != 2 or admission['effectProtocol'] != 1 or admission['status'] != 'Pending':
        raise Refused('Cancellation host Pending required')
    bound = binding(admission['binding'])
    CancellationEndpoint._cancellation_intent(admission['intent'], bound)
    if value['key'] != storage_key(admission):
        raise Refused('Cancellation host companion key')
    selection = value['selection']
    exact(selection, ('selectionId','scope','publication','lease','controlId',
                      'clock','acceptedMonotonicNs','deadlineMonotonicNs'))
    if type(selection['selectionId']) is not str or not re.fullmatch(r'[0-9a-f]{32}',selection['selectionId']):
        raise Refused('Cancellation host selection identity')
    exact(selection['scope'], ('id','generation'))
    for field in ('id','generation'): canonical(selection['scope'][field])
    for field in ('publication','lease','acceptedMonotonicNs','deadlineMonotonicNs'):
        canonical(selection[field])
    control = selection['controlId']
    if type(control) is not str or not control or '\0' in control:
        raise Refused('Cancellation host control')
    try: control_bytes = control.encode('utf-8')
    except UnicodeError as error: raise Refused('Cancellation host control encoding') from error
    if len(control_bytes)>512 or selection['clock']!='CLOCK_MONOTONIC':
        raise Refused('Cancellation host control/clock')
    if int(selection['deadlineMonotonicNs']) - int(selection['acceptedMonotonicNs']) != BUDGET_NS:
        raise Refused('Cancellation host original deadline')
    return copy.deepcopy(value)


def validate_pair(companion_raw, pending_raw, bound, intent, deadline):
    """Exact schema/key/full Pending/D check, no deadline renewal or authority grant."""
    canonical(deadline)
    CancellationEndpoint._cancellation_intent(intent, binding(bound))
    companion = validate_companion(decode(companion_raw))
    pending = validate(decode(pending_raw))
    wanted = {'schema':2,'effectProtocol':1,'binding':bound,'intent':intent,'status':'Pending'}
    if (pending != wanted or companion['admission'] != wanted or
            companion['selection']['deadlineMonotonicNs'] != deadline):
        raise Refused('Cancellation host pair correlation')
    return companion


def read_pair_locked(owner, admissions_fd, companions_fd, bound, intent, deadline):
    """Already-locked hook inside cancellation_reserve BEFORE _sync/mutation.

    Both directory fds must already be verified private directories under the
    same lifetime namespace. This does not open/reacquire host_guard. Missing,
    partial or malformed data refuses; startup must never call this to send.
    """
    wanted = {'schema':2,'effectProtocol':1,'binding':copy.deepcopy(bound),
              'intent':copy.deepcopy(intent),'status':'Pending'}
    identifier = storage_key(wanted)
    companion_raw = owner.raw(companions_fd, identifier+'.json', MAX_BYTES)
    pending_raw = owner.raw(admissions_fd, identifier+'.json', 4096)
    return validate_pair(companion_raw, pending_raw, bound, intent, deadline)


def scan_locked(owner, companions_fd):
    """Bounded strict inventory, including incomplete Reserved records.

    Integration checks these reservations before *all* new legacy/cancellable
    admissions. A partial record is never invisible to target custody. Terminal
    release is established from the existing strict V7 certificate path, not a
    caller-supplied list of exempt keys. Unexpected crash debris fails closed.
    """
    import os
    names = os.listdir(companions_fd)
    if len(names)>MAX_RECORDS: raise Refused('Cancellation companion capacity')
    records=[]; selections=set()
    for name in sorted(names):
        if not re.fullmatch(r'[0-9a-f]{64}\.json',name):
            raise Refused('Cancellation companion filename')
        item = validate_companion(decode(owner.raw(companions_fd,name,MAX_BYTES)), submitted=False)
        if name != item['key']+'.json' or item['selection']['selectionId'] in selections:
            raise Refused('Cancellation companion filename/selection reuse')
        selections.add(item['selection']['selectionId']); records.append(item)
    return records
