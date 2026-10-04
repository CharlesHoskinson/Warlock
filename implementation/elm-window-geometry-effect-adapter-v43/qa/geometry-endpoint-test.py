"""Captured actual decoder and transport tests; synthetic CPU authority only."""
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import shutil
import socket
import struct
import sys
import tempfile
import threading
import time
from unittest.mock import patch

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa' / ('geometry-endpoint-' + str(time.time_ns()))
OUT.mkdir()
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
paths = [Path(__file__), *sorted((ROOT / 'adapter').rglob('*.py')), ROOT / 'adapter/legacy-upstream.json', ROOT / 'adapter/geometry-upstream.json', ROOT / 'adapter/effect-upstream.json']
inputs = {str(path.relative_to(ROOT)): sha(path) for path in paths}
for path in paths:
    dest = OUT / 'inputs' / path.relative_to(ROOT)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)
    dest.chmod(0o444)
sys.path.insert(0, str(OUT / 'inputs/adapter'))
import endpoint as base
import geometry_endpoint as geometry

BIND = {'lifetime': '11', 'session': '12', 'frontend': '13'}
CAPS = {'observe': True, 'effects': False, 'effectProtocol': 2, 'operations': [], 'placementCapacity': 256, 'canonicalScene': False}
ATTACH = {'protocolVersion': 3, 'kind': 'geometry-attached', 'geometryProtocol': 1, 'binding': BIND,
          'requestId': '1', 'capabilities': CAPS}
ROW = {'incarnation': '31', 'owner': None, 'workspace': '1', 'workspaceGeneration': '3',
       'monitor': '0', 'outputOwnershipGeneration': '4', 'workAreaRevision': '5', 'workArea': [0, 0, 800, 600],
       'logicalGeometry': [83, 61, 320, 180], 'visualGeometry': [83, 61, 320, 180],
       'nativeMode': 'ordinary', 'clientMode': 'ordinary', 'minimized': False, 'floating': True,
       'grouped': False, 'fixedSize': False, 'constrainedSize': False, 'geometryEligible': True,
       'ordinaryPlacementKnown': False, 'capabilities': {'maximize': False, 'restoreGeometry': False}}
FACTS = {'protocolVersion': 3, 'kind': 'geometry-facts', 'geometryProtocol': 1, 'binding': BIND,
         'requestId': '2', 'sequence': '7', 'revision': '8', 'outputGeneration': '9',
         'facts': {'focused': '31', 'inputBlocked': False, 'windows': [ROW]}}
checks = []


def check(name, fn):
    try:
        fn()
        checks.append({'name': name, 'passed': True})
    except Exception as error:
        checks.append({'name': name, 'passed': False, 'error': repr(error)})


def eq(actual, expected):
    assert actual == expected, (actual, expected)


def refused(fn):
    try:
        fn()
    except (base.Refused, ValueError, TypeError, OverflowError):
        return
    raise AssertionError('Malformed authority data was admitted')


def scripted(cls=geometry.GeometryEndpoint, attach=ATTACH, facts=FACTS):
    obj = cls.__new__(cls)
    obj.bound = dict(BIND)
    obj.pid, obj.instance = 1234, 'CPU_FIXTURE'
    obj.sent = []
    def request(payload):
        obj.sent.append(copy.deepcopy(payload))
        return copy.deepcopy(attach if payload['kind'] == 'geometry-attach' else facts)
    obj.request = request
    return obj


def admit(facts=FACTS, attach=ATTACH, cls=geometry.GeometryEndpoint):
    obj = scripted(cls, attach, facts)
    obj.geometry_attach('1')
    result = obj.geometry_facts('2', '7')
    return obj, result


check('ObserveOnlyAttachAndActualFieldRoundtrip', lambda: eq(admit()[1], FACTS))
check('CanonicalZeroMonitorIsAnIdentityNotMissingOutput', lambda: eq(admit()[1]['facts']['windows'][0]['monitor'], '0'))
check('FactsRequireSeparateGeometryAttach', lambda: refused(lambda: scripted().geometry_facts('2')))
def changed_binding():
    obj, _ = admit()
    obj.bound = {**BIND, 'frontend': '14'}
    refused(lambda: obj.geometry_facts('2'))
