"""Strict native594 retirement proof consumer; no durable state mutation."""
from dataclasses import dataclass
from effect_endpoint import Endpoint as EffectEndpoint
from endpoint import Refused, binding, canonical, exact

@dataclass(frozen=True)
class NativeBinding:
    lifetime: str
    session: str
    frontend: str
    @classmethod
    def parse(cls, value):
        binding(value)
        return cls(value['lifetime'], value['session'], value['frontend'])
    def as_dict(self):
        return {'lifetime': self.lifetime, 'session': self.session, 'frontend': self.frontend}

@dataclass(frozen=True)
class RetirementProof:
    binding: NativeBinding
    queried_binding: NativeBinding
    request_id: str
    sequence: str
    operation: str
    grant_state: str
    @property
    def allows_release(self):
        return self.grant_state == 'Retired'
    def as_dict(self):
        return {'protocolVersion':3, 'kind':'binding-retirement', 'retirementProtocol':1,
                'operation':self.operation, 'binding':self.binding.as_dict(),
                'queriedBinding':self.queried_binding.as_dict(), 'requestId':self.request_id,
                'sequence':self.sequence, 'grantState':self.grant_state}

class GrantEndpoint(EffectEndpoint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._grant_watermarks = {}

    def _proof(self, operation, request_id, queried_binding):
        if not self.bound: raise Refused('Handshake required')
        captured = NativeBinding.parse(self.bound)
        target = NativeBinding.parse(queried_binding)
        canonical(request_id)
        if target.lifetime != captured.lifetime: raise Refused('Retirement lifetime mismatch')
        if operation == 'retire' and target == captured: raise Refused('Current caller retirement')
        watermarks = self._grant_watermarks
        if captured.lifetime not in watermarks and len(watermarks) >= 16:
            raise Refused('Retirement lifetime history bound')
        kind = 'binding-retire-request' if operation == 'retire' else 'binding-retirement-state-request'
        # Copies, not references to self.bound or caller-owned queried_binding.
        response = self.request({'protocolVersion':3, 'kind':kind, 'binding':captured.as_dict(),
                                 'requestId':request_id, 'queriedBinding':target.as_dict()})
        if not self.bound or NativeBinding.parse(self.bound) != captured:
            raise Refused('Binding changed during retirement transport')
        exact(response, ['protocolVersion','retirementProtocol','kind','operation','binding',
                         'queriedBinding','requestId','sequence','grantState'])
        if type(response['protocolVersion']) is not int or response['protocolVersion'] != 3:
            raise Refused('Retirement protocol version')
        if type(response['retirementProtocol']) is not int or response['retirementProtocol'] != 1:
            raise Refused('Retirement protocol')
        if response['kind'] != 'binding-retirement' or response['operation'] != operation:
            raise Refused('Retirement operation correlation')
        if NativeBinding.parse(response['binding']) != captured or NativeBinding.parse(response['queriedBinding']) != target:
            raise Refused('Retirement binding correlation')
        canonical(response['requestId']); canonical(response['sequence'])
        if response['requestId'] != request_id: raise Refused('Retirement request correlation')
        state = response['grantState']
        if type(state) is not str or state not in ('Registered','Future','Retired'):
            raise Refused('Retirement state')
        # Keep lifetime history so hello/frontend replacement cannot reset freshness.
        sequence = int(response['sequence'])
        if sequence <= watermarks.get(captured.lifetime, 0):
            raise Refused('Non-increasing retirement proof sequence')
        if operation == 'retire' and state != 'Retired':
            raise Refused('Retirement did not certify Retired')
        watermarks[captured.lifetime] = sequence
        return RetirementProof(captured, target, request_id, response['sequence'], operation, state)

    def observe(self, request_id, queried_binding):
        """Registered/Future are valid observations and never release permission."""
        return self._proof('observe', request_id, queried_binding)

    def retire(self, request_id, queried_binding):
        """Return only a strictly correlated current Retired proof."""
        return self._proof('retire', request_id, queried_binding)
