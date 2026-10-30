"""Private typed host-settlement proposal, unexecuted.

Shape validation is NOT producer authentication. Only the owned daemon backend
may supply the C receiver; local cached receipts must have passed that receiver.
Uses the frozen companion helper; never modifies legacy outcome validators.
"""
import copy
import hashlib
from endpoint import Refused, binding, canonical, exact
from durable_ledger import encoded
from recovery_journal import validate
from cancellation_endpoint import CancellationEndpoint
from cancellation_host_admission import validate_companion, decode

MAX_FRAME = 8192
_ACK_RANK = {'NotSent':0, 'Pending':1, 'Acknowledged':2}
_FIELDS = ('protocolVersion','kind','cancellationHostProtocol','binding','key',
           'admission','selection','deadlineMonotonicNs','preparedId',
           'certificate','localStage','ackState','acknowledgement','executionAuthorized')


def validate_settlement(frame, companion, current_delivery_binding):
    """Already-parsed exact DTO plus exact persisted local companion.

    No Pending file is required here: a real daemon has already retired it.
    AdmissionRetired is accepted only on the separately authenticated backend.
    """
    exact(frame, _FIELDS)
    companion = validate_companion(companion)
    current = binding(current_delivery_binding)
    if (type(frame['protocolVersion']) is not int or frame['protocolVersion'] != 3 or
            type(frame['cancellationHostProtocol']) is not int or frame['cancellationHostProtocol'] != 1 or
            frame['kind'] != 'host-cancellation-settled' or
            binding(frame['binding']) != current or
            frame['executionAuthorized'] is not False or
            frame['localStage'] != 'AdmissionRetired'):
        raise Refused('Host cancellation settlement delivery/stage')
    validate(frame['admission'])  # Python bool/int equality is not schema validation.
    if (frame['key'] != companion['key'] or frame['admission'] != companion['admission'] or
            frame['selection'] != companion['selection'] or
            frame['deadlineMonotonicNs'] != companion['selection']['deadlineMonotonicNs']):
        raise Refused('Host cancellation settlement local origin')
    original = companion['admission']['binding']
    if current['lifetime'] != original['lifetime']:
        raise Refused('Host cancellation settlement lifetime')
    canonical(frame['preparedId']); canonical(frame['deadlineMonotonicNs'])
    intent = companion['admission']['intent']
    cert = CancellationEndpoint._cancellation_wire(
        frame['certificate'], original, intent, frame['deadlineMonotonicNs'], frame['preparedId'])
    if cert['kind'] != 'effect-outcome' or cert['status'] not in ('Committed','Refused','Cancelled'):
        raise Refused('Host cancellation settlement lacks known native terminal')
    state = frame['ackState']
    if type(state) is not str or state not in _ACK_RANK:
        raise Refused('Host cancellation settlement ACK state')
    if state == 'Acknowledged':
        CancellationEndpoint._cancellation_wire(
            frame['acknowledgement'], original, intent, frame['deadlineMonotonicNs'],
            frame['preparedId'], ack=True)
    elif frame['acknowledgement'] is not None:
        raise Refused('Host cancellation settlement unexpected ACK')
    if len(encoded(frame)) > MAX_FRAME:
        raise Refused('Host cancellation settlement byte bound')
    return copy.deepcopy(frame)


def decode_settlement(raw, companion, current_delivery_binding):
    if type(raw) is not bytes or len(raw) > MAX_FRAME:
        raise Refused('Host cancellation settlement bytes')
    return validate_settlement(decode(raw), companion, current_delivery_binding)


def make_settlement(validated_v7_record, companion, current_delivery_binding):
    """Call ONLY on a record from _current_v7_locked, under one host_guard.

    Full V7 validation/authenticated native evidence precedes this projection;
    this small function deliberately does not duplicate the V7 state validator.
    Caller also verifies local admission retirement still holds under that guard.
    """
    r = validated_v7_record
    if r['stage'] != 'AdmissionRetired' or r['certificate'] is None:
        raise Refused('Host settlement requires completed local retirement')
    cert = r['certificate']
    exact(cert, ('response','sha256'))
    if cert['sha256'] != hashlib.sha256(encoded(cert['response'])).hexdigest():
        raise Refused('Host settlement stored certificate digest')
    if (r['key'] != companion['key'] or r['admission'] != companion['admission'] or
            r['deadlineMonotonicNs'] != companion['selection']['deadlineMonotonicNs']):
        raise Refused('Host settlement stored record differs from companion')
    frame = {
        'protocolVersion':3, 'kind':'host-cancellation-settled',
        'cancellationHostProtocol':1, 'binding':copy.deepcopy(current_delivery_binding),
        'key':r['key'], 'admission':copy.deepcopy(r['admission']),
        'selection':copy.deepcopy(companion['selection']),
        'deadlineMonotonicNs':r['deadlineMonotonicNs'],
        'preparedId':cert['response']['preparedId'], 'certificate':copy.deepcopy(cert['response']),
        'localStage':'AdmissionRetired', 'ackState':r['ackState'],
        'acknowledgement':copy.deepcopy(r['acknowledgement']), 'executionAuthorized':False,
    }
    return validate_settlement(frame, companion, current_delivery_binding)


def merge_previously_accepted(previous, incoming, companion, current_delivery_binding):
    """C-cache algorithm counterpart; previous must be trusted durable local bytes.

    No producer-authentication exemption: only receiver-accepted cache bytes may
    be passed as previous, never an arbitrary frontend frame or V7 input file.
    """
    new = validate_settlement(incoming, companion, current_delivery_binding)
    if previous is None: return new
    old = validate_settlement(previous, companion, previous['binding'])
    stable = set(_FIELDS) - {'binding','ackState','acknowledgement'}
    if any(old[field] != new[field] for field in stable):
        raise Refused('Host settlement terminal identity changed')
    if old['ackState'] == new['ackState'] and old['acknowledgement'] != new['acknowledgement']:
        raise Refused('Host settlement ACK changed')
    return old if _ACK_RANK[old['ackState']] > _ACK_RANK[new['ackState']] else new
