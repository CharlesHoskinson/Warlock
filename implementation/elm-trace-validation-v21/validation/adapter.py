"""Replay observed scene packets and malformed domain/JSON boundaries without sockets."""
import copy
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
sys.path.insert(0, str(ROOT / 'adapter'))
from endpoint import Refused, decode_reply
from effect_endpoint import Endpoint

ANCESTOR = ROOT.parent / 'elm-surface-facts-v20/qa/native-1791066071820282438/report.json'
OUT = ROOT / 'validation' / ('run-' + str(time.time_ns()))
OUT.mkdir()
source = json.loads(ANCESTOR.read_text())
assert source['passed'] and source['cleanupPassed']
checks = []
report = {'passed': False, 'scope': 'CPU adapter validation against saved native observations; no new native campaign',
          'nativeReportSHA256': hashlib.sha256(ANCESTOR.read_bytes()).hexdigest(),
          'inputs': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in [Path(__file__), *sorted((ROOT / 'adapter').glob('*.py'))]}, 'checks': checks}

class Fixture(Endpoint):
    def __init__(self, packet):
        self.packet = packet
        self.bound = copy.deepcopy(packet['binding'])
    def request(self, payload):
        return self.packet

def accept(name, packet):
    result = Fixture(packet).scene_facts(packet['requestId'])
    assert result is packet
    checks.append({'name': name, 'passed': True})

def refuse(name, packet, bound=None, request=None, minimum='0'):
    endpoint = Fixture(packet)
    if bound is not None:
        endpoint.bound = bound
    try:
        endpoint.scene_facts(request or packet['requestId'], minimum)
    except Refused:
        checks.append({'name': name, 'passed': True})
        return
    raise AssertionError(name)

try:
    packets = [(k, v) for k, v in source.items() if isinstance(v, dict) and v.get('kind') == 'scene-facts']
    assert packets
    for name, packet in packets:
        accept('native-' + name, packet)
    original = packets[0][1]
    assert original['facts']['windows']
    def malformed(name, field, value):
        packet = copy.deepcopy(original)
        packet['facts']['windows'][0][field] = value
        refuse(name, packet)
    for name, value in [('nan', float('nan')), ('infinity', float('inf')), ('negative-infinity', -float('inf')), ('boolean', True), ('huge-int', 10**400)]:
        malformed('geometry-' + name, 'geometry', [value, 0, 10, 10])
    for name, value in [('zero-width', [0,0,0,10]), ('negative-width', [0,0,-1,10]), ('zero-height', [0,0,10,0]), ('short', [0,0,10]), ('string', ['0',0,10,10])]:
        malformed('geometry-' + name, 'geometry', value)
    for field in ('workspace', 'monitor'):
        for value in (True, 0, '00', '-0', ' 1', '1.0', '1e2', '10000000000000000000'):
            malformed(field + '-invalid-' + repr(value), field, value)
        for value in (None, '0', '-1', '9999999999999999999'):
            packet = copy.deepcopy(original)
            packet['facts']['windows'][0][field] = value
            accept(field + '-valid-' + repr(value), packet)
    for value in (-1, True, 2**31, 1.5, '0'):
        malformed('stack-invalid-' + repr(value), 'stackPosition', value)
    for value in (-1, 3, True, 1.5, '0'):
        malformed('fullscreen-invalid-' + repr(value), 'fullscreenMode', value)
    for value in (0, 1, 2):
        packet = copy.deepcopy(original)
        packet['facts']['windows'][0]['fullscreenMode'] = value
        accept('fullscreen-valid-' + str(value), packet)
    packet = copy.deepcopy(original)
    packet['facts']['windows'].append(copy.deepcopy(packet['facts']['windows'][0]))
    refuse('duplicate-incarnation', packet)
    packet = copy.deepcopy(original)
    packet['facts']['focused'] = '18446744073709551615'
    refuse('unknown-focus', packet)
    malformed('unknown-owner', 'owner', '18446744073709551615')
    malformed('boolean-state', 'minimized', 1)
    packet = copy.deepcopy(original)
    bound = copy.deepcopy(packet['binding'])
    bound['frontend'] = str(int(bound['frontend'])+1)
    refuse('obsolete-binding', packet, bound=bound)
    refuse('wrong-request', copy.deepcopy(original), request='18446744073709551615')
    refuse('below-watermark', copy.deepcopy(original), minimum=str(int(original['sequence'])+1))
    for name, raw in [('overflow', '{"v":1e999}'), ('negative-overflow', '{"v":-1e999}'), ('nested-overflow', '{"v":[{"n":1e999}]}'), ('nan', '{"v":NaN}'), ('infinity', '{"v":Infinity}'), ('duplicate', '{"v":0,"v":1}')]:
        try:
            decode_reply(raw)
        except Refused:
            checks.append({'name': 'json-' + name, 'passed': True})
        else:
            raise AssertionError(name)
    assert decode_reply('{"v":1e308}')['v'] == 1e308
    checks.append({'name': 'json-finite-large-number', 'passed': True})
    report.update(passed=True, checkCount=len(checks), nativePackets=len(packets))
except Exception as error:
    report['error'] = repr(error)
finally:
    (OUT / 'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(OUT / 'report.json', flush=True)
    print(json.dumps({k: report[k] for k in ('passed', 'checkCount', 'nativePackets', 'error') if k in report}), flush=True)
raise SystemExit(not report['passed'])