check('FreshFrontendRequiresNewGeometryAttach', changed_binding)
def exact_requests():
    obj, _ = admit()
    eq(obj.sent, [{'protocolVersion': 3, 'kind': 'geometry-attach', 'geometryProtocol': 1, 'binding': BIND, 'requestId': '1'},
                  {'protocolVersion': 3, 'kind': 'geometry-facts-request', 'geometryProtocol': 1, 'binding': BIND, 'requestId': '2', 'minimumWatermark': '7'}])
check('ExactSeparateNegotiationAndWatermarkedRequests', exact_requests)

for key, value in [('effects', True), ('operations', ['maximize']), ('operations', ['activate']),
                   ('operations', ['maximize', 'maximize']), ('effectProtocol', True), ('placementCapacity', 255),
                   ('canonicalScene', True), ('observe', False)]:
    reply = copy.deepcopy(ATTACH); reply['capabilities'][key] = value
    check('RejectAttachCapability:' + key + ':' + repr(value), lambda reply=reply: refused(lambda: admit(attach=reply)))
for field, value in [('requestId', '3'), ('binding', {**BIND, 'frontend': '14'}), ('geometryProtocol', True), ('protocolVersion', True)]:
    reply = copy.deepcopy(ATTACH);reply[field] = value
    check('RejectAttachCorrelation:' + field, lambda reply=reply: refused(lambda: admit(attach=reply)))
for field, value in [('requestId', '3'), ('binding', {**BIND, 'session': '14'}), ('sequence', '6'), ('revision', '0'), ('outputGeneration', '01'), ('geometryProtocol', 2)]:
    reply = copy.deepcopy(FACTS);reply[field] = value
    check('RejectFactsCorrelationCounter:' + field, lambda reply=reply: refused(lambda: admit(facts=reply)))
for field in ('workspaceGeneration', 'outputOwnershipGeneration', 'workAreaRevision', 'incarnation'):
    for value in ('0', '01', '18446744073709551616'):
        reply = copy.deepcopy(FACTS);reply['facts']['windows'][0][field] = value
        check('RejectWindowCounter:' + field + ':' + value, lambda reply=reply: refused(lambda: admit(facts=reply)))
for field, value in [('workspace', '-9223372036854775809'), ('workspace', '+1'), ('workspace', '-0'),
                   ('workspaceGeneration', None), ('monitor', None), ('workArea', None),
                   ('nativeMode', 'MAXIMIZED'), ('clientMode', 1), ('minimized', 0), ('fixedSize', 1)]:
    reply = copy.deepcopy(FACTS);reply['facts']['windows'][0][field] = value
    check('RejectWindowStateOrPair:' + field + ':' + repr(value), lambda reply=reply: refused(lambda: admit(facts=reply)))
for field in ('logicalGeometry', 'visualGeometry', 'workArea'):
    for rectangle in ([0, 0, 0, 1], [0, 0, -1, 1], [0, 0, float('nan'), 1], [True, 0, 1, 1],
                      [1e308, 0, 1e308, 1], [0, 0, 1], [0, 0, 1, float('inf')]):
        reply = copy.deepcopy(FACTS);reply['facts']['windows'][0][field] = rectangle
        check('RejectRectangle:' + field + ':' + repr(rectangle), lambda reply=reply: refused(lambda: admit(facts=reply)))
for mode in ('ordinary', 'maximized', 'fullscreen'):
    reply = copy.deepcopy(FACTS);reply['facts']['windows'][0]['nativeMode'] = mode;reply['facts']['windows'][0]['clientMode'] = mode;reply['facts']['windows'][0]['geometryEligible'] = mode != 'fullscreen'
    check('AdmitClosedNativeMode:' + mode, lambda reply=reply: eq(admit(facts=reply)[1], reply))
reply = copy.deepcopy(FACTS)
for field in ('workspace', 'workspaceGeneration', 'monitor', 'outputOwnershipGeneration', 'workAreaRevision', 'workArea'):
    reply['facts']['windows'][0][field] = None
