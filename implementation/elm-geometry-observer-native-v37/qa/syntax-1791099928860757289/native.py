"""Reviewed real xdg maximize/restore roundtrip, private host only.

No menu transport/authority claim. Request barriers, configure/ACK/buffer records,
native readback and independently captured pixels are separate evidence.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import traceback

import sys

SLICE = Path(__file__).resolve().parents[1]
REPO = SLICE.parents[1]
ROOT = REPO / 'implementation/elm-window-geometry-map-state-v28/core'
AUTH = REPO / 'implementation/elm-window-geometry-authority-v35'
sys.path.insert(0, str(AUTH / 'adapter'))
from geometry_endpoint import GeometryEndpoint
from endpoint import Refused, start_time
spec = importlib.util.spec_from_file_location('geometry_private_host', ROOT / 'candidate_host.py')
host = importlib.util.module_from_spec(spec)
spec.loader.exec_module(host)
host.original.qa.require_qa_scope()
OUT = SLICE / 'qa' / ('native-' + str(time.time_ns()))
OUT.mkdir()
OUTPUT = Path('/home/hoskinson/window-integration-qa') / ('elm-geometry-observer-' + str(time.time_ns()))
LUA = b'hl.config({xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'
report = {'passed': False, 'mainDesktopActions': False, 'menuTransportIntegrated': False,
          'geometryEffectsImplemented': False, 'scope': 'Actual separately negotiated readonly geometry observer, legacy compatibility, native/client MAX and restore readback; no menu integration, workarea-change or ownership-replacement qualification', 'checks': []}
session = None
client = None
records = []
selected_colors = {}


def check(name, value, **data):
    report['checks'].append({'name': name, 'passed': bool(value), **data})
    assert value, name


def wait(predicate, timed=False, deadline=None):
    if deadline is None:
        deadline = time.monotonic() + 6
    while time.monotonic() < deadline:
        session.guard()
        value = predicate(deadline) if timed else predicate()
        if time.monotonic() >= deadline:
            raise RuntimeError('Unchanged six-second observation deadline')
        if value:
            return value
        time.sleep(min(.04, max(0, deadline - time.monotonic())))
    raise RuntimeError('Unchanged six-second observation deadline')


def events():
    global records
    raw = client_log.read_bytes()
    if len(raw) > 4 * 1024 * 1024:
        raise RuntimeError('Client evidence exceeded bound')
    parsed = []
    for line in raw.splitlines(keepends=True):
        if not line.endswith(b'\n'):
            break
        if not line.startswith(b'{'):
            continue  # Actual WAYLAND_DEBUG/stderr stays in the owned log.
        record = json.loads(line)
        if type(record.get('sequence')) is not int or record['sequence'] != len(parsed) + 1:
            raise RuntimeError('Client event sequence gap or duplicate')
        if record.get('event') == 'refused':
            raise RuntimeError('Actual client refused: ' + repr(record))
        parsed.append(record)
    if parsed[:len(records)] != records:
        raise RuntimeError('Client evidence changed after observation')
    records = parsed
    return parsed


def native_window():
    windows = [row for row in session.data('clients') if row.get('pid') == client.pid and row.get('title') == 'ELM-MAXIMIZE-PROBE']
    if len(windows) > 1:
        raise RuntimeError('Native fixture identity ambiguous')
    if not windows:
        return None
    row = windows[0]
    if 'address' in report.get('fixtureIdentity', {}) and row['address'] != report['fixtureIdentity']['address']:
        raise RuntimeError('Native fixture identity replaced')
    return row


def latest_buffer():
    return next((row for row in reversed(events()) if row['event'] == 'buffercommit'), None)


def request(command, deadline=None):
    if deadline is None:
        deadline = time.monotonic() + 6
    session.guard()
    assert client.poll() is None and host.original.same_process(client_identity)
    before = events()[-1]['sequence'] if events() else 0
    if time.monotonic() >= deadline:
        raise RuntimeError('Unchanged six-second observation deadline before request')
    client.stdin.write((command + '\n').encode())
    client.stdin.flush()
    packet = wait(lambda: next((row for row in events() if row['sequence'] > before and row['event'] == 'request' and row.get('command') == command), None), deadline=deadline)
    barrier = wait(lambda: next((row for row in events() if row['event'] == 'server-barrier' and row.get('requestSequence') == packet['sequence']), None), deadline=deadline)
    exact = [row for row in events() if row['event'] == 'server-barrier' and row.get('requestSequence') == packet['sequence']]
    check(command + ':exactRequestCorrelatedServerBarrier', len(exact) == 1 and
          barrier.get('command') == command and barrier.get('requestSerial') == packet['serial'] and
          barrier['sequence'] > packet['sequence'], request=packet, barrier=barrier)
    return packet


def settled(mode, after_sequence=None):
    row, buffer = native_window(), latest_buffer()
    if row is None or buffer is None:
        return None
    expected_maximized = mode == 1
    if row.get('fullscreen') != mode or row.get('fullscreenClient') != mode or row.get('xwayland') is not False:
        return None
    if buffer.get('maximized') is not expected_maximized or buffer.get('fullscreen') is not False:
        return None
    if after_sequence is not None and buffer['sequence'] <= after_sequence:
        return None
    if [buffer.get('bufferWidth'), buffer.get('bufferHeight')] != row['size']:
        return None
    return row, buffer



endpoint = None
loaded = False
request_number = 0

def rid():
    global request_number
    request_number += 1
    return str(request_number)

def refused(name, action):
    try:
        action()
    except Refused as error:
        check(name, True, reason=str(error))
        return
    raise AssertionError(name + ': accepted forbidden operation')

def facts():
    response = endpoint.geometry_facts(rid())
    report.setdefault('geometryObservations', []).append(response)
    return response

def one_fact(response):
    rows = response['facts']['windows']
    assert len(rows) == 1, 'Private observer requires exactly its one real fixture'
    return rows[0]

def correlate(name, response, native, mode):
    row = one_fact(response)
    projection = endpoint.snapshot(rid())
    legacy = endpoint.scene_facts(rid())
    identity = row['incarnation']
    check(name + ':exactNativeMemberIdentity', len(projection['windows']) == 1 and
          projection['windows'][0]['incarnation'] == identity and projection['windows'][0]['label'] == native['title'] and
          len(legacy['facts']['windows']) == 1 and legacy['facts']['windows'][0]['incarnation'] == identity and
          legacy['facts']['windows'][0]['application'] == native['class'] and native['pid'] == client.pid and
          native['address'] == report['fixtureIdentity']['address'], native=native, legacy=legacy, projection=projection)
    check(name + ':logicalAndVisualMatchRawNativeGeometry', row['logicalGeometry'] == [*native['at'], *native['size']] and
          row['visualGeometry'] == [*native['at'], *native['size']], geometry=row)
    check(name + ':actualNativeAndClientMode', row['nativeMode'] == row['clientMode'] == mode and
          native['fullscreen'] == native['fullscreenClient'] == (1 if mode == 'maximized' else 0))
    monitors = session.data('monitors')
    monitor = next(m for m in monitors if str(m['id']) == row['monitor'])
    workspace = native['workspace']['id']
    check(name + ':actualWorkspaceOutputAndWorkarea', row['workspace'] == str(workspace) and row['owner'] is None and
          row['monitor'] == str(native['monitor']) and monitor['width'] == 800 and monitor['height'] == 600 and
          monitor['scale'] == 1 and monitor['reserved'] == [0, 0, 0, 0] and row['workArea'] == [0, 0, 800, 600], monitor=monitor)
    check(name + ':truthfulUnsupportedGeometryAndConstraints', row['capabilities'] == {'maximize': False, 'restoreGeometry': False} and
          row['fixedSize'] is False and row['constrainedSize'] is False and row['grouped'] is False and
          row['minimized'] is False and row['floating'] is True and row['geometryEligible'] is True and
          row['ordinaryPlacementKnown'] is False and response['facts']['inputBlocked'] is False)
    return row

try:
    core = host.core_tuple()
    fixture = json.loads((ROOT / 'client-build-report.json').read_text())
    plugin_report = AUTH / 'qa/geometry-build-1791099555616078276/report.json'
    plugin_build = json.loads(plugin_report.read_text())
    assert plugin_build['passed'] and not plugin_build['missingSymbols']
    plugin = plugin_build['binary']
    assert host.digest(plugin) == plugin_build['binarySHA256']
    assert plugin_build['core']['path'] == core['binary'] and plugin_build['core']['sha256'] == core['sha256']
    assert host.digest(fixture['client']) == fixture['clientSHA256'] and host.digest(fixture['buildReport']) == fixture['buildReportSHA256']
    build = json.loads(Path(fixture['buildReport']).read_text())
    assert build['passed']
    for section in ['inputs', 'dependencies', 'tools', 'linkedLibraries']:
        for path, digest in build[section].items():
            assert host.digest(path) == digest, path
    for rel, digest in build['artifacts'].items():
        assert host.digest(Path(fixture['buildReport']).parent / rel) == digest, rel
    for section in ['inputs', 'dependencies', 'tools', 'linkedLibraries']:
        for path, digest in plugin_build.get(section, {}).items():
            source = Path(path) if Path(path).is_absolute() else AUTH / path
            assert host.digest(source) == digest, source
    source_inputs = [Path(__file__), ROOT/'candidate_host.py', ROOT/'native-build-report.json', ROOT/'client-build-report.json',
                     ROOT/'link-build-report.json', ROOT/'aq-tuple.json', plugin_report, Path(fixture['buildReport'])]
    source_inputs += sorted((AUTH/'adapter').glob('*.py'))
    report['inputs'] = {str(path): host.digest(path) for path in source_inputs}
    report.update(clientBuild=fixture, coreBuild=core, pluginBuild=str(plugin_report), pluginSHA256=plugin_build['binarySHA256'])
    shutil.copy2(__file__, OUT/'native.py')
    captured = OUT/'inputs'
    for index, path in enumerate(source_inputs):
        target = captured/str(index)/path.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    with host.PrivateHyprSession(OUTPUT, dict(os.environ), 800, 600, LUA, mesa_vendor=True) as session:
        try:
            check('exactReviewedCoreMapped', session.evidence['hyprlandMaps']['files'].get(str(Path(core['binary']).resolve())) == core['sha256'])
            check('exactReviewedPrivateAquamarineMapped', session.evidence['privateAquamarine']['mappedVerified'] is True)
            check('geometryPluginLoaded', session.ctl('plugin', 'load', plugin).strip() == 'ok')
            loaded = True
            compositor = next(row for _, row in session.host.processes if row['name'] == 'hyprland')
            maps = host.original.mapped_files(compositor['pid'])
            check('exactGeometryPluginMapped', maps['files'].get(str(Path(plugin).resolve())) == plugin_build['binarySHA256'])
            report['pluginMapsAfterLoad'] = maps
            endpoint = GeometryEndpoint(runtime=str(session.host.runtime), instance=session.env['HYPRLAND_INSTANCE_SIGNATURE'],
                pid=compositor['pid'], expected_start=start_time(compositor['pid']), binary_sha256=core['sha256'])
            hello = endpoint.hello()
            check('legacyHelloUnchanged', hello['capabilities'] == {'observe':True,'effects':True,'minimizedState':True,'effectProtocol':1,
                'operations':['minimize','restore','activate'],'canonicalScene':False,'taskbarProjectionProtocol':1,'effectInvalidationProtocol':1})
            refused('localFactsBeforeAttachRefused', lambda: endpoint.geometry_facts(rid()))
            refused('nativeFactsBeforeAttachRefused', lambda: endpoint.request({'protocolVersion':3,'kind':'geometry-facts-request',
                'geometryProtocol':1,'binding':endpoint.bound,'requestId':rid(),'minimumWatermark':'0'}))
            attach = endpoint.geometry_attach(rid())
            check('separateObserverNegotiatesNoGeometryEffects', attach['capabilities'] == {'observe':True,'effects':False,
                'effectProtocol':2,'operations':[],'placementCapacity':256,'canonicalScene':False})
            client_log = OUTPUT/'xdg-max-client.log'
            output_stream = os.fdopen(os.open(client_log, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600), 'wb')
            session.host.logs.append(output_stream)
            client = subprocess.Popen([fixture['client']], stdin=subprocess.PIPE, stdout=output_stream, stderr=subprocess.STDOUT,
                env=dict(session.env, WAYLAND_DEBUG='1'), cwd=session.host.runtime, start_new_session=True)
            client_identity = host.original.process(client.pid)
            client_identity.update(name='xdg-max-client', command=[fixture['client']], log=str(client_log))
            session.host.processes.append((client, client_identity))
            session.host.evidence['xdgMaxClient'] = client_identity
            wait(lambda: any(row['event']=='ready' for row in events()))
            native = wait(native_window)
            report['fixtureIdentity'] = {'pid':client.pid,'address':native['address'],'title':native['title']}
            address = native['address']
            for operation, argument in [('setfloating','address:'+address), ('movewindowpixel','exact 83 61,address:'+address),
                                        ('resizewindowpixel','exact 320 180,address:'+address)]:
                check('ordinaryPlacementDispatch:'+operation, session.ctl('dispatch',operation,argument).strip()=='ok')
            wait(lambda: settled(0) if native_window() and native_window()['at']==[83,61] and native_window()['size']==[320,180] else None)
            request('sync')
            baseline = facts()
            original = correlate('ordinary', baseline, native_window(), 'ordinary')
            check('zeroMonitorIdentityAccepted', original['monitor']=='0')
            ownership = {key:original[key] for key in ('incarnation','workspace','workspaceGeneration','monitor','outputOwnershipGeneration','workAreaRevision','workArea')}
            previous = baseline
            for name, command, mode, changed in [('maximize','maximize',1,True), ('duplicate-maximize','maximize',1,False),
                                                ('restore','unmaximize',0,True), ('duplicate-restore','unmaximize',0,False)]:
                deadline = time.monotonic()+6
                packet = request(command,deadline=deadline)
                native, buffer = wait(lambda:settled(mode,packet['sequence'] if changed else None),deadline=deadline)
                response = wait(lambda:(lambda f: f if one_fact(f)['nativeMode']==('maximized' if mode else 'ordinary') and
                    one_fact(f)['logicalGeometry']==[*native['at'],*native['size']] else None)(facts()),deadline=deadline)
                row = correlate(name,response,native,'maximized' if mode else 'ordinary')
                if time.monotonic() >= deadline: raise RuntimeError('Unchanged six-second transition deadline')
                check(name+':exactNativePlacement', native['at']==([0,0] if mode else [83,61]) and native['size']==([800,600] if mode else [320,180]), buffer=buffer)
                check(name+':ownershipAndWorkareaStable', all(row[k]==v for k,v in ownership.items()))
                check(name+':geometryRevisionTracksChanges', int(response['revision'])>int(previous['revision']) if changed else response['revision']==previous['revision'])
                previous = response
            unchanged = facts()
            refused('unsupportedGeometryVersionRefused',lambda:endpoint.request({'protocolVersion':3,'kind':'geometry-attach',
                'geometryProtocol':2,'binding':endpoint.bound,'requestId':rid()}))
            intent = {'request':'1','generation':'1','incarnation':original['incarnation'],'operation':'maximize','context':endpoint.context(endpoint.scene_facts(rid()))}
            for attempt in range(2):
                refused('unsupportedGeometryEffectReplayRefused:'+str(attempt),lambda:endpoint.request({'protocolVersion':3,'kind':'window-effect',
                    'effectProtocol':2,'binding':endpoint.bound,'intent':intent}))
            check('unsupportedRequestsDoNotMutateGeometry', one_fact(facts())==one_fact(unchanged) and native_window()['at']==[83,61] and native_window()['size']==[320,180])
            old_bound = dict(endpoint.bound)
            endpoint.hello()
            refused('newHelloInvalidatesLocalAttach',lambda:endpoint.geometry_facts(rid()))
            refused('newHelloInvalidatesNativeAttach',lambda:endpoint.request({'protocolVersion':3,'kind':'geometry-facts-request',
                'geometryProtocol':1,'binding':endpoint.bound,'requestId':rid(),'minimumWatermark':'0'}))
            refused('staleGeometryBindingRefused',lambda:endpoint.request({'protocolVersion':3,'kind':'geometry-attach',
                'geometryProtocol':1,'binding':old_bound,'requestId':rid()}))
            endpoint.geometry_attach(rid())
            recovered = one_fact(facts())
            check('freshAttachRecoversSameNativeOwnership', all(recovered[k]==v for k,v in ownership.items()))
            client.stdin.write(b'quit\n');client.stdin.flush();client.stdin.close();client.wait(timeout=5)
            check('xdgClientNormalExit',client.returncode==0 and any(row['event']=='normalexit' for row in events()))
            wait(lambda:not any(row.get('address')==address for row in session.data('clients')))
            check('actualNativeWindowRetiredBeforeHostStop',not any(row.get('address')==address for row in session.data('clients')))
            wait(lambda:not facts()['facts']['windows'])
            check('geometryMemberRetired',not facts()['facts']['windows'])
            for path,digest in report['inputs'].items(): assert host.digest(path)==digest,path
            report['passed']=True
        finally:
            if client is not None and client.poll() is None:
                try:
                    client.stdin.write(b'quit\n');client.stdin.flush();client.stdin.close();client.wait(timeout=5)
                except Exception as error: report['clientCleanupError']=repr(error)
            if loaded:
                try:
                    check('pluginUnloadedBeforeHostStop',session.ctl('plugin','unload',plugin).strip()=='ok')
                    loaded=False
                except Exception as error: report['pluginCleanupError']=repr(error)
            registered={row['pid'] for proc,row in session.host.processes}
            for descendant in reversed([row for row in session.host.descendants() if row['pid'] not in registered]): session.host.stop(descendant)
except Exception as error:
    report.update(passed=False,error=repr(error),traceback=traceback.format_exc())
finally:
    if OUTPUT.exists(): shutil.copytree(OUTPUT,OUT/'native-evidence',dirs_exist_ok=True)
    if session is not None:
        report['privateHost']=session.evidence
        report['cleanupPassed']=not any(session.evidence.get(key) for key in ('cleanupErrors','unexpectedInnerDescendants','remainingDescendants')) and bool(session.evidence.get('runtimeGone'))
    else: report['cleanupPassed']=False
    report['passed']=report['passed'] and report['cleanupPassed'] and not report.get('clientCleanupError') and not report.get('pluginCleanupError')
    report['artifacts']={str(p.relative_to(OUT)):host.digest(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}),flush=True)
raise SystemExit(not report['passed'])
