"""Separate, negotiated geometry observer; legacy restore stays unminimize."""
import math
import re

from effect_endpoint import Endpoint as LegacyEffectEndpoint
from endpoint import Refused, binding, canonical, exact

MODES = {'ordinary', 'maximized', 'fullscreen'}
OPERATIONS = {'maximize', 'restore-geometry'}
WINDOW_FIELDS = ['incarnation', 'owner', 'workspace', 'workspaceGeneration', 'monitor',
                 'outputOwnershipGeneration', 'workAreaRevision', 'workArea',
                 'logicalGeometry', 'visualGeometry', 'nativeMode', 'clientMode',
                 'minimized', 'floating', 'grouped', 'fixedSize', 'constrainedSize',
                 'geometryEligible', 'ordinaryPlacementKnown', 'capabilities']


def rect(value):
    if not isinstance(value, list) or len(value) != 4 or any(type(v) not in (int, float) for v in value):
        raise Refused('Geometry rectangle shape')
    try:
        valid = all(math.isfinite(v) for v in value) and value[2] > 0 and value[3] > 0 and all(
            math.isfinite(edge) for edge in (value[0] + value[2], value[1] + value[3]))
    except OverflowError:
        valid = False
    if not valid:
        raise Refused('Invalid geometry rectangle')


def workspace(value):
    if not isinstance(value, str) or not re.fullmatch(r'(?:0|-?[1-9][0-9]{0,18})', value) or not -(1 << 63) <= int(value) < (1 << 63):
        raise Refused('Invalid workspace identity')