reply['facts']['windows'][0]['geometryEligible'] = False
check('AdmitWhollyAbsentPlacementGroups', lambda reply=reply: eq(admit(facts=reply)[1], reply))
reply = copy.deepcopy(FACTS);reply['facts']['windows'][0]['workspace'] = '-9223372036854775808'
check('SignedWorkspaceMinimumAccepted', lambda reply=reply: eq(admit(facts=reply)[1], reply))
reply = copy.deepcopy(FACTS);reply['revision'] = '18446744073709551615'
check('FullUInt64RevisionPreservedAsString', lambda reply=reply: eq(admit(facts=reply)[1]['revision'], '18446744073709551615'))
for field, value in [('floating', False), ('grouped', True), ('constrainedSize', True),
                     ('minimized', True), ('nativeMode', 'fullscreen'), ('clientMode', 'maximized')]:
    reply = copy.deepcopy(FACTS);reply['facts']['windows'][0][field] = value
    check('RejectContradictoryGeometryEligibility:' + field, lambda reply=reply: refused(lambda: admit(facts=reply)))
reply = copy.deepcopy(FACTS);reply['facts']['inputBlocked'] = True
check('InputBlockedCannotClaimGeometryEligibility', lambda reply=reply: refused(lambda: admit(facts=reply)))
reply = copy.deepcopy(FACTS);reply['facts']['windows'][0]['workspace'] = None;reply['facts']['windows'][0]['workspaceGeneration'] = None;reply['facts']['windows'][0]['geometryEligible'] = False
check('AbsentWorkspaceCannotMixWithKnownOutputOwner', lambda reply=reply: refused(lambda: admit(facts=reply)))
for field, value in [('workspace', '2'), ('monitor', '1'), ('workAreaRevision', '6'), ('workArea', [0, 0, 640, 480])]:
    reply = copy.deepcopy(FACTS);reply['facts']['windows'].append({**copy.deepcopy(ROW), 'incarnation': '32', field: value})
    check('GenerationCannotContradictItsKnownOwner:' + field, lambda reply=reply: refused(lambda: admit(facts=reply)))
reply = copy.deepcopy(FACTS);reply['facts']['windows'].append({**copy.deepcopy(ROW), 'incarnation': '32', 'workspaceGeneration': '33', 'outputOwnershipGeneration': '44', 'workAreaRevision': '55'})
check('SamePeerIdsWithDifferentNativeGenerationsRemainDistinct', lambda reply=reply: eq(admit(facts=reply)[1], reply))
# External native contract oracle: area identity is per workspace owner.
two_workspaces = copy.deepcopy(FACTS)
two_workspaces['facts']['windows'].append({**copy.deepcopy(ROW), 'incarnation':'32',
    'workspace':'2', 'workspaceGeneration':'33', 'workAreaRevision':'55', 'workArea':[0,24,800,576]})
check('SameOutputOwnerTwoWorkspaceAreasAccepted', lambda:eq(admit(facts=two_workspaces)[1],two_workspaces))
for field,value in [('monitor','1'),('workspace','3')]:
    conflict=copy.deepcopy(two_workspaces)
    if field=='workspace': conflict['facts']['windows'][1]['workspaceGeneration']='3'
    conflict['facts']['windows'][1][field]=value
    check('RejectConflictingNativeOwner:'+field,lambda conflict=conflict:refused(lambda:admit(facts=conflict)))
for field,value in [('outputOwnershipGeneration','44'),('workAreaRevision','55'),('workArea',[0,24,800,576])]:
    conflict=copy.deepcopy(FACTS)
    conflict['facts']['windows'].append({**copy.deepcopy(ROW),'incarnation':'32',field:value})
    check('RejectSameWorkspaceOwnerConflictingArea:'+field,lambda conflict=conflict:refused(lambda:admit(facts=conflict)))
