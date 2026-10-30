"""Opt-in coordinator for durable attempts and current native cancellation grants.

Only the selected authenticated client's strict replies become store evidence.
Historical records remain informational; native calls never hold host_guard.
"""
import copy
import threading

from endpoint import Refused, binding, canonical, exact
from cancellation_ledger import _native_cancellation_evidence
from recovery_journal import guarded


class CancellationCoordinator:
    """Own one negotiated current grant and serialize durable/native ordering."""
    def __init__(self, client, recovery, hello, *, settlement_sink):
        if not callable(settlement_sink):
            raise Refused('Owned backend settlement sink required')
        self.settlement_sink = settlement_sink
        self.client = client
        self.recovery = recovery
        if (not isinstance(hello, dict) or type(hello.get('protocolVersion')) is not int
                or hello['protocolVersion'] != 3 or hello.get('kind') != 'attached'):
            raise Refused('Validated cancellation hello required')
        self.bound = copy.deepcopy(binding(client.bound))
        if binding(hello.get('binding')) != self.bound:
            raise Refused('Cancellation hello binding differs')
        self.negotiated = False
        self.owned = {}  # strict in-process client handles, never restored as authority
        self.acks = {}
        self.poisoned = False
        self.lock = threading.Lock()
        self.attached = False
        self.closed = False
        # The caller passes only the response of this selected client's strict
        # hello. Never attach from a frontend frame or a stored record.
        try:
            guarded(lambda: self.recovery.cancellation_attach(copy.deepcopy(self.bound)))
            self.attached = True
        except Exception:
            self.poisoned = True
            raise

    def _detach_locked(self):
        if self.closed:
            return
        try:
            if self.attached:
                guarded(self.recovery.cancellation_detach)
        except BaseException:
            self.poisoned = True
            raise
        finally:
            self.attached = False
            self.closed = True
            self.negotiated = False
            self.owned.clear()
            self.acks.clear()

    def close(self):
        with self.lock:
            self._detach_locked()

    def _live(self):
        if self.poisoned or self.closed or not self.attached:
            raise Refused('Cancellation coordinator requires recovery')
        try:
            current = binding(self.client.bound)
        except Exception as error:
            self._detach_locked()
            raise Refused('Cancellation binding lost') from error
        if current != self.bound:
            self._detach_locked()
            raise Refused('Cancellation binding changed')

    def _store(self, method, *args):
        self._live()
        try:
            return guarded(lambda: method(*args))
        except Exception:
            self.poisoned = True
            raise

    def _attempted(self, record):
        """Require the reviewed durable monotone attemptedKinds representation."""
        if not isinstance(record, dict) or any(k not in record for k in ('attemptedKinds', 'commitAttempted', 'lastOperation')):
            self.poisoned = True
            raise Refused('Cancellation attemptedKinds is required')
        kinds = record['attemptedKinds']
        if (type(kinds) is not list or any(type(k) is not str or k not in ('prepare', 'commit', 'cancel') for k in kinds)
                or len(set(kinds)) != len(kinds) or type(record['commitAttempted']) is not bool
                or record['commitAttempted'] != ('commit' in kinds)):
            self.poisoned = True
            raise Refused('Invalid cancellation attemptedKinds')
        return frozenset(kinds)

    def _attempt(self, record, operation):
        before = self._attempted(record)
        # Store must reject a consumed commit atomically under host_guard.
        # Merely returning an existing record does not authorize transport.
        if operation == 'commit' and 'commit' in before:
            raise Refused('Cancellation commit already attempted')
        updated = self._store(self.recovery.cancellation_attempt, record['key'], operation)
        after = self._attempted(updated)
        if (updated.get('key') != record['key'] or updated.get('admission') != record['admission']
                or updated.get('deadlineMonotonicNs') != record['deadlineMonotonicNs']
                or not before.issubset(after) or operation not in after):
            self.poisoned = True
            raise Refused('Cancellation durable attempt confirmation differs')
        return updated

    def startup(self):
        """Complete only local, already-certified retirement before attached."""
        with self.lock:
            self._live()
            for record in self._store(self.recovery.cancellation_snapshot, self.bound):
                self._attempted(record)
                if record['stage'] == 'TerminalStored':
                    completed = self._store(self.recovery.cancellation_finish, record['key'])
                    if not self._attempted(record).issubset(self._attempted(completed)):
                        self.poisoned = True
                        raise Refused('Cancellation attemptedKinds regressed during startup')
            return (self._store(self.recovery.cancellation_recovery_frames, self.bound)
                    + self._store(self.recovery.cancellation_settlement_frames, self.bound))

    def _emit_settlement_locked(self, key):
        frames = self._store(self.recovery.cancellation_settlement_frames, self.bound)
        matches = [frame for frame in frames if frame['key'] == key]
        if len(matches) != 1:
            self.poisoned = True
            raise Refused('Exact typed host settlement unavailable')
        try:
            # Every short store guard ended before touching owned backend I/O.
            self.settlement_sink(copy.deepcopy(matches[0]))
        except Exception:
            self.poisoned = True
            self._detach_locked()
            raise

    def _record(self, request):
        records = self._store(self.recovery.cancellation_snapshot, self.bound)
        matches = [r for r in records if r['admission']['binding'] == self.bound
                   and r['admission']['effectProtocol'] == request['effectProtocol']
                   and r['admission']['intent'] == request['intent']
                   and r['deadlineMonotonicNs'] == request['deadlineMonotonicNs']]
        if len(matches) != 1:
            raise Refused('Cancellation key not owned by current binding')
        record = matches[0]
        self._attempted(record)
        prepared = record['prepared'] or record['lastObserved']
        if prepared is None or prepared['preparedId'] != request['preparedId']:
            raise Refused('Cancellation prepared identity differs')
        owned = self.owned.get(record['key'])
        if owned is None or owned['preparedId'] != request['preparedId']:
            raise Refused('No live native preparation for current grant')
        return record, owned

    def _observed(self, original, response, phase, prepared_id):
        key = original['key']
        evidence = _native_cancellation_evidence(original['admission'], original['deadlineMonotonicNs'], prepared_id, response, phase=phase)
        if evidence.key != key:
            self.poisoned = True
            raise Refused('Cancellation evidence key differs')
        record = self._store(self.recovery.cancellation_observe, key, evidence)
        if not self._attempted(original).issubset(self._attempted(record)):
            self.poisoned = True
            raise Refused('Cancellation attemptedKinds regressed after observation')
        if response['kind'] != 'effect-outcome' or response['status'] == 'Unknown':
            return copy.deepcopy(response)
        if response['status'] not in ('Committed', 'Refused', 'Cancelled'):
            raise Refused('Unexpected cancellation terminal')
        prior_attempted = self._attempted(record)
        record = self._store(self.recovery.cancellation_finish, key)
        if not prior_attempted.issubset(self._attempted(record)):
            self.poisoned = True
            raise Refused('Cancellation attemptedKinds regressed during retirement')
        if record['stage'] != 'AdmissionRetired':
            self.poisoned = True
            raise Refused('Cancellation admission was not durably retired')
        # The store returns the exact terminal mapping after durable ACK-pending.
        # Reject any deviation from the strict client response.
        certificate = self._store(self.recovery.cancellation_ack_pending, key)
        if certificate != response:
            self.poisoned = True
            raise Refused('Cancellation terminal certificate representation differs')
        self._emit_settlement_locked(key)
        try:
            ack = self.client.ack_effect_decision(copy.deepcopy(response))
            self._live()
        except Exception:
            self.poisoned = True
            self._detach_locked()
            raise
        acknowledged = self._store(self.recovery.cancellation_acknowledged, key, ack)
        if not self._attempted(record).issubset(self._attempted(acknowledged)):
            self.poisoned = True
            raise Refused('Cancellation attemptedKinds regressed after ACK')
        self.acks[key] = copy.deepcopy(ack)
        self._emit_settlement_locked(key)
        return copy.deepcopy(response)

    def handle(self, request, workspace_navigation=None):
        with self.lock:
            self._live()
            if not isinstance(request, dict):
                raise Refused('Cancellation request object')
            kind = request.get('kind')
            if kind == 'host-cancellation-receipt-request':
                import re
                exact(request, ('protocolVersion','kind','cancellationHostProtocol','binding','effectProtocol','intent','selectionId','deadlineMonotonicNs'))
                if (type(request['protocolVersion']) is not int or request['protocolVersion'] != 3 or
                    type(request['cancellationHostProtocol']) is not int or request['cancellationHostProtocol'] != 1 or
                    type(request['effectProtocol']) is not int or request['effectProtocol'] != 1 or
                    binding(request['binding']) != self.bound):
                    raise Refused('Cancellation receipt scope')
                self.client._cancellation_intent(request['intent'], self.bound)
                canonical(request['deadlineMonotonicNs'])
                selection = request['selectionId']
                if type(selection) is not str or not re.fullmatch(r'[0-9a-f]{32}', selection):
                    raise Refused('Cancellation selection identity')
                result = self._store(self.recovery.cancellation_receipt_lookup, self.bound,
                                     copy.deepcopy(request['intent']), request['deadlineMonotonicNs'], selection)
                if result is not None and result['stage'] == 'AdmissionRetired' and result['certificate'] is not None:
                    self._emit_settlement_locked(result['key'])
                return {'protocolVersion':3,'kind':'host-cancellation-receipt','cancellationHostProtocol':1,
                        'binding':copy.deepcopy(self.bound),'effectProtocol':1,'intent':copy.deepcopy(request['intent']),
                        'selectionId':selection,'deadlineMonotonicNs':request['deadlineMonotonicNs'],
                        'executionAuthorized':False,'record':copy.deepcopy(result)}
            common = ['protocolVersion', 'kind', 'binding', 'cancellationProtocol']
            if kind == 'effect-cancellation-negotiate':
                exact(request, common + ['requestId'])
            elif kind == 'effect-prepare':
                exact(request, common + ['effectProtocol', 'intent', 'deadlineMonotonicNs'])
            elif kind in ('effect-commit', 'effect-cancel', 'effect-decision-request', 'effect-decision-ack'):
                exact(request, common + ['effectProtocol', 'intent', 'deadlineMonotonicNs', 'preparedId'])
            else:
                raise Refused('Unsupported cancellation request')
            if (type(request['protocolVersion']) is not int or request['protocolVersion'] != 3
                    or type(request['cancellationProtocol']) is not int or request['cancellationProtocol'] != 1
                    or binding(request['binding']) != self.bound):
                raise Refused('Cancellation request scope')
            if kind == 'effect-cancellation-negotiate':
                canonical(request['requestId'])
                try:
                    response = self.client.cancellation_negotiate(request['requestId'])
                    self._live()
                except Exception:
                    self.poisoned = True
                    self._detach_locked()
                    raise
                self.negotiated = True
                return response
            if not self.negotiated or type(request['effectProtocol']) is not int or request['effectProtocol'] != 1:
                raise Refused('Cancellation not negotiated')
            self.client._cancellation_intent(request['intent'], self.bound)
            canonical(request['deadlineMonotonicNs'])
            if kind == 'effect-prepare':
                if workspace_navigation is not None and self._store(workspace_navigation.blocked):
                    raise Refused('Workspace navigation unresolved')
                result = self._store(self.recovery.cancellation_reserve, self.bound,
                                     copy.deepcopy(request['intent']), request['deadlineMonotonicNs'])
                record = result['record']; key = record['key']
                self._attempted(record)
                if not result['submitPrepare']:
                    if key not in self.owned:
                        raise Refused('Historical cancellation is informational only')
                    prior = record['lastObserved']
                    if prior is None:
                        raise Refused('Previously admitted cancellation remains unconfirmed')
                    if prior.get('kind') == 'effect-outcome' and prior.get('status') != 'Unknown':
                        if record['ackState'] != 'Acknowledged':
                            raise Refused('Stored terminal has not been acknowledged')
                    elif key not in self.owned:
                        raise Refused('No live cancellation handle; observation only')
                    return copy.deepcopy(prior)
                record = self._attempt(record, 'prepare')
                try:
                    response = self.client.prepare_effect(copy.deepcopy(request['intent']), request['deadlineMonotonicNs'])
                    self._live()
                    self.owned[key] = copy.deepcopy(response)
                    return self._observed(record, response, 'initial', None)
                except Exception:
                    self.poisoned = True
                    self._detach_locked()
                    raise
            canonical(request['preparedId'])
            record, prepared = self._record(request)
            key = record['key']
            if kind == 'effect-decision-ack':
                # Terminal ACK is performed only by _observed after durable finish.
                # A repeated frontend ACK does not itself call native.
                if record['ackState'] != 'Acknowledged' or key not in self.acks:
                    raise Refused('Cancellation decision not acknowledged on this live grant')
                return copy.deepcopy(self.acks[key])
            if record['stage'] == 'AdmissionRetired':
                terminal = record['lastObserved']
                if (record['ackState'] != 'Acknowledged' or key not in self.acks
                        or terminal is None or terminal.get('kind') != 'effect-outcome'
                        or terminal.get('status') not in ('Committed', 'Refused', 'Cancelled')):
                    raise Refused('Durable terminal unavailable on this live grant')
                return copy.deepcopy(terminal)
            if kind == 'effect-commit' and 'commit' in self._attempted(record):
                prior = record['lastObserved']
                if prior is None:
                    raise Refused('Commit attempted; native outcome remains unconfirmed')
                return copy.deepcopy(prior)
            if kind in ('effect-commit', 'effect-cancel'):
                if (record['stage'] != 'Prepared' or
                        (record['lastObserved'] is not None and
                         record['lastObserved'].get('kind') == 'effect-outcome' and
                         record['lastObserved'].get('status') == 'Unknown')):
                    raise Refused('Cancellation mutation requires a live prepared record')
                operation = 'commit' if kind == 'effect-commit' else 'cancel'
                record = self._attempt(record, operation)
                call = self.client.commit_effect if operation == 'commit' else self.client.cancel_effect
            else:
                call = self.client.query_effect_decision
            try:
                response = call(copy.deepcopy(prepared))
                self._live()
                self.owned[key] = copy.deepcopy(response)
                return self._observed(record, response, 'established', prepared['preparedId'])
            except Exception:
                self.poisoned = True
                self._detach_locked()
                raise
