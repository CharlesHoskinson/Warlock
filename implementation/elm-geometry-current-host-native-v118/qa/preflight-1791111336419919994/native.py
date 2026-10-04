"""Reviewed real xdg maximize/restore roundtrip, private host only.

Native authority effects only; no Elm menu transport claim. Configure/ACK/buffer records,
native readback and independently captured pixels are separate evidence.
"""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import time
import traceback

import sys

SLICE = Path(__file__).resolve().parents[1]
REPO = SLICE.parents[1]
ROOT = REPO / 'implementation/elm-geometry-current-private-host-links-v112'
FIXTURE = REPO / 'implementation/elm-geometry-client-suspend-v53'
AUTH = REPO / 'implementation/elm-parent-first-anchor-pair-v90'
ADAPTER = REPO / 'implementation/elm-window-geometry-effect-adapter-v43/adapter'
sys.path.insert(0, str(Path(__file__).parent))
from tuple_preflight import verify_frozen_tuple
sys.path.insert(0, str(ADAPTER))
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
          'geometryEffectsImplemented': True, 'scope': 'Actual negotiated native geometry effects and shared legacy IDs, maximize/minimize/restore composition, exact client configure/interior pixels, no Elm menu, workarea-change or ownership-replacement qualification', 'checks': []}
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


def settled(mode, after_sequence=None, suspended=False):
    row, buffer = native_window(), latest_buffer()
    if row is None or buffer is None:
        return None
    expected_maximized = mode == 1
    if row.get('fullscreen') != mode or row.get('fullscreenClient') != mode or row.get('xwayland') is not False:
        return None
    if buffer.get('maximized') is not expected_maximized or buffer.get('fullscreen') is not False or buffer.get('suspended') is not suspended:
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
    check(name + ':logicalAndVisualMatchRawNativeGeometry', row['logicalGeometry'] == (row['workArea'] if mode == 'maximized' else [*native['at'], *native['size']]) and
          row['visualGeometry'] == [*native['at'], *native['size']], geometry=row)
    check(name + ':actualNativeAndClientMode', row['nativeMode'] == row['clientMode'] == mode and
          native['fullscreen'] == native['fullscreenClient'] == (1 if mode == 'maximized' else 0))
    monitors = session.data('monitors')
    monitor = next(m for m in monitors if str(m['id']) == row['monitor'])
    workspace = native['workspace']['id']
    check(name + ':actualWorkspaceOutputAndWorkarea', row['workspace'] == str(workspace) and row['owner'] is None and
          row['monitor'] == str(native['monitor']) and monitor['width'] == 800 and monitor['height'] == 600 and
          monitor['scale'] == 1 and monitor['reserved'] == [0, 0, 0, 0] and row['workArea'] == [0, 0, 800, 600], monitor=monitor)
    expected_caps = {'maximize': mode == 'ordinary', 'restoreGeometry': mode == 'maximized'}
    check(name + ':truthfulGeometryCapabilitiesAndConstraints', row['capabilities'] == expected_caps and
          row['fixedSize'] is False and row['constrainedSize'] is False and row['grouped'] is False and
          row['minimized'] is False and row['floating'] is True and row['geometryEligible'] is True and
          row['ordinaryPlacementKnown'] == (mode == 'maximized') and response['facts']['inputBlocked'] is False)

    return row