# The original actual V35 decoder rejects this legitimate multi-workspace case.
def original_output_scope_mutant():
    parent=json.loads((ROOT/'adapter/geometry-upstream.json').read_text())
    source=Path(parent['parent'])/'adapter/geometry_endpoint.py'
    eq(sha(source),parent['files']['adapter/geometry_endpoint.py'])
    target=OUT/'original-output-scope-mutant.py';shutil.copy2(source,target)
    spec=importlib.util.spec_from_file_location('original_output_scope_mutant',target)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    try: admit(facts=two_workspaces,cls=module.GeometryEndpoint)
    except base.Refused as error:
        eq(str(error),'Output generation/workarea changed inside facts')
        return
    raise AssertionError('Original wrong output scoping was not detected')
check('AppliedOriginalOutputScopeMutantCaughtByPositiveOracle',original_output_scope_mutant)
for corruption in ('unknown-focus', 'unknown-owner', 'self-cycle', 'two-cycle', 'duplicate', 'extra-field', 'missing-field', 'cap-exceeds-negotiation'):
    reply = copy.deepcopy(FACTS);row = reply['facts']['windows'][0]
    if corruption in ('unknown-owner', 'self-cycle', 'two-cycle'): row['geometryEligible'] = False
    if corruption == 'unknown-focus': reply['facts']['focused'] = '99'
    elif corruption == 'unknown-owner': row['owner'] = '99'
    elif corruption == 'self-cycle': row['owner'] = '31'
    elif corruption == 'two-cycle':
        row['owner'] = '32';reply['facts']['windows'].append({**copy.deepcopy(row), 'incarnation': '32', 'owner': '31'})
    elif corruption == 'duplicate': reply['facts']['windows'].append(copy.deepcopy(row))
    elif corruption == 'extra-field': row['script'] = '/bin/sh'
    elif corruption == 'missing-field': del row['floating']
    else: row['capabilities']['maximize'] = True
    check('RejectGraphSchemaCapability:' + corruption, lambda reply=reply: refused(lambda: admit(facts=reply)))
reply = copy.deepcopy(FACTS);reply['facts']['windows'] = [{**copy.deepcopy(ROW), 'incarnation': str(index+1)} for index in range(256)];reply['facts']['focused'] = '1'
check('Actual256WindowBudgetAccepted', lambda reply=reply: eq(len(admit(facts=reply)[1]['facts']['windows']), 256))
too_many = copy.deepcopy(reply);too_many['facts']['windows'].append({**copy.deepcopy(ROW), 'incarnation': '257'})
check('257thWindowRefusedWithoutTruncation', lambda: refused(lambda: admit(facts=too_many)))
future_attach = copy.deepcopy(ATTACH);future_attach['capabilities'].update(effects=True, operations=['maximize', 'restore-geometry'])
future_facts = copy.deepcopy(FACTS);future_facts['facts']['windows'][0]['capabilities'] = {'maximize': True, 'restoreGeometry': True}
check('FutureClosedNegotiatedSubsetCanBeDecodedWithoutExecution', lambda: eq(admit(future_facts, future_attach)[1], future_facts))
def legacy_preserved():
    obj = scripted()
    hello = {'protocolVersion': 3, 'kind': 'attached', 'binding': BIND,
             'compositor': {'pid': 1234, 'instance': 'CPU_FIXTURE', 'coreHash': 'cpu'},
             'capabilities': {'observe': True, 'effects': True, 'minimizedState': True, 'effectProtocol': 1,
                              'operations': ['minimize', 'restore', 'activate'], 'canonicalScene': False,
                              'taskbarProjectionProtocol': 1, 'effectInvalidationProtocol': 1}}
    obj.bound = None;obj.request = lambda payload: copy.deepcopy(hello)
    obj.hello();eq(obj.bound, BIND);eq(obj.geometry_capabilities, None)
    intent = {'request': '1', 'generation': '1', 'incarnation': '31', 'operation': 'restore',
              'context': {'lifetime': '11', 'epoch': '13', 'output': '9', 'revision': '8'}}
    def effect(payload):
        eq(payload['effectProtocol'], 1);eq(payload['intent']['operation'], 'restore')
        return {'protocolVersion': 3, 'kind': 'effect-outcome', 'effectProtocol': 1, 'binding': BIND,
                'intent': intent, 'status': 'Committed', 'reason': '', 'revision': '9', 'outputGeneration': '9'}
    obj.request = effect;eq(obj.effect(intent)['intent'], intent)
