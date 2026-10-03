"""Pure durable direction reconstruction. A returned plan grants no native authority."""
from dataclasses import dataclass, asdict
import re
from direction import Direction, compose


def positive(value):
    if type(value) is not int or not 0 < value < 2**63:
        raise ValueError('positive typed bounded receipt/PID required')
    return value


def identity(value):
    if not isinstance(value, (tuple, list)) or len(value) != 3:
        raise ValueError('exact recovery identity required')
    address, sid, pid = value
    if (type(address) is not str or re.fullmatch(r'0x[0-9a-f]{1,16}', address) is None
            or type(sid) is not str or re.fullmatch(r'[0-9a-f]{1,16}', sid) is None):
        raise ValueError('canonical exact recovery identity required')
    return address, sid, positive(pid)


def direction(value):
    if not isinstance(value, dict) or set(value) != {'anchor', 'inverted', 'identity'}:
        raise ValueError('complete symbolic direction required')
    if type(value['inverted']) is not bool:
        raise ValueError('typed direction inversion required')
    captured = identity(value['identity']) if value['identity'] is not None else None
    result = Direction(value['anchor'], value['inverted'], captured)
    if (result.constant is None) != (captured is not None):
        raise ValueError('anchored direction must carry its exact captured identity')
    return result


@dataclass(frozen=True)
class RecoveryIntent:
    receipt: int
    members: frozenset
    direction: Direction

    def endpoint(self, windows, active=None):
        # No client list is fetched here; the runtime must establish its fresh
        # selected-session family/workspace/output/geometry proof separately.
        observed = {}
        for window in windows:
            captured = identity([window['address'], window['stableId'], window['pid']])
            if captured in observed:
                raise ValueError('duplicate fresh recovery family identity')
            if window.get('mapped', True) is not True:
                raise ValueError('unmapped recovery identity')
            observed[captured] = window
        if set(observed) != self.members:
            raise ValueError('fresh complete recovery family changed')
        if self.direction.constant:
            return self.direction.constant
        if self.direction.identity not in observed:
            raise ValueError('captured direction identity missing/reused')
        if self.direction.anchor == 'activate':
            if active is not None:
                active = identity(active)
                if active[0] in {k[0] for k in observed} and active not in observed:
                    raise ValueError('active address belongs to a reused exact identity')
            # None is a fresh observation of no active client; the underlying
            # Direction requires a non-None sentinel to distinguish no query.
            active_address = active[0] if active is not None else ''
        else:
            active_address = None
        return self.direction.resolve(observed[self.direction.identity], active_address)


def reconstruct(ledger, members, durable_serial):
    serial = positive(durable_serial)
    if not isinstance(ledger, dict) or set(ledger) != {'anchors', 'events', 'receipts'}:
        raise ValueError('complete durable accepted intent ledger required')
    if any(not isinstance(ledger[name], list) or len(ledger[name]) > 512 for name in ledger):
        raise ValueError('bounded complete accepted intent lists required')
    family = frozenset(identity(member) for member in members)
    if not 1 <= len(family) <= 64 or len(family) != len(members):
        raise ValueError('bounded distinct complete fresh family required')
    owners = {}
    for row in ledger['receipts']:
        if not isinstance(row, list) or len(row) != 2:
            raise ValueError('complete exact receipt ownership required')
        captured, receipt = identity(row[0]), positive(row[1])
        if captured in owners or receipt > serial:
            raise ValueError('duplicate/future receipt ownership')
        owners[captured] = receipt
    anchors = {}
    anchored_members = set()
    for row in ledger['anchors']:
        if not isinstance(row, dict) or set(row) != {'identity', 'receipt', 'direction'}:
            raise ValueError('complete direction anchor required')
        captured, receipt, intent = identity(row['identity']), positive(row['receipt']), direction(row['direction'])
        if captured in anchored_members or receipt > serial:
            raise ValueError('duplicate/future direction anchor')
        anchored_members.add(captured)
        if captured in family:
            if receipt in anchors and anchors[receipt] != intent:
                raise ValueError('conflicting compressed family direction')
            anchors[receipt] = intent
    if len(anchors) > 1:
        raise ValueError('previous accepted family scopes require atomic replacement')
    baseline = max(anchors, default=0)
    intent = anchors.get(baseline)
    latest = baseline
    events = {}
    for row in ledger['events']:
        if not isinstance(row, dict) or set(row) != {'receipt', 'captured', 'command'}:
            raise ValueError('complete direction event required')
        receipt, captured = positive(row['receipt']), identity(row['captured'])
        if receipt in events or receipt > serial:
            raise ValueError('duplicate/future direction event')
        if row['command'] not in ('minimize', 'restore', 'toggle', 'activate'):
            raise ValueError('invalid accepted command')
        events[receipt] = captured, row['command']
    for receipt, (captured, command) in sorted(events.items()):
        if baseline < receipt and captured in family:
            intent = compose(command, intent, captured=captured)
            latest = receipt
    if intent is None or latest == 0:
        raise ValueError('unresolved family has no durable accepted direction')
    if max((r for k, r in owners.items() if k in family), default=0) != latest:
        raise ValueError('latest family receipt and direction provenance differ')
    if intent.identity is not None and intent.identity not in family:
        raise ValueError('direction anchor belongs to another fresh family')
    return RecoveryIntent(latest, family, intent)


def snapshot_intent(manager):
    """Copy the actual manager ledger under its reservation lock, never mutate it."""
    with manager.lock:
        return {
            'anchors': [{'identity':list(captured),'receipt':receipt,'direction':asdict(intent)}
                        for captured,(receipt,intent) in sorted(manager.intent_anchors.items())],
            'events': [{'receipt':receipt,'captured':list(event['captured']),'command':event['command']}
                       for receipt,event in sorted(manager.intent_events.items())],
            'receipts': [[list(captured),receipt] for captured,receipt in sorted(manager.receipts.items())],
        }
