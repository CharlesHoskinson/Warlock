"""Opt-in native Restore cancellation. No durable storage or transport retry policy.

All methods require sequential use of one Endpoint. Retain a validated terminal
in durable caller-owned storage before ack_effect_decision; this class cannot
verify that persistence. Transport failures do not establish native outcome.
"""
from copy import deepcopy
from endpoint import Refused, binding, canonical, exact

_REFUSALS = frozenset({
    'original-deadline-expired', 'ambiguous-or-ineligible-restore-focus',
    'dependency-mismatch', 'exclusive-input', 'family-state-mismatch',
    'implicit-transfer-required', 'ineligible-family', 'ineligible-workspace-owner',
    'invalid-family', 'invalid-family-root', 'mixed-family-workspace-owner',
    'native-operation-bound', 'native-operation-unresolved', 'native-pointer-owned',
    'navigation-family-state-changed', 'navigation-recipient-changed',
    'navigation-refused', 'seat-grab', 'stale-incarnation', 'state-bound',
    'superseded-switcher-selection', 'switcher-cancelled-or-retired',
    'unsupported-operation', 'workspace-navigation-unresolved',
})
_COMMON = ('protocolVersion','kind','cancellationProtocol','effectProtocol',
           'binding','intent','preparedId','deadlineMonotonicNs')
_TERMINAL = ('status','reason','revision','outputGeneration')