check('LegacyHelloAndRestoreUnminimizeWireUnchanged', legacy_preserved)

# Deterministic transport clock covers successful EOF, late EOF, exhausted
# connect/send budget, and expensive final JSON parse on the ACTUAL request.
def transport(method=None, connect=0, send=0, receive=(0, 0), parse_cost=0, raw_reply=b'{"protocolVersion":3,"kind":"cpu-response"}'):
    clock = [0.0]
    class Stream:
        index = 0
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def settimeout(self, value): assert 0 < value <= 2
        def connect(self, path): clock[0] += connect
        def getsockopt(self, *args): return struct.pack('3i', os.getpid(), os.getuid(), os.getgid())
        def sendall(self, raw): clock[0] += send
        def shutdown(self, how): pass
        def recv(self, count):
            index = self.index;self.index += 1;clock[0] += receive[index]
            return raw_reply if index == 0 else b''
    obj = base.Endpoint.__new__(base.Endpoint)
    obj.pid, obj.path = os.getpid(), Path('/cpu-only/socket')
    obj.verify_process = lambda: None;obj.verify_paths = lambda: (1, 2, 3)
    loads = json.loads
    def parse(*args, **kwargs):
        result = loads(*args, **kwargs);clock[0] += parse_cost;return result
    with patch.object(base.time, 'monotonic', lambda: clock[0]), patch.object(base.socket, 'socket', lambda *args: Stream()), patch.object(base.json, 'loads', parse):
        return (method or base.Endpoint.request)(obj, {'protocolVersion': 3, 'kind': 'cpu-request'})
check('ActualTransportAcceptsCompleteEofWithinSingleBudget', lambda: eq(transport(connect=.5, send=.5, receive=(.5,.5))['kind'], 'cpu-response'))
check('ActualTransportRefusesEofArrivingAfterAbsoluteDeadline', lambda: refused(lambda: transport(connect=1, send=1, receive=(.7,.4))))
check('ConnectAndSendCannotEachResetDeadline', lambda: refused(lambda: transport(connect=1.6, send=1.6)))
check('FinalJsonParseMustFinishInsideOriginalDeadline', lambda: refused(lambda: transport(receive=(1,1), parse_cost=1.1)))
check('TransportRejectsDuplicateJsonKeys', lambda: refused(lambda: transport(raw_reply=b'{"protocolVersion":3,"kind":"cpu-response","kind":"spoof"}')))
check('TransportRejectsRawNonfiniteJson', lambda: refused(lambda: transport(raw_reply=b'{"protocolVersion":3,"kind":"cpu-response","x":NaN}')))
def real_socket_roundtrip():
    with tempfile.TemporaryDirectory(prefix='geometry-endpoint-cpu-') as temporary:
        runtime = Path(temporary).resolve();runtime.chmod(0o700)
        directory = runtime / 'hypr' / 'CPU_FIXTURE';directory.mkdir(parents=True, mode=0o700);directory.parent.chmod(0o700)
        path = directory / '.socket.sock'
        errors = []
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
            server.bind(str(path));server.listen(1);server.settimeout(3)
            def serve():
                try:
                    with server.accept()[0] as connection:
                        connection.settimeout(2)
                        data = bytearray()
                        while True:
                            part = connection.recv(4096)
                            if not part: break
                            data.extend(part)
                        assert data.startswith(b'j/elm_observe ')
                        connection.sendall(b'{"protocolVersion":3,"kind":"cpu-response"}')
                except Exception as error:
                    errors.append(repr(error))
            thread = threading.Thread(target=serve);thread.start()
            obj = base.Endpoint(str(runtime), 'CPU_FIXTURE', os.getpid(), base.start_time(os.getpid()), sha('/proc/self/exe'))
            eq(obj.request({'protocolVersion': 3, 'kind': 'cpu-request'})['kind'], 'cpu-response')
            thread.join(timeout=3);assert not thread.is_alive() and not errors, errors