class GeometryEndpoint(LegacyEffectEndpoint):
    def hello(self):
        response = super().hello()
        self.geometry_binding = None
        self.geometry_capabilities = None
        return response

    def geometry_attach(self, request_id):
        if not self.bound:
            raise Refused('Legacy handshake required')
        canonical(request_id)
        response = self.request({'protocolVersion': 3, 'kind': 'geometry-attach',
                                 'geometryProtocol': 1, 'binding': self.bound, 'requestId': request_id})
        exact(response, ['protocolVersion', 'kind', 'geometryProtocol', 'binding', 'requestId', 'capabilities'])
        self._correlation(response, 'geometry-attached', request_id)
        caps = response['capabilities']
        exact(caps, ['observe', 'effects', 'effectProtocol', 'operations', 'placementCapacity', 'canonicalScene'])
        if caps['observe'] is not True or type(caps['effects']) is not bool or caps['canonicalScene'] is not False:
            raise Refused('Geometry capability booleans')
        if type(caps['effectProtocol']) is not int or caps['effectProtocol'] != 2 or type(caps['placementCapacity']) is not int or caps['placementCapacity'] != 256:
            raise Refused('Geometry capability versions/bounds')
        operations = caps['operations']
        if not isinstance(operations, list) or len(operations) > 2 or any(type(op) is not str or op not in OPERATIONS for op in operations) or len(set(operations)) != len(operations):
            raise Refused('Geometry operation capabilities')
        if caps['effects'] != bool(operations):
            raise Refused('Geometry effects/operation contradiction')
        self.geometry_binding = dict(self.bound)
        self.geometry_capabilities = {**caps, 'operations': list(operations)}
        return response

    def _correlation(self, response, kind, request_id):
        if type(response['protocolVersion']) is not int or response['protocolVersion'] != 3 or type(response['geometryProtocol']) is not int or response['geometryProtocol'] != 1:
            raise Refused('Geometry protocol version')
        if response['kind'] != kind or binding(response['binding']) != self.bound or response['requestId'] != request_id:
            raise Refused('Geometry response correlation')

    def geometry_facts(self, request_id, minimum_watermark='0'):
        if not self.bound or getattr(self, 'geometry_binding', None) != self.bound or getattr(self, 'geometry_capabilities', None) is None:
            raise Refused('Geometry attach required for current binding')
        canonical(request_id)
        canonical(minimum_watermark, True)
        response = self.request({'protocolVersion': 3, 'kind': 'geometry-facts-request',
                                 'geometryProtocol': 1, 'binding': self.bound, 'requestId': request_id,
                                 'minimumWatermark': minimum_watermark})
        exact(response, ['protocolVersion', 'kind', 'geometryProtocol', 'binding', 'requestId',
                         'sequence', 'revision', 'outputGeneration', 'facts'])
        self._correlation(response, 'geometry-facts', request_id)
        for field in ('sequence', 'revision', 'outputGeneration'):
            canonical(response[field])
        if int(response['sequence']) < int(minimum_watermark):
            raise Refused('Obsolete geometry facts')
        facts = response['facts']
        exact(facts, ['focused', 'inputBlocked', 'windows'])
        if type(facts['inputBlocked']) is not bool:
            raise Refused('Input blocking state')
        rows = facts['windows']
        if not isinstance(rows, list) or len(rows) > 256:
            raise Refused('Geometry window bound')
        table = {}
        workspace_owners = {}
        output_owners = {}
        workspace_areas = {}
        for row in rows:
            exact(row, WINDOW_FIELDS)
            identity = canonical(row['incarnation'])
            if identity in table:
                raise Refused('Duplicate geometry incarnation')
            table[identity] = row
            if row['owner'] is not None:
                canonical(row['owner'])
            placement_fields = ('workspace', 'workspaceGeneration', 'monitor',
                                'outputOwnershipGeneration', 'workAreaRevision', 'workArea')
            if len({row[field] is None for field in placement_fields}) != 1:
                raise Refused('Workspace/output/workarea pairing')
            if row['workspace'] is not None:
                workspace(row['workspace'])
                canonical(row['workspaceGeneration'])
                generation = row['workspaceGeneration']
                if generation in workspace_owners and workspace_owners[generation] != row['workspace']:
                    raise Refused('Workspace generation owner changed')
                workspace_owners[generation] = row['workspace']
            if row['monitor'] is not None:
                canonical(row['monitor'], True)
                canonical(row['outputOwnershipGeneration'])
                canonical(row['workAreaRevision'])
                rect(row['workArea'])
                generation = row['outputOwnershipGeneration']
                value = row['monitor']
                if generation in output_owners and output_owners[generation] != value:
                    raise Refused('Output generation owner changed inside facts')
                output_owners[generation] = value
                # Native workarea revisions belong to workspace owners, not
                # outputs: two workspaces on one output may differ here.
                area_owner = row['workspaceGeneration']
                area = (generation, row['workAreaRevision'], row['workArea'])
                if area_owner in workspace_areas and workspace_areas[area_owner] != area:
                    raise Refused('Workspace generation workarea changed inside facts')
                workspace_areas[area_owner] = area
            rect(row['logicalGeometry'])
            rect(row['visualGeometry'])
            if type(row['nativeMode']) is not str or row['nativeMode'] not in MODES or type(row['clientMode']) is not str or row['clientMode'] not in MODES:
                raise Refused('Native/client geometry mode')
            for field in ('minimized', 'floating', 'grouped', 'fixedSize', 'constrainedSize', 'geometryEligible', 'ordinaryPlacementKnown'):
                if type(row[field]) is not bool:
                    raise Refused('Geometry state boolean')
            if row['geometryEligible'] and (row['workspace'] is None or facts['inputBlocked'] or
                    row['minimized'] or row['grouped'] or row['constrainedSize'] or not row['floating'] or
                    row['owner'] is not None or row['nativeMode'] != row['clientMode'] or row['nativeMode'] == 'fullscreen'):
                raise Refused('Contradictory geometry eligibility')
            caps = row['capabilities']
            exact(caps, ['maximize', 'restoreGeometry'])
            if any(type(value) is not bool for value in caps.values()):
                raise Refused('Window geometry capability booleans')
            for field, operation in (('maximize', 'maximize'), ('restoreGeometry', 'restore-geometry')):
                if caps[field] and operation not in self.geometry_capabilities['operations']:
                    raise Refused('Window capability exceeds negotiated native support')
        if facts['focused'] is not None and canonical(facts['focused']) not in table:
            raise Refused('Unknown geometry focus')
        for row in rows:
            visited = set()
            current = row['incarnation']
            while current is not None:
                if current not in table:
                    raise Refused('Unknown geometry owner')
                if current in visited:
                    raise Refused('Geometry ownership cycle')
                visited.add(current)
                current = table[current]['owner']
        return response

    def geometry_context(self, facts):
        """Geometry revision occupies revision; legacy scene revision stays separate."""
        if getattr(self, 'geometry_binding', None) != self.bound or not self.bound:
            raise Refused('Geometry attach required for current binding')
        exact(facts, ['protocolVersion', 'kind', 'geometryProtocol', 'binding', 'requestId',
                      'sequence', 'revision', 'outputGeneration', 'facts'])
        self._correlation(facts, 'geometry-facts', facts['requestId'])
        for field in ('requestId', 'sequence', 'revision', 'outputGeneration'):
            canonical(facts[field])
        return {'lifetime': self.bound['lifetime'], 'epoch': self.bound['frontend'],
                'output': facts['outputGeneration'], 'revision': facts['revision']}

    def geometry_effect(self, intent):
        """No allocator or retries: caller supplies the shared effect1/2 intent IDs.

        A native attach with effects false remains unavailable. CPU fixtures may
        explicitly negotiate hypothetical support to exercise this wire decoder.
        """
        if not self.bound or getattr(self, 'geometry_binding', None) != self.bound:
            raise Refused('Geometry attach required for current binding')
        caps = getattr(self, 'geometry_capabilities', None)
        if not caps or caps['effects'] is not True:
            raise Refused('Native geometry effects unavailable')
        exact(intent, ['request', 'generation', 'incarnation', 'operation', 'context'])
        exact(intent['context'], ['lifetime', 'epoch', 'output', 'revision'])
        for field in ('request', 'generation', 'incarnation'):
            canonical(intent[field])
        for value in intent['context'].values():
            canonical(value)
        operation = intent['operation']
        if type(operation) is not str or operation not in OPERATIONS or operation not in caps['operations']:
            raise Refused('Unsupported negotiated geometry operation')
        if intent['context']['lifetime'] != self.bound['lifetime'] or intent['context']['epoch'] != self.bound['frontend']:
            raise Refused('Geometry intent authority mismatch')
        response = self.request({'protocolVersion': 3, 'kind': 'window-effect', 'effectProtocol': 2,
                                 'binding': dict(self.bound), 'intent': intent})
        exact(response, ['protocolVersion', 'kind', 'effectProtocol', 'binding', 'intent',
                         'status', 'reason', 'revision', 'outputGeneration'])
        if type(response['protocolVersion']) is not int or response['protocolVersion'] != 3 or response['kind'] != 'effect-outcome' or type(response['effectProtocol']) is not int or response['effectProtocol'] != 2:
            raise Refused('Geometry effect outcome protocol')
        if binding(response['binding']) != self.bound or response['intent'] != intent:
            raise Refused('Geometry effect outcome correlation')
        if type(response['status']) is not str or response['status'] not in ('Committed', 'Refused', 'Unknown'):
            raise Refused('Geometry effect outcome status')
        reason = response['reason']
        if type(reason) is not str:
            raise Refused('Geometry effect reason type')
        try:
            if len(reason.encode('utf-16-le')) // 2 > 256:
                raise Refused('Geometry effect reason bound')
        except UnicodeError as error:
            raise Refused('Geometry effect reason Unicode') from error
        canonical(response['revision']); canonical(response['outputGeneration'])
        return response