class CancellationEndpoint:
    """Mixin for effect_endpoint.Endpoint; relies only on endpoint transport."""
    def _cancellation_reset(self):
        self._cancellation_binding = None
        self._cancellation_entry = None
        self._cancellation_terminal = None
        self._cancellation_observed = None

    def _cancellation_scope(self):
        if not self.bound:
            raise Refused('Handshake required')
        current = deepcopy(binding(self.bound))
        if getattr(self, '_cancellation_binding', None) != current:
            raise Refused('Cancellation negotiation required')
        return current

    @staticmethod
    def _cancellation_intent(intent, bound):
        exact(intent, ('request','generation','incarnation','operation','context'))
        exact(intent['context'], ('lifetime','epoch','output','revision'))
        for key in ('request','generation','incarnation'):
            canonical(intent[key])
        for value in intent['context'].values():
            canonical(value)
        if type(intent['operation']) is not str or intent['operation'] != 'restore':
            raise Refused('Unsupported cancellation operation')
        if intent['context']['lifetime'] != bound['lifetime'] or intent['context']['epoch'] != bound['frontend']:
            raise Refused('Cancellation intent authority')

    @staticmethod
    def _cancellation_wire(response, bound, intent, deadline, prepared_id=None, *, ack=False):
        if not isinstance(response, dict):
            raise Refused('Cancellation response type')
        kind = response.get('kind')
        if ack:
            expected_kind = 'effect-decision-acknowledged'
        elif kind == 'effect-prepared':
            expected_kind = 'effect-prepared'
        elif kind == 'effect-outcome':
            expected_kind = 'effect-outcome'
        else:
            raise Refused('Cancellation response kind')
        exact(response, (*_COMMON, *(_TERMINAL if expected_kind == 'effect-outcome' else ())))
        if (type(response['protocolVersion']) is not int or response['protocolVersion'] != 3 or
            type(response['cancellationProtocol']) is not int or response['cancellationProtocol'] != 1 or
            type(response['effectProtocol']) is not int or response['effectProtocol'] != 1 or
            response['kind'] != expected_kind or binding(response['binding']) != bound or
            response['intent'] != intent or response['deadlineMonotonicNs'] != deadline):
            raise Refused('Cancellation response correlation')
        canonical(response['preparedId']); canonical(response['deadlineMonotonicNs'])
        if prepared_id is not None and response['preparedId'] != prepared_id:
            raise Refused('Cancellation preparation identity')
        if expected_kind == 'effect-outcome':
            status, reason = response['status'], response['reason']
            if type(status) is not str or type(reason) is not str:
                raise Refused('Cancellation outcome type')
            if not ((status == 'Cancelled' and reason == 'cancelled-before-commit') or
                    (status == 'Committed' and reason == 'applied') or
                    (status == 'Unknown' and reason == 'effect-unproven') or
                    (status == 'Refused' and reason in _REFUSALS)):
                raise Refused('Cancellation outcome reason')
            canonical(response['revision']); canonical(response['outputGeneration'])
        return deepcopy(response)

    def cancellation_negotiate(self, request_id):
        if not self.bound:
            raise Refused('Handshake required')
        canonical(request_id)
        bound = deepcopy(binding(self.bound))
        response = self.request({'protocolVersion':3, 'kind':'effect-cancellation-negotiate',
                                 'binding':deepcopy(bound), 'requestId':request_id,
                                 'cancellationProtocol':1})
        exact(response, ('protocolVersion','kind','binding','requestId','cancellationProtocol',
                         'effectProtocol','operations','maxPreparedPerSession',
                         'maxPreparedGlobal','deadlineClock'))
        if (type(response['protocolVersion']) is not int or response['protocolVersion'] != 3 or
            response['kind'] != 'effect-cancellation-capabilities' or
            binding(response['binding']) != bound or response['requestId'] != request_id or
            type(response['cancellationProtocol']) is not int or response['cancellationProtocol'] != 1 or
            type(response['effectProtocol']) is not int or response['effectProtocol'] != 1 or
            type(response['operations']) is not list or response['operations'] != ['restore'] or
            type(response['maxPreparedPerSession']) is not int or response['maxPreparedPerSession'] != 1 or
            type(response['maxPreparedGlobal']) is not int or response['maxPreparedGlobal'] != 64 or
            response['deadlineClock'] != 'CLOCK_MONOTONIC' or self.bound != bound):
            raise Refused('Cancellation capability correlation')
        self._cancellation_binding = deepcopy(bound)
        return deepcopy(response)

    def prepare_effect(self, intent, deadline):
        bound = self._cancellation_scope()
        intent = deepcopy(intent)
        self._cancellation_intent(intent, bound)
        canonical(deadline)
        payload = {'protocolVersion':3, 'kind':'effect-prepare', 'cancellationProtocol':1,
                   'effectProtocol':1, 'binding':deepcopy(bound), 'intent':deepcopy(intent),
                   'deadlineMonotonicNs':deadline}
        response = self.request(payload)
        if self._cancellation_scope() != bound:
            raise Refused('Cancellation binding changed')
        result = self._cancellation_wire(response, bound, intent, deadline)
        # One native slot per session; an exact replay may return its terminal.
        previous = getattr(self, '_cancellation_entry', None)
        if previous is not None and previous['intent'] == intent and previous['deadlineMonotonicNs'] == deadline and previous['preparedId'] != result['preparedId']:
            raise Refused('Cancellation preparation changed')
        same_entry = previous is not None and all(previous[k] == result[k] for k in previous)
        old = getattr(self, '_cancellation_terminal', None) if same_entry else None
        if old is not None and old != result:
            raise Refused('Cancellation terminal changed')
        self._cancellation_entry = deepcopy({key: result[key] for key in _COMMON if key != 'kind'})
        self._cancellation_terminal = deepcopy(result) if result['kind'] == 'effect-outcome' and result['status'] != 'Unknown' else None
        self._cancellation_observed = deepcopy(result)
        return deepcopy(result)

    def _cancellation_entry_for(self, value, terminal=False):
        bound = self._cancellation_scope()
        value = deepcopy(value)
        stored = getattr(self, '_cancellation_terminal' if terminal else '_cancellation_entry', None)
        if stored is None:
            raise Refused('Cancellation receipt not owned')
        if terminal:
            if value != stored or value.get('status') not in ('Committed','Refused','Cancelled'):
                raise Refused('Cancellation terminal not owned')
            entry = getattr(self, '_cancellation_entry', None)
            if entry is None:
                raise Refused('Cancellation receipt not owned')
            self._cancellation_wire(value,bound,entry['intent'],entry['deadlineMonotonicNs'],entry['preparedId'])
        else:
            if not isinstance(value,dict) or value.get('kind') not in ('effect-prepared','effect-outcome'):
                raise Refused('Cancellation preparation not owned')
            entry = {key:value.get(key) for key in _COMMON if key != 'kind'}
            if entry != stored:
                raise Refused('Cancellation preparation not owned')
            self._cancellation_wire(value,bound,entry['intent'],entry['deadlineMonotonicNs'],entry['preparedId'])
            if value['kind'] == 'effect-outcome' and value not in (getattr(self, '_cancellation_observed', None), getattr(self, '_cancellation_terminal', None)):
                raise Refused('Cancellation outcome not owned')
        if entry is None or entry['binding'] != bound:
            raise Refused('Cancellation binding changed')
        return bound, deepcopy(entry)

    def _cancellation_action(self, kind, prepared):
        bound, entry = self._cancellation_entry_for(prepared)
        payload = {'protocolVersion':3, 'kind':kind, 'cancellationProtocol':1, 'effectProtocol':1,
                   'binding':deepcopy(bound), 'intent':deepcopy(entry['intent']),
                   'preparedId':entry['preparedId'], 'deadlineMonotonicNs':entry['deadlineMonotonicNs']}
        response = self.request(payload)
        if self._cancellation_scope() != bound:
            raise Refused('Cancellation binding changed')
        result = self._cancellation_wire(response,bound,entry['intent'],entry['deadlineMonotonicNs'],entry['preparedId'])
        if kind != 'effect-decision-request' and result['kind'] != 'effect-outcome':
            raise Refused('Cancellation decision expected')
        old = getattr(self, '_cancellation_terminal', None)
        if old is not None and result != old:
            raise Refused('Cancellation terminal changed')
        if result['kind'] == 'effect-outcome' and result['status'] != 'Unknown':
            self._cancellation_terminal = deepcopy(result)
        self._cancellation_observed = deepcopy(result)
        return deepcopy(result)

    def commit_effect(self, prepared):
        return self._cancellation_action('effect-commit', prepared)

    def cancel_effect(self, prepared):
        return self._cancellation_action('effect-cancel', prepared)

    def query_effect_decision(self, prepared):
        return self._cancellation_action('effect-decision-request', prepared)

    def ack_effect_decision(self, terminal):
        """ACK only after the caller has durably retained this exact terminal."""
        bound, entry = self._cancellation_entry_for(terminal, terminal=True)
        payload = {'protocolVersion':3, 'kind':'effect-decision-ack', 'cancellationProtocol':1,
                   'effectProtocol':1, 'binding':deepcopy(bound), 'intent':deepcopy(entry['intent']),
                   'preparedId':entry['preparedId'], 'deadlineMonotonicNs':entry['deadlineMonotonicNs']}
        response = self.request(payload)
        if self._cancellation_scope() != bound:
            raise Refused('Cancellation binding changed')
        return self._cancellation_wire(response,bound,entry['intent'],entry['deadlineMonotonicNs'],entry['preparedId'],ack=True)