check('ActualOwnedUnixSocketPeerCompleteEofRoundtrip', real_socket_roundtrip)

def oracle_detects_unsafe(fn):
    try:
        refused(fn)
    except AssertionError as error:
        eq(str(error), 'Malformed authority data was admitted')
        return
    raise AssertionError('Mutant was not detected by the independent refusal oracle')

def historical_deadline_mutant():
    old = ast.parse((OUT / 'inputs/adapter/inherited/endpoint.py').read_text())
    cls = next(node for node in old.body if isinstance(node, ast.ClassDef) and node.name == 'Endpoint')
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == 'request')
    namespace = dict(vars(base));exec(compile(ast.Module(body=[method], type_ignores=[]), 'historical-request-mutant', 'exec'), namespace)
    # Original unsafe code really accepts late EOF; the independent refusal
    # oracle detects it, rather than counting a compile/runtime fault as killed.
    oracle_detects_unsafe(lambda: transport(method=namespace['request'], connect=1, send=1, receive=(.7,.4)))
check('AppliedHistoricalLateEofMutantCaughtByRefusalOracle', historical_deadline_mutant)
def capability_mutant():
    source = (OUT / 'inputs/adapter/geometry_endpoint.py').read_text()
    needle = "if caps[field] and operation not in self.geometry_capabilities['operations']:"
    assert source.count(needle) == 1
    mutated = source.replace(needle, 'if False:')
    path = OUT / 'geometry-capability-mutant.py';path.write_text(mutated)
    spec = importlib.util.spec_from_file_location('actual_capability_mutant', path)
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    bad = copy.deepcopy(FACTS);bad['facts']['windows'][0]['capabilities']['maximize'] = True
    oracle_detects_unsafe(lambda: admit(facts=bad, cls=module.GeometryEndpoint))
check('AppliedCapabilityBypassMutantCaughtByNegotiationOracle', capability_mutant)
upstream = json.loads((ROOT / 'adapter/legacy-upstream.json').read_text())
for name, digest in upstream['files'].items():
    check('InheritedSourcePreserved:' + name, lambda name=name, digest=digest: eq(
        (sha(Path(upstream['parent']) / name), sha(ROOT / 'adapter/inherited' / name)), (digest, digest)))
check('EffectEndpointLegacySourceByteUnchanged', lambda: eq(sha(ROOT / 'adapter/effect_endpoint.py'), upstream['files']['effect_endpoint.py']))
def only_transport_changed():
    current = ast.parse((ROOT / 'adapter/endpoint.py').read_text())
    previous = ast.parse((ROOT / 'adapter/inherited/endpoint.py').read_text())
    old_class = next(node for node in previous.body if isinstance(node, ast.ClassDef) and node.name == 'Endpoint')
    old_request = next(node for node in old_class.body if isinstance(node, ast.FunctionDef) and node.name == 'request')
    new_class = next(node for node in current.body if isinstance(node, ast.ClassDef) and node.name == 'Endpoint')
    new_class.body = [old_request if isinstance(node, ast.FunctionDef) and node.name == 'request' else node for node in new_class.body]
    eq(ast.dump(current, include_attributes=False), ast.dump(previous, include_attributes=False))
check('BaseEndpointAstOnlyAbsoluteTransportMethodChanged', only_transport_changed)

EFFECT_INTENT = {'request':'41','generation':'42','incarnation':'31','operation':'maximize',
                 'context':{'lifetime':'11','epoch':'13','output':'9','revision':'8'}}
EFFECT_REPLY = {'protocolVersion':3,'kind':'effect-outcome','effectProtocol':2,'binding':BIND,
                'intent':EFFECT_INTENT,'status':'Committed','reason':'','revision':'9','outputGeneration':'9'}
def effect_script(reply=EFFECT_REPLY, operations=('maximize','restore-geometry')):
    attach=copy.deepcopy(ATTACH);attach['capabilities'].update(effects=True,operations=list(operations))
    obj=scripted(attach=attach);obj.geometry_attach('1');obj.sent=[]
    def request(payload):
        obj.sent.append(copy.deepcopy(payload));return copy.deepcopy(reply)
    obj.request=request
    return obj
