"""Opt-in V7 cancellation custody, strict evidence and durable attempt gates.

The authenticated coordinator supplies native evidence; decoding cannot establish
transport identity. Legacy persistence remains the default. This store performs
no native calls and does not enable the daemon or frontend cancellation route.
"""
from copy import deepcopy
from dataclasses import dataclass, replace
import json
from cancellation_endpoint import CancellationEndpoint, _REFUSALS as _CANCELLATION_REFUSALS
from endpoint import Refused, binding, canonical, exact, unique

# Immutable canonical byte snapshots prevent caller mutation after validation.
def _encode(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('ascii')

@dataclass(frozen=True, slots=True)
class ExpectedKey:
    _binding: bytes
    _intent: bytes
    deadline: str
    prepared_id: str | None

    def __post_init__(self):
        if type(self._binding) is not bytes or type(self._intent) is not bytes:
            raise Refused('Invalid cancellation key representation')
        try:
            bound = json.loads(self._binding, object_pairs_hook=unique)
            intent = json.loads(self._intent, object_pairs_hook=unique)
            binding(bound); CancellationEndpoint._cancellation_intent(intent, bound)
            canonical(self.deadline)
            if self.prepared_id is not None: canonical(self.prepared_id)
            if _encode(bound) != self._binding or _encode(intent) != self._intent:
                raise Refused('Noncanonical cancellation key representation')
        except (ValueError, TypeError, UnicodeDecodeError) as error:
            raise Refused('Malformed cancellation key representation') from error

    @classmethod
    def from_values(cls, bound, intent, deadline, prepared_id=None):
        bound = deepcopy(bound)
        intent = deepcopy(intent)
        binding(bound)
        CancellationEndpoint._cancellation_intent(intent, bound)
        canonical(deadline)
        if prepared_id is not None:
            canonical(prepared_id)
        return cls(_encode(bound), _encode(intent), deadline, prepared_id)

    def bound(self):
        return json.loads(self._binding, object_pairs_hook=unique)

    def intent(self):
        return json.loads(self._intent, object_pairs_hook=unique)

@dataclass(frozen=True, slots=True)
class Receipt:
    _wire: bytes
    kind: str
    status: str | None
    prepared_id: str
    raw_wire: bytes | None = None

    def __post_init__(self):
        if type(self._wire) is not bytes or (self.raw_wire is not None and type(self.raw_wire) is not bytes):
            raise Refused('Invalid receipt representation')
        try:
            frame = json.loads(self._wire, object_pairs_hook=unique)
            if not isinstance(frame, dict) or frame.get('kind') not in ('effect-prepared', 'effect-outcome'):
                raise Refused('Invalid receipt kind')
            key = ExpectedKey.from_values(frame.get('binding'), frame.get('intent'), frame.get('deadlineMonotonicNs'), frame.get('preparedId'))
            valid = CancellationEndpoint._cancellation_wire(frame, key.bound(), key.intent(), key.deadline, key.prepared_id)
            if _encode(valid) != self._wire or self.kind != frame['kind'] or self.status != frame.get('status') or self.prepared_id != frame['preparedId']:
                raise Refused('Receipt representation mismatch')
            if self.raw_wire is not None and json.loads(self.raw_wire, object_pairs_hook=unique) != frame:
                raise Refused('Receipt original bytes mismatch')
        except (ValueError, TypeError, UnicodeDecodeError, RecursionError) as error:
            raise Refused('Malformed receipt representation') from error

    def value(self):
        """Return a new copy of the exact schema-defined native fields."""
        return json.loads(self._wire, object_pairs_hook=unique)

    @property
    def terminal(self):
        return self.kind == 'effect-outcome' and self.status in ('Committed', 'Refused', 'Cancelled')

def parse_receipt(value, expected, *, phase):
    """Correlate an already-decoded native prepared/outcome to the full key.

    `expected` must originate in authenticated caller state, not be constructed
    from the same untrusted response. An unassigned prepared_id is valid only
    when correlating the initial prepare response. This does not confer ownership.
    """
    if type(expected) is not ExpectedKey:
        raise Refused('Expected cancellation key required')
    if phase not in ('initial', 'established') or (phase == 'initial') != (expected.prepared_id is None):
        raise Refused('Cancellation receipt phase and preparation identity')
    if not isinstance(value, dict) or value.get('kind') not in ('effect-prepared', 'effect-outcome'):
        raise Refused('Prepared or outcome response required')
    result = CancellationEndpoint._cancellation_wire(
        deepcopy(value), expected.bound(), expected.intent(), expected.deadline,
        expected.prepared_id)
    return Receipt(_encode(result), result['kind'], result.get('status'), result['preparedId'])

def parse_receipt_json(raw, expected, *, phase):
    """Decode bounded bytes with duplicate-key rejection before schema checks."""
    if type(raw) is not bytes or not raw or len(raw) > 65536:
        raise Refused('Cancellation response byte bound')
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=unique,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite')))
    except (ValueError, UnicodeDecodeError, RecursionError) as error:
        raise Refused('Malformed cancellation response') from error
    parsed = parse_receipt(value, expected, phase=phase)
    return replace(parsed, raw_wire=bytes(raw))

@dataclass(frozen=True, slots=True)
class NativeCancellationEvidence:
    """Private coordinator evidence wrapper; not a signature or persistence token.

    The coordinator alone must create this immediately after a successful strict
    client call on its authenticated live grant. Never construct it from frontend
    request dictionaries. Python module privacy is an application boundary, not
    a security sandbox.
    """
    key: str
    admission_bytes: bytes
    response: Receipt

    def admission(self):
        return json.loads(self.admission_bytes, object_pairs_hook=unique)

def _native_cancellation_evidence(admission, deadline, prepared_id, response, *, phase):
    """Coordinator-only factory; authentication must already have happened."""
    from admission_ledger import storage_key
    from recovery_journal import validate
    admission = deepcopy(admission)
    validate(admission)
    if admission['schema'] != 2 or admission['effectProtocol'] != 1 or admission['status'] != 'Pending':
        raise Refused('Exact legacy Pending restore admission required')
    expected = ExpectedKey.from_values(admission['binding'], admission['intent'], deadline, prepared_id)
    parsed = parse_receipt(response, expected, phase=phase)
    return NativeCancellationEvidence(storage_key(admission), _encode(admission), parsed)

# Incremental V7 bootstrap. Legacy validation is delegated ONLY to the explicit
# already-held-lock seam. No network calls or legacy object grafting occur here.
import hashlib
import os
import secrets
from delivery_ledger import DeliveryLedger
from recovery_journal import Journal, validate
from admission_ledger import storage_key
from durable_ledger import encoded, normalize, key as legacy_key, watermark
from retirement_ledger import ObservationJoin, release_payload

_NAME = 'ledger-v7.json'
_MARKER = 'ledger-v7.initialized'
_PREDECESSOR = 'ledger-v6.json'
_LIMIT = 1048576
_CAPACITY = 64
_STAGES = frozenset(('Reserved', 'Prepared', 'Uncertain', 'TerminalStored', 'AdmissionRetired'))
_ACKS = frozenset(('NotSent', 'Pending', 'Acknowledged'))
_OPERATIONS = ('prepare', 'commit', 'cancel')

# This is a size envelope only: never persist/emit these maximum-valued objects
# as native evidence. Every number comes from the strict wire/record schemas.
_MAX_WIRE_COUNTER = str((1 << 64) - 1)

def _future_record_bytes(record):
    """Upper bound for this immutable key's complete future record, in bytes.

    Counter strings are <=20 ASCII digits by endpoint.canonical. The only free
    native reason is actually a member of the finite strict client vocabulary.
    All remaining JSON fields are exact shape, bounded enums, booleans or the
    immutable admission/deadline. encoded() is the actual persistent serializer.
    """
    common = {
        'protocolVersion': 3, 'cancellationProtocol': 1, 'effectProtocol': 1,
        'binding': deepcopy(record['admission']['binding']),
        'intent': deepcopy(record['admission']['intent']),
        'preparedId': _MAX_WIRE_COUNTER,
        'deadlineMonotonicNs': record['deadlineMonotonicNs'],
    }
    prepared = dict(common, kind='effect-prepared')
    terminals = [dict(common, kind='effect-outcome', status=status, reason=reason,
                      revision=_MAX_WIRE_COUNTER, outputGeneration=_MAX_WIRE_COUNTER)
                 for status, reason in [('Committed', 'applied'),
                                        ('Cancelled', 'cancelled-before-commit'),
                                        *[('Refused', reason) for reason in _CANCELLATION_REFUSALS]]]
    terminal = max(terminals, key=lambda value: len(encoded(value)))
    unknown = dict(common, kind='effect-outcome', status='Unknown', reason='effect-unproven',
                   revision=_MAX_WIRE_COUNTER, outputGeneration=_MAX_WIRE_COUNTER)
    observed = max([prepared, unknown, terminal], key=lambda value: len(encoded(value)))
    # Per-field maxima form a conservative size envelope, not a valid state.
    # false is one byte longer than true even though the maximal attempts list
    # contains commit. ACK may coexist with historical prepared/certificate.
    maximum = {
        'key': record['key'], 'admission': deepcopy(record['admission']),
        'deadlineMonotonicNs': record['deadlineMonotonicNs'],
        'stage': max(_STAGES, key=lambda value: len(encoded(value))),
        'prepared': prepared, 'lastObserved': observed,
        'certificate': {'response': terminal, 'sha256': 'f' * (hashlib.sha256().digest_size * 2)},
        'ackState': max(_ACKS, key=lambda value: len(encoded(value))),
        'attemptedKinds': list(_OPERATIONS), 'commitAttempted': False,
        'lastOperation': max(_OPERATIONS, key=lambda value: len(encoded(value))),
        'acknowledgement': dict(common, kind='effect-decision-acknowledged'),
    }
    return len(encoded(maximum))

def _reserved_envelope_bytes(state):
    """Fund all retained records at once; other writes cannot spend this credit."""
    actual = len(encoded(state))
    growth = sum(max(0, _future_record_bytes(record) - len(encoded(record)))
                 for record in state['cancellations'])
    return actual + growth


class CancellationLedger(DeliveryLedger):
    """Single V7 envelope over immutable V6, with one shared host guard.

    `cancellation_legacy` is a required separately reviewed extraction of V6
    locked validation/bootstrap. Its API must never treat bare caller keys as
    authorization to erase a reservation. Until installed, construction fails.
    """
    _supports_cancellation_v7 = True

    def __init__(self, runtime, instance, lifetime):
        self.poisoned = False
        self._live_cancellation_binding = None
        self._live_cancellation_keys = set()
        import cancellation_legacy as legacy_helpers
        self._legacy_helpers = legacy_helpers
        Journal.__init__(self, runtime, instance, lifetime)
        try:
            with self.host_guard() as directory:
                raw = self.raw(self.fd, _NAME, _LIMIT)
                marker = self.raw(self.fd, _MARKER, 4096)
                if raw is None:
                    if marker is not None:
                        raise Refused('V7 missing after initialization')
                    legacy = legacy_helpers.initialize_v6_locked(self, directory)
                    old = self.raw(self.fd, _PREDECESSOR, _LIMIT)
                    if old is None:
                        raise Refused('V7 predecessor missing')
                    predecessor = json.loads(old, object_pairs_hook=unique)
                    if predecessor != legacy:
                        raise Refused('V6 bootstrap must match frozen bytes')
                    state = {'schema': 7, 'lifetime': lifetime,
                             'predecessorV6SHA256': hashlib.sha256(old).hexdigest(),
                             'legacy': deepcopy(legacy), 'cancellations': []}
                    self._validate_v7_locked(state, old)
                    self._write_v7_locked(state)
                    raw = self.raw(self.fd, _NAME, _LIMIT)
                state = self._decode_v7_locked(raw)
                expected = {'schema': 1, 'lifetime': lifetime,
                            'kind': 'cancellation-ledger-initialized',
                            'predecessorV6SHA256': state['predecessorV6SHA256']}
                if marker is None:
                    # Recovery of interrupted initialization is safe only for the
                    # exact initial envelope with no typed activity or V6 delta.
                    old = self.raw(self.fd, _PREDECESSOR, _LIMIT)
                    if state['cancellations'] or state['legacy'] != json.loads(old, object_pairs_hook=unique):
                        raise Refused('Populated V7 initialization marker missing')
                    os.fsync(self.fd)
                    self._write_file_locked(_MARKER, encoded(expected), 4096)
                else:
                    actual = json.loads(marker, object_pairs_hook=unique)
                    if actual != expected or type(actual.get('schema')) is not int:
                        raise Refused('V7 initialization marker mismatch')
                    os.fsync(self.fd)
                legacy_helpers.validate_delivery_locked(self, state['legacy'])
                # Certified retirements precede any ordinary import on restart.
                for item in state['cancellations']:
                    if item['stage'] in ('TerminalStored', 'AdmissionRetired'):
                        legacy_helpers.finish_certificate_locked(self, directory, item['key'])
                # Preserve the legacy restart contract in the active V7 view.
                # Only custody status changes: typed admission keys and native
                # evidence remain immutable, and no old capability is attached.
                legacy = self._sync(directory)
                changed = False
                for row in legacy['entries']:
                    if row['status'] == 'Pending':
                        row['status'] = 'Unknown'
                        changed = True
                if legacy['latest'] is not None and legacy['latest']['status'] == 'Pending':
                    legacy['latest']['status'] = 'Unknown'
                    changed = True
                if changed:
                    self._save(legacy)
        except BaseException:
            self.poisoned = True
            self.close()
            raise

    def _validate_record(self, record):
        fields = ('key', 'admission', 'deadlineMonotonicNs', 'stage', 'prepared',
                  'lastObserved', 'certificate', 'ackState', 'attemptedKinds',
                  'commitAttempted', 'lastOperation', 'acknowledgement')
        exact(record, fields)
        admission = record['admission']
        validate(admission)
        if admission['schema'] != 2 or admission['effectProtocol'] != 1 or admission['status'] != 'Pending':
            raise Refused('V7 requires exact protocol1 Pending admission')
        bound = binding(admission['binding'])
        CancellationEndpoint._cancellation_intent(admission['intent'], bound)
        if bound['lifetime'] != self.target['lifetime'] or record['key'] != storage_key(admission):
            raise Refused('V7 cancellation key/scope')
        canonical(record['deadlineMonotonicNs'])
        if type(record['stage']) is not str or type(record['ackState']) is not str or record['stage'] not in _STAGES or record['ackState'] not in _ACKS:
            raise Refused('V7 cancellation stage')
        kinds = record['attemptedKinds']
        if type(kinds) is not list or any(type(x) is not str or x not in _OPERATIONS for x in kinds) or len(kinds) != len(set(kinds)):
            raise Refused('V7 attempted kinds')
        if type(record['commitAttempted']) is not bool or record['commitAttempted'] != ('commit' in kinds):
            raise Refused('V7 commit attempt correlation')
        if record['lastOperation'] is not None and (type(record['lastOperation']) is not str or record['lastOperation'] not in _OPERATIONS):
            raise Refused('V7 last operation')
        if record['lastOperation'] is not None and record['lastOperation'] not in kinds:
            raise Refused('V7 last operation without attempt')
        prepared = record['prepared']; observed = record['lastObserved']; cert = record['certificate']
        if (prepared is not None or observed is not None or cert is not None or 'commit' in kinds or 'cancel' in kinds) and 'prepare' not in kinds:
            raise Refused('V7 native evidence requires durable preparation attempt')
        if ('commit' in kinds or 'cancel' in kinds) and prepared is None:
            raise Refused('V7 mutation attempt requires exact prepared receipt')
        prepared_id = None
        if prepared is not None:
            expected = ExpectedKey.from_values(bound, admission['intent'], record['deadlineMonotonicNs'])
            value = parse_receipt(prepared, expected, phase='initial')
            if value.kind != 'effect-prepared':
                raise Refused('V7 prepared response kind')
            prepared_id = value.prepared_id
        if observed is not None:
            candidate_id = prepared_id if prepared_id is not None else None
            key = ExpectedKey.from_values(bound, admission['intent'], record['deadlineMonotonicNs'], candidate_id)
            outcome = parse_receipt(observed, key, phase='established' if candidate_id else 'initial')
            if prepared_id is not None and outcome.prepared_id != prepared_id:
                raise Refused('V7 observation preparation mismatch')
        if cert is not None:
            exact(cert, ('response', 'sha256'))
            response = cert['response']
            key = ExpectedKey.from_values(bound, admission['intent'], record['deadlineMonotonicNs'], prepared_id)
            outcome = parse_receipt(response, key, phase='established' if prepared_id else 'initial')
            if not outcome.terminal or cert['sha256'] != hashlib.sha256(encoded(response)).hexdigest():
                raise Refused('V7 terminal certificate correlation')
            if response['status'] == 'Committed' and not record['commitAttempted']:
                raise Refused('V7 committed receipt requires durable commit attempt')
            if observed != response:
                raise Refused('V7 terminal observation mismatch')
        if (record['stage'] in ('TerminalStored', 'AdmissionRetired')) != (cert is not None):
            raise Refused('V7 terminal stage correlation')
        if record['ackState'] != 'NotSent' and record['stage'] != 'AdmissionRetired':
            raise Refused('V7 ACK before admission retirement')
        ack = record['acknowledgement']
        if record['ackState'] == 'Acknowledged':
            if cert is None or ack is None:
                raise Refused('V7 acknowledged response missing')
            CancellationEndpoint._cancellation_wire(ack, bound, admission['intent'], record['deadlineMonotonicNs'], cert['response']['preparedId'], ack=True)
        elif ack is not None:
            raise Refused('V7 unexpected acknowledged response')
        if record['stage'] == 'Prepared' and prepared is None:
            raise Refused('V7 prepared stage without receipt')
        return record

    def _validate_v7_locked(self, state, old):
        exact(state, ('schema', 'lifetime', 'predecessorV6SHA256', 'legacy', 'cancellations'))
        if type(state['schema']) is not int or state['schema'] != 7 or state['lifetime'] != self.target['lifetime']:
            raise Refused('V7 schema or lifetime')
        if old is None or state['predecessorV6SHA256'] != hashlib.sha256(old).hexdigest():
            raise Refused('V6 predecessor drift')
        records = state['cancellations']
        if type(records) is not list or len(records) > _CAPACITY:
            raise Refused('V7 cancellation capacity')
        keys = set()
        for record in records:
            self._validate_record(record)
            if record['key'] in keys:
                raise Refused('Duplicate V7 cancellation key')
            keys.add(record['key'])
        self._legacy_helpers.validate_v7_legacy_locked(self, state['legacy'], old, records)
        if len(encoded(state)) > _LIMIT:
            raise Refused('V7 byte capacity')
        if _reserved_envelope_bytes(state) > _LIMIT:
            raise Refused('V7 future terminal capacity not reserved')
        return state

    def _decode_v7_locked(self, raw):
        if raw is None:
            raise Refused('V7 ledger missing')
        return self._validate_v7_locked(json.loads(raw, object_pairs_hook=unique), self.raw(self.fd, _PREDECESSOR, _LIMIT))

    def _write_file_locked(self, name, raw, limit):
        if self.poisoned or len(raw) > limit:
            raise Refused('V7 storage poisoned or capacity exceeded')
        temp = 'cancellation-v7-pending-' + secrets.token_hex(12)
        fd = None
        try:
            fd = os.open(temp, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=self.fd)
            offset = 0
            while offset < len(raw):
                try: size = os.write(fd, raw[offset:])
                except InterruptedError: continue
                if size <= 0: raise OSError('V7 write made no progress')
                offset += size
            os.fsync(fd); closing = fd; fd = None; os.close(closing)
            os.replace(temp, name, src_dir_fd=self.fd, dst_dir_fd=self.fd)
            os.fsync(self.fd)
        except BaseException:
            self.poisoned = True
            raise
        finally:
            try:
                if fd is not None: os.close(fd)
            except BaseException:
                self.poisoned = True
                raise
            finally:
                try: os.unlink(temp, dir_fd=self.fd)
                except FileNotFoundError: pass
                except BaseException: self.poisoned = True; raise

    def _write_v7_locked(self, state):
        self._validate_v7_locked(state, self.raw(self.fd, _PREDECESSOR, _LIMIT))
        previous = self.raw(self.fd, _NAME, _LIMIT)
        if previous is not None:
            before = self._decode_v7_locked(previous)
            self._legacy_helpers.validate_v7_transition_locked(self, before, state)
        self._write_file_locked(_NAME, encoded(state), _LIMIT)

    def _current_v7_locked(self):
        if self.poisoned:
            raise Refused('V7 storage requires explicit recovery')
        marker = self.raw(self.fd, _MARKER, 4096)
        if marker is None:
            raise Refused('V7 marker missing')
        state = self._decode_v7_locked(self.raw(self.fd, _NAME, _LIMIT))
        expected = {'schema': 1, 'lifetime': self.target['lifetime'],
                    'kind': 'cancellation-ledger-initialized',
                    'predecessorV6SHA256': state['predecessorV6SHA256']}
        if json.loads(marker, object_pairs_hook=unique) != expected:
            raise Refused('V7 marker mismatch')
        return state

    def _record_locked(self, state, identifier):
        if type(identifier) is not str or len(identifier) != 64 or any(c not in '0123456789abcdef' for c in identifier):
            raise Refused('V7 key')
        records = [item for item in state['cancellations'] if item['key'] == identifier]
        if len(records) != 1:
            raise Refused('V7 unknown or ambiguous key')
        return records[0]

    def _require_live_record(self, record):
        # The selected authenticated connection must explicitly attach.
        bound = getattr(self, '_live_cancellation_binding', None)
        if bound is None or binding(bound) != record['admission']['binding']:
            raise Refused('Exact current cancellation grant not established')
        identifier = record.get('key')
        if identifier is not None and identifier not in self._live_cancellation_keys:
            raise Refused('Cancellation record is not owned by this live attachment')

    def cancellation_observe(self, identifier, evidence):
        if type(evidence) is not NativeCancellationEvidence:
            raise Refused('Authenticated coordinator evidence required')
        with self.host_guard():
            state = self._current_v7_locked()
            record = self._record_locked(state, identifier)
            self._require_live_record(record)
            if 'prepare' not in record['attemptedKinds']:
                raise Refused('Native observation before durable preparation attempt')
            if evidence.key != identifier or evidence.admission() != record['admission']:
                raise Refused('V7 native evidence admission mismatch')
            response = evidence.response.value()
            bound = record['admission']['binding']; intent = record['admission']['intent']
            old_prepared = record['prepared']
            known_id = old_prepared['preparedId'] if old_prepared is not None else None
            expected = ExpectedKey.from_values(bound, intent, record['deadlineMonotonicNs'], known_id)
            receipt = parse_receipt(response, expected, phase='established' if known_id else 'initial')
            if receipt.status == 'Committed' and not record['commitAttempted']:
                raise Refused('Committed observation before durable commit attempt')
            old_observed = record['lastObserved']
            if old_observed is not None and old_observed['preparedId'] != response['preparedId']:
                self.poisoned = True
                raise Refused('V7 observed preparation identity changed')
            prior = record['certificate']
            if prior is not None:
                if receipt.value() != prior['response']:
                    self.poisoned = True
                    raise Refused('V7 conflicting or regressing terminal evidence')
                return deepcopy(record)
            if receipt.kind == 'effect-prepared':
                if old_prepared is not None and old_prepared != response:
                    self.poisoned = True
                    raise Refused('V7 conflicting prepared receipt')
                record['prepared'] = deepcopy(response)
                record['stage'] = 'Prepared'
            elif receipt.terminal:
                record['certificate'] = {'response': deepcopy(response),
                    'sha256': hashlib.sha256(encoded(response)).hexdigest()}
                record['stage'] = 'TerminalStored'
            else:
                record['stage'] = 'Uncertain'
            record['lastObserved'] = deepcopy(response)
            # In particular, no observation may erase a consumed commit attempt.
            self._write_v7_locked(state)
            return deepcopy(record)

    def cancellation_ack_pending(self, identifier):
        with self.host_guard():
            state = self._current_v7_locked(); record = self._record_locked(state, identifier)
            self._require_live_record(record)
            if record['stage'] != 'AdmissionRetired' or record['certificate'] is None:
                raise Refused('Terminal and retired admission required before ACK')
            if record['ackState'] == 'Acknowledged':
                raise Refused('V7 terminal already acknowledged')
            if record['ackState'] != 'Pending':
                record['ackState'] = 'Pending'
                self._write_v7_locked(state)
            # Return only after the directory-fsync barrier in _write_v7_locked.
            return deepcopy(record['certificate']['response'])

    def cancellation_acknowledged(self, identifier, ack):
        with self.host_guard():
            state = self._current_v7_locked(); record = self._record_locked(state, identifier)
            self._require_live_record(record)
            if record['stage'] != 'AdmissionRetired' or record['certificate'] is None or record['ackState'] not in ('Pending','Acknowledged'):
                raise Refused('V7 ACK not admitted')
            cert = record['certificate']['response']; bound = record['admission']['binding']
            value = CancellationEndpoint._cancellation_wire(deepcopy(ack), bound, record['admission']['intent'],
                        record['deadlineMonotonicNs'], cert['preparedId'], ack=True)
            if record['ackState'] == 'Acknowledged':
                if record['acknowledgement'] != value:
                    self.poisoned = True
                    raise Refused('V7 acknowledged response changed')
                return deepcopy(record)
            record['acknowledgement'] = deepcopy(value)
            record['ackState'] = 'Acknowledged'
            self._write_v7_locked(state)
            return deepcopy(record)

    def cancellation_snapshot(self, bound):
        binding(bound)
        if bound['lifetime'] != self.target['lifetime']:
            raise Refused('V7 foreign lifetime')
        with self.host_guard():
            state = self._current_v7_locked()
            return deepcopy(state['cancellations'])

    def cancellation_attach(self, bound):
        """Caller authenticates the owned connection before attaching its full binding."""
        current = deepcopy(binding(deepcopy(bound)))
        if current['lifetime'] != self.target['lifetime']:
            raise Refused('V7 foreign live binding')
        with self.host_guard():
            self._current_v7_locked()
            if self._live_cancellation_binding is not None:
                raise Refused('Detach the previous live grant before attach')
            self._live_cancellation_binding = current
            self._live_cancellation_keys.clear()

    def cancellation_detach(self):
        with self.host_guard():
            self._live_cancellation_binding = None
            self._live_cancellation_keys.clear()

    def cancellation_attempt(self, identifier, operation):
        if operation not in _OPERATIONS:
            raise Refused('Invalid cancellation mutation')
        with self.host_guard():
            state = self._current_v7_locked()
            record = self._record_locked(state, identifier)
            self._require_live_record(record)
            if record['certificate'] is not None or operation in record['attemptedKinds']:
                raise Refused('Cancellation mutation already consumed or terminal')
            if operation == 'prepare':
                if record['stage'] != 'Reserved' or record['attemptedKinds']:
                    raise Refused('Prepare not available')
            elif record['prepared'] is None or record['stage'] not in ('Prepared', 'Uncertain'):
                raise Refused('Exact prepared identity required')
            if operation == 'commit' and record['commitAttempted']:
                raise Refused('Commit permission consumed')
            record['attemptedKinds'].append(operation)
            record['lastOperation'] = operation
            if operation == 'commit': record['commitAttempted'] = True
            record['stage'] = 'Uncertain'
            self._write_v7_locked(state)
            return deepcopy(record)

    def cancellation_finish(self, identifier):
        with self.host_guard() as directory:
            state = self._legacy_helpers.finish_certificate_locked(self, directory, identifier)
            return deepcopy(self._record_locked(state, identifier))

    def _require_legacy_key_locked(self, record):
        """Legacy proof never authorizes a typed cancellation disposition."""
        identity = legacy_key(record)
        state = self._current_v7_locked()
        if any(legacy_key(row['admission']) == identity for row in state['cancellations']):
            raise Refused('Typed cancellation requires its native certificate path')

    def _remove_admission(self, directory, record):
        # Parent _finish and replayed legacy _sync must check BEFORE unlink.
        self._require_legacy_key_locked(record)
        return super()._remove_admission(directory, record)

    def release(self, join):
        if type(join) is not ObservationJoin:
            raise Refused('Post-retirement join required')
        payload = release_payload(join.record, join.proof, join.observation())
        identifier = hashlib.sha256(encoded(payload)).hexdigest()
        with self.host_guard() as directory:
            self._require_legacy_key_locked(payload['record'])
            state = self._sync(directory)
            # Keep the parent V6 release semantics for genuine legacy keys.
            existing = next((row for row in state['releases'] if row['record'] == payload['record']), None)
            if existing is not None:
                return deepcopy(existing)
            if len(state['releases']) >= 64:
                raise Refused('Historical release capacity')
            matching = [row for row in state['entries'] if legacy_key(row) == legacy_key(payload['record'])]
            if len(matching) != 1 or matching[0] != payload['record']:
                raise Refused('Release must match stored Unknown')
            released = dict(payload, id=identifier, phase='Prepared')
            state['releases'].append(released)
            self._save(state)
            self._finish(directory, state, released)
            return deepcopy(released)

    def legacy_reconciliation_records(self):
        """Read-only legacy projection; typed records use cancellation recovery."""
        with self.host_guard() as directory:
            legacy = self._sync(directory)
            state = self._current_v7_locked()
            typed = {legacy_key(row['admission']) for row in state['cancellations']}
            records = legacy['entries'] + [deepcopy(row['record']) for row in legacy['releases'] if row['phase'] == 'Released']
            return deepcopy([row for row in records if legacy_key(row) not in typed])

    def _load(self):
        return deepcopy(self._current_v7_locked()['legacy'])

    def _save(self, legacy):
        state = self._current_v7_locked()
        state['legacy'] = deepcopy(legacy)
        self._write_v7_locked(state)

    def _sync(self, directory, exclude=None):
        """Already locked. Finish every certified retirement before import."""
        state = self._current_v7_locked()
        for row in state['cancellations']:
            if row['stage'] in ('TerminalStored', 'AdmissionRetired'):
                state = self._legacy_helpers.finish_certificate_locked(self, directory, row['key'])
        legacy = state['legacy']
        try:
            os.fsync(self.fd)
            # Existing release removals are exact and their original proof retained.
            for release in legacy['releases']:
                self._remove_admission(directory, release['record'])
                if release['phase'] == 'Prepared':
                    legacy['entries'] = [r for r in legacy['entries'] if legacy_key(r) != legacy_key(release['record'])]
                    release['phase'] = 'Released'
                    self._write_v7_locked(state)
            admitted = self.admissions(directory)
            present = {legacy_key(r) for r in admitted}
            if any(legacy_key(r) not in present for r in legacy['settled']): os.fsync(directory)
            before = encoded(state)
            legacy['settled'] = [r for r in legacy['settled'] if legacy_key(r) in present]
            for row in admitted:
                if exclude is not None and legacy_key(row) == legacy_key(exclude): continue
                if any(legacy_key(old) == legacy_key(row) for old in legacy['entries'] + legacy['settled']): continue
                latest = legacy['latest']
                if latest is not None and legacy_key(latest) == legacy_key(row) and latest['status'] in ('Committed', 'Refused'):
                    legacy['settled'].append(deepcopy(latest)); continue
                if any(old['intent']['incarnation'] == row['intent']['incarnation'] for old in legacy['entries']):
                    raise Refused('Admission conflicts with unresolved target')
                legacy['entries'].append(dict(row, status='Unknown'))
                self._mark(legacy, row)
            if encoded(state) != before: self._write_v7_locked(state)
            return deepcopy(legacy)
        except OSError:
            self.poisoned = True
            raise

    def cancellation_reserve(self, bound, intent, deadline):
        canonical(deadline)
        bound = deepcopy(binding(deepcopy(bound)))
        CancellationEndpoint._cancellation_intent(intent, bound)
        wanted = normalize({'schema': 2, 'binding': bound, 'intent': deepcopy(intent), 'effectProtocol': 1, 'status': 'Pending'})
        identifier = storage_key(wanted)
        with self.host_guard() as directory:
            self._require_live_record({'admission': wanted})
            from workspace_navigation import NAME as workspace_name, MARKER as workspace_marker, record as workspace_record
            raw = self.raw(self.fd, workspace_name, 4096)
            marker = self.raw(self.fd, workspace_marker, 4096)
            expected = {'schema': 1, 'lifetime': self.target['lifetime'], 'kind': 'workspace-navigation-initialized'}
            actual_marker = json.loads(marker, object_pairs_hook=unique) if marker is not None else None
            if raw is None or actual_marker != expected or type(actual_marker.get('schema')) is not int:
                raise Refused('Workspace navigation guard unavailable')
            workspace = json.loads(raw, object_pairs_hook=unique)
            if workspace is not None and workspace_record(workspace, self.target['lifetime'])['status'] in ('Pending', 'Unknown'):
                raise Refused('Workspace navigation unresolved')
            self._sync(directory, exclude=wanted)
            state = self._current_v7_locked()
            existing = [r for r in state['cancellations'] if r['key'] == identifier]
            if existing:
                if existing[0]['admission'] != wanted or existing[0]['deadlineMonotonicNs'] != deadline:
                    raise Refused('Existing cancellation differs')
                return {'record': deepcopy(existing[0]), 'submitPrepare': False}
            legacy = state['legacy']
            if any(r['admission']['binding'] == bound and r['ackState'] != 'Acknowledged' for r in state['cancellations']):
                raise Refused('Current binding already has an unacknowledged cancellation slot')
            if len(state['cancellations']) >= _CAPACITY or len(legacy['entries']) >= 64 or len(legacy['settlementHistory']) >= 64 or len(legacy['releases']) >= 64:
                raise Refused('Cancellation history or admission capacity')
            if any(r['proof']['queriedBinding'] == bound for r in legacy['releases']):
                raise Refused('Retired scope cannot submit a new effect')
            if not any(r == wanted for r in self.admissions(directory)):
                raise Refused('Exact durable Pending host admission required')
            if any(legacy_key(r) == legacy_key(wanted) or r['intent']['incarnation'] == intent['incarnation'] for r in legacy['entries']):
                raise Refused('Unresolved target or duplicate legacy admission')
            mark = next((m for m in legacy['watermarks'] if m['binding'] == bound), None)
            if mark is None:
                if len(legacy['watermarks']) >= 128: raise Refused('Allocation scope capacity')
                mark = watermark(bound, '0', '0'); legacy['watermarks'].append(mark)
            if int(intent['request']) <= int(mark['request']) or int(intent['generation']) <= int(mark['generation']):
                raise Refused('Allocation replay/order')
            mark.update(request=intent['request'], generation=intent['generation'])
            legacy['entries'].append(deepcopy(wanted)); legacy['latest'] = deepcopy(wanted)
            record = {'key': identifier, 'admission': wanted, 'deadlineMonotonicNs': deadline,
                      'stage': 'Reserved', 'prepared': None, 'lastObserved': None, 'certificate': None,
                      'ackState': 'NotSent', 'attemptedKinds': [], 'commitAttempted': False,
                      'lastOperation': None, 'acknowledgement': None}
            state['cancellations'].append(record)
            # Refuse while still under host_guard, before any durable permission
            # or native call. Every later write preserves the same headroom.
            if _reserved_envelope_bytes(state) > _LIMIT:
                raise Refused('V7 future terminal capacity not reserved')
            self._write_v7_locked(state)
            self._live_cancellation_keys.add(identifier)
            return {'record': deepcopy(record), 'submitPrepare': True}

    def _settle_record(self, row):
        # Legacy settlement must never consume a typed cancellation reservation.
        row = normalize(row)
        if row['status'] not in ('Committed', 'Refused', 'Unknown'):
            raise Refused('Admission receipt status')
        with self.host_guard() as directory:
            self._sync(directory)
            envelope = self._current_v7_locked()
            if any(item['key'] == storage_key(row) for item in envelope['cancellations']):
                raise Refused('Typed cancellation requires its exact terminal certificate')
            legacy = envelope['legacy']
            matching = [old for old in legacy['entries'] if legacy_key(old) == legacy_key(row)]
            if len(matching) != 1: raise Refused('Admission uncorrelated receipt')
            if row['status'] == 'Unknown': matching[0]['status'] = 'Unknown'
            else:
                if len(legacy['settled']) >= 64 or len(legacy['settlementHistory']) >= 64:
                    raise Refused('Definitive history capacity')
                legacy['entries'] = [old for old in legacy['entries'] if legacy_key(old) != legacy_key(row)]
                legacy['settled'].append(deepcopy(row)); legacy['settlementHistory'].append(deepcopy(row))
            if legacy['latest'] is not None and legacy_key(legacy['latest']) == legacy_key(row):
                legacy['latest'] = deepcopy(row)
            self._write_v7_locked(envelope)

    def cancellation_recovery_frames(self, bound):
        """Versioned historical reports only; never NativeOutcome or admission ACK.

        Outer binding routes this report to the current recipient. The complete
        original binding/key/deadline stays inside record unchanged. Even a
        same-binding report cannot attach, authorize execution, or ACK a slot.
        """
        current = deepcopy(binding(deepcopy(bound)))
        if current['lifetime'] != self.target['lifetime']:
            raise Refused('V7 foreign lifetime')
        with self.host_guard():
            state = self._current_v7_locked()
            frames = []
            for record in state['cancellations']:
                # _current_v7_locked validated full record, certificate and
                # predecessor, including monotone native terminal consistency.
                frame = {
                    'protocolVersion': 3, 'kind': 'host-cancellation-recovery',
                    'cancellationRecoveryProtocol': 1, 'binding': deepcopy(current),
                    'recoveryState': 'Terminal' if record['certificate'] is not None else 'Unknown',
                    'executionAuthorized': False, 'record': deepcopy(record),
                }
                # Same byte bound as the actual daemon OutputWriter frame.
                # No oversized partial list is returned to startup/send.
                if len(encoded(frame)) > _LIMIT:
                    raise Refused('Cancellation recovery frame byte capacity')
                frames.append(frame)
            return frames