def validate_pixels(name, native, buffer, deadline=None):
    serial = buffer['ackedSerial']
    check(name + ':bufferUsesItsExactAckedConfigure', serial == buffer['serial'] and
          any(row['event'] == 'configure' and row['serial'] == serial and row['ackedSerial'] == serial and
              row['sequence'] < buffer['sequence'] and [row['width'], row['height']] == native['size']
              for row in events()), buffer=buffer)
    # Independent serial-color oracle, not the client's emitted argb alone.
    rgb = [0x28 ^ (serial & 63), 0x71 ^ ((serial >> 6) & 63), 0xc8 ^ ((serial >> 12) & 63)]
    argb = 'ff' + ''.join(f'{part:02x}' for part in rgb)
    check(name + ':serialColorHasNoCollision', buffer.get('argb') == argb and
          (argb not in selected_colors or selected_colors[argb] == serial), serial=serial, argb=argb)
    selected_colors[argb] = serial
    x, y = native['at']
    width, height = native['size']
    points = [(x + width // 2, y + height // 2), (x + 12, y + 12), (x + width - 13, y + height - 13)]
    attempts = []

    def capture(deadline):
        path = OUTPUT / (name + '-pixels-' + str(len(attempts)) + '.png')
        session.guard()
        def unchanged():
            current = native_window()
            latest = latest_buffer()
            return current is not None and all(current.get(key) == native.get(key) for key in
                ('address', 'pid', 'at', 'size', 'fullscreen', 'fullscreenClient')) and latest == buffer
        if not unchanged():
            raise RuntimeError('Native window or selected exact buffer changed before pixel capture')
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError('Unchanged six-second observation deadline')
        result = subprocess.run(['/usr/bin/grim', str(path)], env=session.env, capture_output=True, timeout=min(5, remaining))
        if result.returncode:
            raise RuntimeError('Owned child grim failed: ' + result.stderr.decode(errors='replace'))
        png = path.read_bytes()
        if png[:8] != bytes.fromhex('89504e470d0a1a0a') or png[12:16] != b'IHDR' or struct.unpack('>II', png[16:24]) != (800, 600):
            raise RuntimeError('Screenshot is not the actual private 800x600 child output')
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError('Unchanged six-second observation deadline')
        decoded = subprocess.run(['/usr/bin/magick', str(path), '-depth', '8', 'rgb:-'], capture_output=True, timeout=min(5, remaining))
        if decoded.returncode or len(decoded.stdout) != 800 * 600 * 3:
            raise RuntimeError('Actual screenshot RGB decoding failed')
        samples = []
        for px, py in points:
            if type(px) is not int or type(py) is not int or not (0 <= px < 800 and 0 <= py < 600):
                raise RuntimeError('Pixel sample is outside exact output geometry')
            offset = (py * 800 + px) * 3
            samples.append(list(decoded.stdout[offset:offset + 3]))
        attempts.append({'path': str(path), 'sha256': host.digest(path), 'points': points, 'samples': samples})
        report.setdefault('pixelAttempts', []).append(attempts[-1])
        if not unchanged():
            raise RuntimeError('Native window or selected exact buffer changed during pixel capture')
        return attempts[-1] if all(sample == rgb for sample in samples) else None

    matched = wait(capture, timed=True, deadline=deadline)
    check(name + ':actualInteriorPixelsMatchSelectedConfigure', bool(matched), expectedRGB=rgb, capture=matched)

effect_number = 0

def intent_for(operation, geometry=True):
    global effect_number
    effect_number += 1
    observed = facts() if geometry else endpoint.scene_facts(rid())
    return {'request':str(effect_number),'generation':str(effect_number),
            'incarnation':report['nativeIncarnation'],'operation':operation,
            'context':endpoint.geometry_context(observed) if geometry else endpoint.context(observed)}

def native_effect(name, operation, mode, changed, geometry=True):
    deadline = time.monotonic() + 6
    before = latest_buffer()
    intent = intent_for(operation, geometry)
    if time.monotonic() >= deadline: raise RuntimeError('Unchanged six-second transition deadline before send')
    receipt = endpoint.geometry_effect(intent) if geometry else endpoint.effect(intent)
    report.setdefault('effectReceipts',[]).append({'name':name,'intent':intent,'receipt':receipt})
    check(name+':exactSharedIntentCommitted', receipt['status']=='Committed' and receipt['intent']==intent and
          receipt['effectProtocol']==(2 if geometry else 1), receipt=receipt)
    if operation=='minimize':
        response = wait(lambda:(lambda f:f if one_fact(f)['minimized'] else None)(facts()),deadline=deadline)
        native, suspended_buffer = wait(lambda:settled(1,before['sequence'],suspended=True),deadline=deadline)
        row = one_fact(response)
        check(name+':retainsMaximizedModeAndOriginal', row['nativeMode']==row['clientMode']=='maximized' and
              row['ordinaryPlacementKnown'] is True and row['geometryEligible'] is False and
              row['capabilities']=={'maximize':False,'restoreGeometry':False} and
              native['fullscreen']==native['fullscreenClient']==1 and native['acceptsInput'] is False,
              native=native, geometry=row, buffer=suspended_buffer)
        if time.monotonic() >= deadline: raise RuntimeError('Unchanged six-second transition deadline')
        return intent,receipt,response
    native,buffer = wait(lambda:settled(mode,before['sequence'] if changed else None),deadline=deadline)
    response = wait(lambda:(lambda f:f if one_fact(f)['visualGeometry']==[*native['at'],*native['size']] and
        not one_fact(f)['minimized'] and one_fact(f)['nativeMode']==('maximized' if mode else 'ordinary') else None)(facts()),deadline=deadline)
    row = correlate(name,response,native,'maximized' if mode else 'ordinary')
    check(name+':exactNativePlacement', native['at']==([1,1] if mode else [83,61]) and
          native['size']==([798,598] if mode else [320,180]), native=native, buffer=buffer)
    check(name+':ownershipAndWorkareaStable',all(row[k]==v for k,v in ownership.items()))
    validate_pixels(name,native,buffer,deadline=deadline)
    if time.monotonic() >= deadline: raise RuntimeError('Unchanged six-second transition deadline')
    return intent,receipt,response

try:
    core = host.base.core_tuple()
    host.pair_tuple()
    fixture = json.loads((FIXTURE/'client-build-report.json').read_text())
    assert fixture['requiresXdgVersion']==6 and fixture['suspendedStateObserved'] is True
    assert host.digest(FIXTURE/'client-build-report.json')=='a6fa464f3390d64e8e18b3275d1cbb2d5cc2b5bed55df635fc27166f347911cc'
    descriptor_path = AUTH/'native-build-report.json'
    descriptor = json.loads(descriptor_path.read_text())
    plugin_report = Path(descriptor['pluginBuildReport'])
    assert host.digest(plugin_report)==descriptor['pluginBuildReportSHA256']
    plugin_build = json.loads(plugin_report.read_text())
    assert plugin_build['passed'] and not plugin_build['missingSymbols']
    plugin = plugin_build['binary']
    assert host.digest(plugin)==plugin_build['binarySHA256']==descriptor['plugin']['sha256']
    assert plugin==descriptor['plugin']['path']
    assert plugin_build['core']['path']==core['binary'] and plugin_build['core']['sha256']==core['sha256']
    for section in ['inputs','dependencies','tools','linkedLibraries']:
        for path,digest in plugin_build[section].items():
            source=Path(path) if Path(path).is_absolute() else AUTH/path
            assert host.digest(source)==digest,source
    for rel,digest in plugin_build['owningHeaders'].items():assert host.digest(plugin_report.parent/'owning-headers'/rel)==digest,rel
    for rel,digest in plugin_build['artifacts'].items():assert host.digest(plugin_report.parent/rel)==digest,rel
    assert host.digest(fixture['client'])==fixture['clientSHA256'] and host.digest(fixture['buildReport'])==fixture['buildReportSHA256']
    client_build=json.loads(Path(fixture['buildReport']).read_text());assert client_build['passed']
    for section in ['inputs','dependencies','tools','linkedLibraries']:
        for path,digest in client_build[section].items():assert host.digest(path)==digest,path
    for rel,digest in client_build['artifacts'].items():assert host.digest(Path(fixture['buildReport']).parent/rel)==digest,rel
    manifest_path,core_component,original_manifest=verify_frozen_tuple(REPO,AUTH,descriptor)
    closure_path=Path(descriptor['linkClosureReport'])
    assert host.digest(closure_path)==descriptor['linkClosureReportSHA256']
    closure=json.loads(closure_path.read_text());assert closure['passed'] and closure['missingSymbols']==[]
    assert closure['core']==plugin_build['core'] and closure['plugin']==descriptor['plugin']
    assert host.digest(core_component)==descriptor['coreComponentManifestSHA256']
    source_inputs=[Path(__file__),ROOT/'candidate_host.py',ROOT/'core_host.py',ROOT/'native-build-report.json',ROOT/'aq-tuple.json',ROOT/'source-origins.json',
                   FIXTURE/'client-build-report.json',descriptor_path,plugin_report,manifest_path,core_component,Path(fixture['buildReport']),Path('/usr/bin/grim'),Path('/usr/bin/magick')]
    source_inputs+=[Path(__file__).with_name('tuple_preflight.py'),original_manifest,closure_path,Path(core['buildReport'])]
    source_inputs+=sorted(ADAPTER.glob('*.py'))
    report['inputs']={str(p):host.digest(p) for p in source_inputs}
    report.update(clientBuild=fixture,coreBuild=core,pluginBuild=str(plugin_report),pluginSHA256=plugin_build['binarySHA256'])
    shutil.copy2(__file__,OUT/'native.py')
    for index,path in enumerate(source_inputs):
        target=OUT/'inputs'/str(index)/path.name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
    with host.PrivateHyprSession(OUTPUT,dict(os.environ),800,600,LUA,mesa_vendor=True) as session:
        try:
            check('exactReviewedCoreMapped',session.evidence['hyprlandMaps']['files'].get(str(Path(core['binary']).resolve()))==core['sha256'])
            check('exactReviewedPrivateAquamarineMapped',session.evidence['privateAquamarine']['mappedVerified'] is True)
            check('geometryPluginLoaded',session.ctl('plugin','load',plugin).strip()=='ok');loaded=True
            compositor=next(row for _,row in session.host.processes if row['name']=='hyprland')
            maps=host.original.mapped_files(compositor['pid'])
            check('exactGeometryPluginMapped',maps['files'].get(str(Path(plugin).resolve()))==plugin_build['binarySHA256'])
            report['pluginMapsAfterLoad']=maps
            endpoint=GeometryEndpoint(runtime=str(session.host.runtime),instance=session.env['HYPRLAND_INSTANCE_SIGNATURE'],
                pid=compositor['pid'],expected_start=start_time(compositor['pid']),binary_sha256=core['sha256'])
            hello=endpoint.hello()
            check('legacyHelloUnchanged',hello['capabilities']=={'observe':True,'effects':True,'minimizedState':True,'effectProtocol':1,
                'operations':['minimize','restore','activate'],'canonicalScene':False,'taskbarProjectionProtocol':1,'effectInvalidationProtocol':1})
            refused('localFactsBeforeAttachRefused',lambda:endpoint.geometry_facts(rid()))
            refused('nativeFactsBeforeAttachRefused',lambda:endpoint.request({'protocolVersion':3,'kind':'geometry-facts-request',
                'geometryProtocol':1,'binding':endpoint.bound,'requestId':rid(),'minimumWatermark':'0'}))
            refused('nativeEffectBeforeAttachRefused',lambda:endpoint.request({'protocolVersion':3,'kind':'window-effect','effectProtocol':2,
                'binding':endpoint.bound,'intent':{'request':'1','generation':'1','incarnation':'1','operation':'maximize',
                'context':{'lifetime':endpoint.bound['lifetime'],'epoch':endpoint.bound['frontend'],'output':'1','revision':'1'}}}))
            attach=endpoint.geometry_attach(rid())
            check('explicitGeometryEffectsNegotiated',attach['capabilities']=={'observe':True,'effects':True,'effectProtocol':2,
                'operations':['maximize','restore-geometry'],'placementCapacity':256,'canonicalScene':False})
            client_log=OUTPUT/'xdg-max-client.log'
            output_stream=os.fdopen(os.open(client_log,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'wb');session.host.logs.append(output_stream)
            client=subprocess.Popen([fixture['client']],stdin=subprocess.PIPE,stdout=output_stream,stderr=subprocess.STDOUT,
                env=dict(session.env,WAYLAND_DEBUG='1'),cwd=session.host.runtime,start_new_session=True)
            client_identity=host.original.process(client.pid);client_identity.update(name='xdg-max-client',command=[fixture['client']],log=str(client_log))
            session.host.processes.append((client,client_identity));session.host.evidence['xdgMaxClient']=client_identity
            wait(lambda:any(row['event']=='ready' for row in events()));native=wait(native_window)
            report['fixtureIdentity']={'pid':client.pid,'address':native['address'],'title':native['title']};address=native['address']
            border=session.data('getoption','general:border_size');check('exactNativeBorderPolicy',border.get('int')==1,option=border)
            selector=json.dumps('address:'+address)
            for operation,fields in [('float','action="enable"'),('resize','x=320,y=180,relative=false'),('move','x=83,y=61,relative=false')]:
                expression='hl.dsp.window.'+operation+'({'+fields+',window='+selector+'})'
                code='local r=hl.dispatch('+expression+'); if type(r)~="table" or r.ok~=true then error("placement dispatch refused") end'
                check('ordinaryPlacementDispatch:'+operation,session.ctl('eval',code).strip()=='ok',expression=expression)
            native,buffer=wait(lambda:settled(0) if native_window() and native_window()['at']==[83,61] and native_window()['size']==[320,180] else None)
            request('sync');baseline=facts();original=correlate('ordinary',baseline,native,'ordinary')
            report['nativeIncarnation']=original['incarnation']
            ownership={key:original[key] for key in ('incarnation','workspace','workspaceGeneration','monitor','outputOwnershipGeneration','workAreaRevision','workArea')}
            validate_pixels('ordinary',native,buffer)
            max_intent,max_receipt,max_facts=native_effect('maximize','maximize',1,True)
            duplicate_deadline=time.monotonic()+6
            duplicate=endpoint.geometry_effect(max_intent)
            check('exactGeometryRetryReturnsOriginalReceipt',duplicate==max_receipt and one_fact(facts())==one_fact(max_facts))
            validate_pixels('exact-maximize-retry',*wait(lambda:settled(1),deadline=duplicate_deadline),deadline=duplicate_deadline)
            conflict={**max_intent,'operation':'restore-geometry'}
            conflicting=endpoint.geometry_effect(conflict)
            check('changedPayloadSameIdentityRefused',conflicting['status']=='Refused' and conflicting['reason']=='request-reuse')
            cross=endpoint.effect({**max_intent,'operation':'minimize'})
            check('effectVersionCannotReuseSharedIdentity',cross['status']=='Refused' and cross['reason']=='request-reuse')
            native_effect('desired-maximize-duplicate','maximize',1,False)
            max_bound=dict(endpoint.bound)
            endpoint.hello()
            refused('maxHelloInvalidatesNegotiation',lambda:endpoint.geometry_facts(rid()))
            refused('maxHelloRejectsPriorBinding',lambda:endpoint.request({'protocolVersion':3,'kind':'window-effect',
                'effectProtocol':2,'binding':max_bound,'intent':max_intent}))
            endpoint.geometry_attach(rid());retained=one_fact(facts())
            check('maxOriginalSurvivesFrontendHello',retained['ordinaryPlacementKnown'] is True and
                  retained['nativeMode']==retained['clientMode']=='maximized' and retained['capabilities']['restoreGeometry'] is True and
                  all(retained[k]==v for k,v in ownership.items()),geometry=retained)
            native_effect('minimize-maximized','minimize',1,False,geometry=False)
            native_effect('restore-minimized-maximized','restore',1,True,geometry=False)
            native_effect('restore-geometry','restore-geometry',0,True)
            native_effect('desired-restore-duplicate','restore-geometry',0,False)
            old_bound=dict(endpoint.bound);endpoint.hello()
            refused('newHelloInvalidatesLocalAttach',lambda:endpoint.geometry_facts(rid()))
            refused('newHelloInvalidatesNativeEffectNegotiation',lambda:endpoint.request({'protocolVersion':3,'kind':'window-effect',
                'effectProtocol':2,'binding':endpoint.bound,'intent':max_intent}))
            refused('staleGeometryBindingRefused',lambda:endpoint.request({'protocolVersion':3,'kind':'geometry-attach',
                'geometryProtocol':1,'binding':old_bound,'requestId':rid()}))
            endpoint.geometry_attach(rid());recovered=one_fact(facts())
            check('freshAttachRecoversSameNativeOwnership',all(recovered[k]==v for k,v in ownership.items()) and recovered['ordinaryPlacementKnown'] is False)
            client.stdin.write(b'quit\n');client.stdin.flush();client.stdin.close();client.wait(timeout=5)
            check('xdgClientNormalExit',client.returncode==0 and any(row['event']=='normalexit' for row in events()))
            wait(lambda:not any(row.get('address')==address for row in session.data('clients')))
            check('actualNativeWindowRetiredBeforeHostStop',not any(row.get('address')==address for row in session.data('clients')))
            wait(lambda:not facts()['facts']['windows']);check('geometryMemberRetired',not facts()['facts']['windows'])
            for path,digest in report['inputs'].items():assert host.digest(path)==digest,path
            report['passed']=True
        finally:
            if client is not None and client.poll() is None:
                try:client.stdin.write(b'quit\n');client.stdin.flush();client.stdin.close();client.wait(timeout=5)
                except Exception as error:report['clientCleanupError']=repr(error)
            if client is not None:
                check('normalGeometryClientExitBeforePluginUnload',client.poll()==0)
            if loaded:
                wait(lambda:True if session.data('clients')==[] else None)
                check('nativeGeometryClientsEmptyBeforePluginUnload',session.data('clients')==[])
                try:check('pluginUnloadedBeforeHostStop',session.ctl('plugin','unload',plugin).strip()=='ok');loaded=False
                except Exception as error:report['pluginCleanupError']=repr(error)
            registered={row['pid'] for proc,row in session.host.processes}
            for descendant in reversed([row for row in session.host.descendants() if row['pid'] not in registered]):session.host.stop(descendant)
except Exception as error:report.update(passed=False,error=repr(error),traceback=traceback.format_exc())
finally:
    if OUTPUT.exists():shutil.copytree(OUTPUT,OUT/'native-evidence',dirs_exist_ok=True)
    if session is not None:
        report['privateHost']=session.evidence
        report['cleanupPassed']=not any(session.evidence.get(key) for key in ('cleanupErrors','unexpectedInnerDescendants','remainingDescendants')) and bool(session.evidence.get('runtimeGone'))
    else:report['cleanupPassed']=False
    report['passed']=report['passed'] and report['cleanupPassed'] and not report.get('clientCleanupError') and not report.get('pluginCleanupError')
    report['artifacts']={str(p.relative_to(OUT)):host.digest(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}),flush=True)
raise SystemExit(not report['passed'])