def effect_admit(reply=EFFECT_REPLY, intent=EFFECT_INTENT, operations=('maximize','restore-geometry')):
    obj=effect_script(reply,operations);return obj,obj.geometry_effect(copy.deepcopy(intent))
check('Effect2ExplicitNegotiatedExactWire',lambda:eq(effect_admit()[0].sent,[{'protocolVersion':3,'kind':'window-effect',
      'effectProtocol':2,'binding':BIND,'intent':EFFECT_INTENT}]))
check('GeometryRevisionContextRemainsDistinctFromSceneRevision',lambda:eq(admit()[0].geometry_context(FACTS),EFFECT_INTENT['context']))
def unavailable_no_send():
    obj,_=admit();before=copy.deepcopy(obj.sent);refused(lambda:obj.geometry_effect(EFFECT_INTENT));eq(obj.sent,before)
check('ActualObserveOnlyNegotiationNeverSendsEffect2',unavailable_no_send)
for status in ['Committed','Refused','Unknown']:
    reply=copy.deepcopy(EFFECT_REPLY);reply['status']=status
    check('Effect2AuthoritativeOutcome:'+status,lambda reply=reply:eq(effect_admit(reply)[1],reply))
reply=copy.deepcopy(EFFECT_REPLY);reply['intent']['operation']='restore-geometry'
check('RestoreGeometryDistinctFromLegacyRestore',lambda:eq(effect_admit(reply,reply['intent'])[1],reply))
for field,value in [('protocolVersion',True),('effectProtocol',1),('effectProtocol',True),('kind','attached'),
                    ('status','Cancelled'),('reason','x'*257),('reason','\ud800'),('revision','0'),('outputGeneration','01')]:
    reply=copy.deepcopy(EFFECT_REPLY);reply[field]=value
    check('RejectMalformedEffect2Outcome:'+field+':'+repr(value),lambda reply=reply:refused(lambda:effect_admit(reply)))
for field,value in [('request','43'),('generation','43'),('incarnation','32'),('operation','restore-geometry')]:
    reply=copy.deepcopy(EFFECT_REPLY);reply['intent'][field]=value
    check('RejectFullIntentCorrelation:'+field,lambda reply=reply:refused(lambda:effect_admit(reply)))
for field in ['lifetime','epoch','output','revision']:
    reply=copy.deepcopy(EFFECT_REPLY);reply['intent']['context'][field]='99'
    check('RejectFullContextCorrelation:'+field,lambda reply=reply:refused(lambda:effect_admit(reply)))
reply=copy.deepcopy(EFFECT_REPLY);reply['binding']['frontend']='14'
check('RejectEffect2BindingCorrelation',lambda:refused(lambda:effect_admit(reply)))
for field,value in [('request','0'),('generation',True),('incarnation','01'),('operation','restore'),('operation',[]),('extra',1)]:
    intent=copy.deepcopy(EFFECT_INTENT);intent[field]=value
    check('RejectMalformedEffect2Intent:'+field,lambda intent=intent:refused(lambda:effect_admit(intent=intent)))
for field in ['lifetime','epoch']:
    intent=copy.deepcopy(EFFECT_INTENT);intent['context'][field]='99'
    check('RejectStaleGeometryAuthorityBeforeSend:'+field,lambda intent=intent:refused(lambda:effect_admit(intent=intent)))
check('AbsentOperationCapabilityCannotBeInferred',lambda:refused(lambda:effect_admit(operations=('restore-geometry',))))
def unknown_no_retry():
    reply=copy.deepcopy(EFFECT_REPLY);reply['status']='Unknown';obj,result=effect_admit(reply)
    eq(len(obj.sent),1);eq(result,reply)
    # Only explicit caller replay sends another identical full key; no auto retry.
    obj.geometry_effect(copy.deepcopy(EFFECT_INTENT));eq(obj.sent[0],obj.sent[1]);eq(len(obj.sent),2)
check('UnknownNeverRetriesOrAllocatesAndExplicitReplayPreservesFullKey',unknown_no_retry)
def old_effect_preserved():
    obj=effect_script();intent=copy.deepcopy(EFFECT_INTENT);intent['operation']='restore'
    reply=copy.deepcopy(EFFECT_REPLY);reply.update(effectProtocol=1,intent=intent)
    obj.request=lambda payload:(obj.sent.append(copy.deepcopy(payload)) or copy.deepcopy(reply))
    eq(obj.effect(intent),reply);eq(obj.sent[-1]['effectProtocol'],1)
    refused(lambda:obj.geometry_effect(intent))
check('SharedCallerIDsPreserveLegacyRestoreAndProtocolNamespace',old_effect_preserved)
for corrupt in ('protocol','binding','intent'):
    source=(OUT/'inputs/adapter/geometry_endpoint.py').read_text()
    needle={'protocol':"response['effectProtocol'] != 2",'binding':"binding(response['binding']) != self.bound",'intent':"response['intent'] != intent"}[corrupt]
    prefix,method=source.split('    def geometry_effect(self, intent):',1)
    assert method.count(needle)==1
    target=OUT/('effect-'+corrupt+'-mutant.py');target.write_text(prefix+'    def geometry_effect(self, intent):'+method.replace(needle,'False'))
    spec=importlib.util.spec_from_file_location('effect_'+corrupt+'_mutant',target);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    reply=copy.deepcopy(EFFECT_REPLY)
    if corrupt=='protocol':reply['effectProtocol']=1
    elif corrupt=='binding':reply['binding']['frontend']='14'
    else:reply['intent']['generation']='99'
    obj=effect_script(reply);obj.__class__=module.GeometryEndpoint
    check('AppliedFullKeyBypassMutantDetected:'+corrupt,lambda obj=obj:oracle_detects_unsafe(lambda:obj.geometry_effect(copy.deepcopy(EFFECT_INTENT))))

effect_parent=json.loads((ROOT/'adapter/effect-upstream.json').read_text())
for name in ['adapter/endpoint.py','adapter/effect_endpoint.py']:
    check('V38TransportAndLegacyEffectBytePreserved:'+name,lambda name=name:eq(sha(ROOT/name),effect_parent['files'][name]))
def unchanged_observer_methods():
    previous=ast.parse((Path(effect_parent['parent'])/'adapter/geometry_endpoint.py').read_text())
    current=ast.parse((ROOT/'adapter/geometry_endpoint.py').read_text())
    old=next(node for node in previous.body if isinstance(node,ast.ClassDef))
    new=next(node for node in current.body if isinstance(node,ast.ClassDef))
    eq([ast.dump(node,include_attributes=False) for node in new.body[:len(old.body)]],
       [ast.dump(node,include_attributes=False) for node in old.body])
check('V38ObserverMethodsAstPreserved',unchanged_observer_methods)
check('V38Accepted132ParentStillPasses',lambda:eq(json.loads(Path(effect_parent['report']).read_text())['checkCount'],132))
parent=json.loads((ROOT/'adapter/geometry-upstream.json').read_text())
check('Accepted117ParentReportPreserved',lambda:eq(sha(parent['report']),parent['reportSHA256']))
for relative,digest in parent['files'].items():
    check('AcceptedParentSourcePreserved:'+relative,lambda relative=relative,digest=digest:eq(sha(Path(parent['parent'])/relative),digest))
for relative, digest in inputs.items():
    check('CapturedAndOriginalInputPreserved:' + relative, lambda relative=relative, digest=digest: eq(
        (sha(ROOT / relative), sha(OUT / 'inputs' / relative)), (digest, digest)))
report = {'passed': all(check['passed'] for check in checks), 'nativeAcceptance': False, 'effectsImplemented': False,
          'scope': 'Actual captured geometry decoder, legacy wire, applied unsafe mutants and deterministic transport CPU tests; no native authority/GUI',
          'inputs': inputs, 'checks': checks, 'checkCount': len(checks)}
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(OUT / 'report.json', flush=True)
print('checks', len(checks), 'failed', sum(not check['passed'] for check in checks), flush=True)
raise SystemExit(not report['passed'])
