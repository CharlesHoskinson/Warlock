"""Serial real pixel/pointer/keyboard qualification of a frozen native candidate."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent
stage = 'elm-input-region-fix-v23'
full_trace=sys.argv[1:]==['--trace-full-redraw']
if sys.argv[1:] and not full_trace:
    assert len(sys.argv)==3 and sys.argv[1]=='--core-stage' and sys.argv[2] in ('elm-input-region-fix-v23',), 'Unknown private core stage'
    stage=sys.argv[2]
CORE = REPO / 'implementation' / stage
spec = importlib.util.spec_from_file_location('scene_v9_private_host', CORE / 'candidate_host.py')
host = importlib.util.module_from_spec(spec)
spec.loader.exec_module(host)
sys.path.insert(0, str(CORE / 'adapter'))
from endpoint import start_time
from effect_endpoint import Endpoint

host.original.qa.require_qa_scope()
OUT = ROOT / 'qa' / ('native-' + str(time.time_ns()))
OUT.mkdir(parents=True)
OUTPUT = Path('/home/hoskinson/window-integration-qa') / ('elm-native-scene-' + str(time.time_ns()))
POINTER = Path('/home/hoskinson/.local/share/hypr-window-controls/qa/virtual-pointer')
KEYBOARD = Path('/home/hoskinson/window-integration-qa/orca-reader/physical-commands/evdev-keyboard')
report = {'passed': False, 'scope': 'Single-output private real pixel/pointer/MAX/modal regression; full release gates remain open',
          'mainDesktopActions': False, 'coreStage':stage, 'fixtureStage':'elm-input-region-fix-v23', 'output': str(OUTPUT), 'checks': [], 'captures': {}, 'pointerRuns': [], 'positionReceipts': []}
for path in (ROOT / 'qa/lifecycle_native.py', ROOT / 'birth_fixture.py', ROOT / 'pointer_fifo.py'):
    shutil.copy2(path, OUT / path.name)
report['inputs'] = {str(path): host.digest(path) for path in (ROOT / 'qa/lifecycle_native.py', ROOT / 'birth_fixture.py', ROOT / 'pointer_fifo.py', POINTER, KEYBOARD, KEYBOARD.with_suffix('.c'), CORE / 'candidate_host.py')}
loaded = []
apps = []
s = None

def record(name, passed, **evidence):
    report['checks'].append({'name': name, 'passed': bool(passed), **evidence})
    assert passed, name

def wait(predicate):
    deadline = time.monotonic() + 6
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(.04)
    raise RuntimeError('Original fixture observation deadline')

LUA = b'''hl.config({xwayland={enabled=false},animations={enabled=false},decoration={dim_modal=false},input={follow_mouse=2,float_switch_override_focus=0}})
hl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})
hl.on("window.open",function(w) hl.dispatch(hl.dsp.window.float({action="enable",window="address:"..w.address})) end)
'''

if full_trace:
    LUA=LUA.replace(b'decoration={dim_modal=false}',b'debug={damage_tracking=0,vfr=false},decoration={dim_modal=false}')
    report['configurationVariant']='Continuous full redraw diagnostic; no production performance claim'

try:
    fixture_manifest=json.loads((ROOT/'qa/source-manifest.json').read_text())
    for relative,digest in fixture_manifest['files'].items():assert host.digest(ROOT/relative)==digest,relative
    report['fixtureManifestSHA256']=host.digest(ROOT/'qa/source-manifest.json')
    manifest = json.loads((CORE / 'qa/build-pair-manifest.json').read_text())
    assert manifest['passed']
    for relative, digest in manifest['files'].items():
        assert host.digest(CORE / relative) == digest, relative
    pair = json.loads((REPO / 'implementation/maximized-stack-v2/plugin-build-report.json').read_text())
    assert pair['result'] == 'pass' and host.digest(pair['binary']) == pair['sha256']
    assert pair['owning_version_header_sha256'] == manifest['nativePair']['core']['versionHeaderSHA256']
    assert host.digest(pair['full_report']) == pair['full_report_sha256']
    owning = json.loads(Path(pair['full_report']).read_text())
    for path, digest in owning['compiler_dependency_headers'].items():
        assert host.digest(path) == digest, path
    report['pair'] = {'core': manifest['nativePair']['core'], 'authority': manifest['nativePair']['plugin'], 'titlebar': pair}
    report['sourceManifestSHA256'] = host.digest(CORE / 'qa/build-pair-manifest.json')
    with host.PrivateHyprSession(OUTPUT, dict(os.environ), 800, 600, LUA, mesa_vendor=True) as s:
        try:
            for plugin in [pair['binary'], manifest['nativePair']['plugin']['path']]:
                assert s.ctl('plugin', 'load', plugin).strip() == 'ok'
                loaded.append(plugin)
            row = next(row for proc, row in s.host.processes if row['name'] == 'hyprland')
            client = Endpoint(runtime=str(s.host.runtime), instance=s.env['HYPRLAND_INSTANCE_SIGNATURE'], pid=row['pid'],
                              expected_start=start_time(row['pid']), binary_sha256=manifest['nativePair']['core']['sha256'])
            client.hello()
            env = dict(s.env, GTK_A11Y='none', GSETTINGS_BACKEND='memory', GTK_USE_PORTAL='0')
            control = OUTPUT / 'fixture-control.json'
            app = s.host.launch('scene-fixture', ['/usr/bin/python3', '-B', str(ROOT / 'birth_fixture.py'), str(control)], env=env)
            apps.append(app)

            def window(title):
                return wait(lambda: next((w for w in s.data('clients') if w['title'] == title), None))

            def dispatch(text):
                reply = s.ctl('dispatch', text)
                assert reply.strip() == 'ok', reply

            def raise_(address):
                dispatch('hl.dsp.focus({window="address:' + address + '"})')
                dispatch('hl.dsp.window.alter_zorder({mode="top",window="address:' + address + '"})')

            def position(address, x, y, width, height):
                receipt = {'address':address,'target':[x,y,width,height],'before':s.data('clients')}
                report['positionReceipts'].append(receipt)
                dispatch(f'hl.dsp.window.float({{action="enable",window="address:{address}"}})')
                wait(lambda: next((w for w in s.data('clients') if w['address'] == address and w['floating']), None))
                dispatch(f'hl.dsp.window.resize({{x={width},y={height},window="address:{address}"}})')
                current = wait(lambda: next((w for w in s.data('clients') if w['address'] == address and w['size'] == [width,height]), None))
                # Correct explicit fixture placement from observed native geometry,
                # rather than assuming initial map/configure has settled its goal.
                dx, dy = x-current['at'][0], y-current['at'][1]
                receipt['afterResize'] = current
                receipt['moveDelta'] = [dx,dy]
                dispatch(f'hl.dsp.window.move({{x={dx},y={dy},relative=true,window="address:{address}"}})')
                wait(lambda: next((w for w in s.data('clients') if w['address'] == address and w['at'] == [x,y]), None))

            def snap(name, x=300, y=300):
                file = OUTPUT / (name + '.png')
                s.guard()
                subprocess.run(['grim', str(file)], env=s.env, check=True, timeout=5)
                pixel = subprocess.check_output(['magick', str(file), '-format', f'%[pixel:p{{{x},{y}}}]', 'info:'], text=True, timeout=5)
                value = {'pixel': pixel, 'point': [x,y], 'clients': s.data('clients'), 'active': s.data('activewindow'), 'image': str(file)}
                trace=client.request({'protocolVersion':3,'kind':'render-trace-request','binding':client.bound,'requestId':'90','minimumWatermark':'0'})
                value['renderTrace']=trace
                assert trace['kind']=='render-trace' and trace['binding']==client.bound and trace['requestId']=='90'
                report['captures'][name] = value
                expected={'peer-raised':'SCENE-PEER','max-raised':'SCENE-MAX','max-lowered':'SCENE-PEER','pinned-peer':'SCENE-PEER','unpinned-peer':'SCENE-MAX','first-class-minimized':'SCENE-PEER','first-class-restored':'SCENE-MAX'}.get(name)
                if full_trace and expected:
                    labels={w['incarnation']:w['label'] for w in client.snapshot('90')['windows']}
                    facts={w['incarnation']:w for w in client.scene_facts('90')['facts']['windows']}
                    frame=next(f for f in trace['frames'] if f['monitor']=='0')
                    record(name+'TraceCommittedAndComplete',frame['committed'] and frame['complete'] and not frame['overflow'],frame=frame['frame'])
                    at_probe=[]
                    for draw in frame['draws']:
                        identity=draw['incarnation']
                        if identity not in facts or not draw['main'] or draw['popup']:continue
                        gx,gy,gw,gh=facts[identity]['geometry']
                        if gx<=x<gx+gw and gy<=y<gy+gh:at_probe.append(labels[identity])
                    record(name+'ActualDrawOrderAtPixel',bool(at_probe) and at_probe[-1]==expected,drawOrder=at_probe,trace=trace)
                    if name=='first-class-minimized':
                        record('minimizedMAXAbsentFromActualSurfaceDraws',not any(labels.get(draw['incarnation'])=='SCENE-MAX' for draw in frame['draws']))
                return value

            def click(x, y):
                s.guard()
                process = subprocess.run([str(POINTER), '800', '600'],
                    input=f'move {x} {y}\nsleep 100\nbutton 272 1\nsleep 50\nbutton 272 0\nsleep 100\n',
                    text=True, capture_output=True, env=s.env, timeout=5)
                report['pointerRuns'].append({'point':[x,y], 'exitCode':process.returncode, 'stdout':process.stdout,
                    'stderr':process.stderr, 'waylandDisplay':s.env['WAYLAND_DISPLAY'], 'runtime':s.env['XDG_RUNTIME_DIR']})
                assert process.returncode == 0, process.stderr
                return s.data('activewindow').get('address')

            def color(capture, rgb):
                return rgb in capture['pixel'].replace(' ', '')

            def keyboard_recipient(expected):
                event_file = control.with_suffix('.events.jsonl')
                before = event_file.read_text().splitlines() if event_file.exists() else []
                s.guard()
                process = subprocess.run([str(KEYBOARD)], input='sleep 100\nkey 30 1\nsleep 50\nkey 30 0\nsleep 100\nsync\n',
                    text=True, capture_output=True, env=s.env, timeout=5)
                receipt = {'expected':expected,'exitCode':process.returncode,'stdout':process.stdout,'stderr':process.stderr,
                    'waylandDisplay':s.env['WAYLAND_DISPLAY'],'runtime':s.env['XDG_RUNTIME_DIR']}
                report.setdefault('keyboardRuns',[]).append(receipt)
                assert process.returncode == 0, process.stderr
                events = [json.loads(line) for line in event_file.read_text().splitlines()[len(before):]]
                receipt['events'] = events
                keys = [event for event in events if event['kind']=='key' and event['keyval']==97]
                return len(keys)==1 and keys[0]['window']==expected

            a, b = window('SCENE-MAX')['address'], window('SCENE-PEER')['address']
            dispatch('hl.dsp.window.fullscreen({mode="maximized",action="set",window="address:' + a + '"})')
            position(b, 200, 180, 320, 240)
            raise_(b); time.sleep(.25)
            peer = snap('peer-raised')
            record('peerOnTop', color(peer, '0,255,0') and peer['active']['address'] == b)
            raise_(a); time.sleep(.25)
            top = snap('max-raised')
            record('maxOnTop', color(top, '255,0,0') and top['active']['address'] == a)
            record('hitMatchesMax', click(300,300) == a)
            dispatch('hl.dsp.window.alter_zorder({mode="bottom",window="address:' + a + '"})')
            time.sleep(.25); lower = snap('max-lowered')
            record('loweringRestoresPeer', color(lower, '0,255,0'))
            raise_(b); dispatch('hl.dsp.window.pin({window="address:' + b + '"})'); raise_(a)
            time.sleep(.25); pinned = snap('pinned-peer')
            record('pinRemainsAbove', color(pinned, '0,255,0'))
            dispatch('hl.dsp.window.pin({window="address:' + b + '"})'); raise_(a)
            time.sleep(.25); unpinned = snap('unpinned-peer')
            record('unpinAndRaiseMax', color(unpinned, '255,0,0'))
            record('nativeModesPreserved', all(next(w for w in capture['clients'] if w['address'] == a)['fullscreen'] == 1
                for capture in (top, lower, pinned, unpinned)))
            # Opaque paint is unchanged; only the actual native input region changes.
            event_file = control.with_suffix('.events.jsonl')
            def control_input(op):
                prior=event_file.read_text().splitlines() if event_file.exists() else []
                temp=control.with_suffix('.tmp');payload={'op':op}
                if op=='input-hole-peer':payload['hole']=[80,80,80,80]
                temp.write_text(json.dumps(payload));temp.replace(control)
                return wait(lambda:next((json.loads(line) for line in event_file.read_text().splitlines()[len(prior):] if json.loads(line)['kind']=='input-region'),None))
            def pointer_recipient(x,y,expected,address):
                before_events=event_file.read_text().splitlines()
                active=click(x,y)
                delivered=[json.loads(line) for line in event_file.read_text().splitlines()[len(before_events):]]
                pointer=[e for e in delivered if e['kind'] in ('pressed','released')]
                return active==address and [e['kind'] for e in pointer]==['pressed','released'] and all(e['window']==expected for e in pointer),delivered
            raise_(b);dispatch('hl.dsp.window.pin({window="address:'+b+'"})')
            pre_hole=client.request({'protocolVersion':3,'kind':'retain-render-trace-request','binding':client.bound,'requestId':'49','minimumWatermark':'0'})
            input_receipt=control_input('input-hole-peer')
            time.sleep(.25)
            opaque=snap('opaque-peer-input-hole')
            record('opaquePeerStillPaintsInputHole',color(opaque,'0,255,0'),fixture=input_receipt)
            peer_identity=next(w['incarnation'] for w in client.snapshot('50')['windows'] if w['label']=='SCENE-PEER')
            hole_draw=wait(lambda:next((d for f in client.request({'protocolVersion':3,'kind':'render-trace-request','binding':client.bound,'requestId':'50','minimumWatermark':'0'})['frames'] for d in f['draws'] if d['incarnation']==peer_identity and d['main'] and not d['popup'] and len(d['input'])>1),None))
            record('inputFixtureUsesUntransformedUnitScaleMapping',hole_draw['box']==[200,180,320,240] and input_receipt['width']==320 and input_receipt['height']==240,draw=hole_draw,fixture=input_receipt)
            def inside_input(x,y):return any(rx<=x<rx+rw and ry<=y<ry+rh for rx,ry,rw,rh in hole_draw['input'])
            held=client.request({'protocolVersion':3,'kind':'retained-render-trace-request','binding':client.bound,'requestId':'49','minimumWatermark':'0'})
            record('retainedInputRegionUnchangedAfterNativeMutation',[[d['input'] for d in f['draws']] for f in held['frames']]==[[d['input'] for d in f['draws']] for f in pre_hole['frames']])
            record('nativeDrawCapturesActualInputHole',not inside_input(100,120) and inside_input(200,120),draw=hole_draw)
            hit,delivered=pointer_recipient(300,300,'SCENE-MAX',a)
            record('inputHolePassesPointerToUnderlyingMAX',hit,events=delivered)
            record('inputHoleFocusGivesUnderlyingKeyboard',keyboard_recipient('SCENE-MAX'))
            record('opaqueHolePaintUnchangedAfterUnderlyingFocus',color(snap('opaque-hole-after-focus'),'0,255,0'))
            record('opaquePeerStillPaintsOutsideHole',color(snap('opaque-peer-outside-hole',400,300),'0,255,0'))
            hit,delivered=pointer_recipient(400,300,'SCENE-PEER',b)
            record('outsideHoleGivesPointerToPeer',hit,events=delivered)
            record('outsideHoleFocusGivesPeerKeyboard',keyboard_recipient('SCENE-PEER'))
            full_receipt=control_input('input-full-peer');time.sleep(.25)
            restored_draw=wait(lambda:next((d for f in client.request({'protocolVersion':3,'kind':'render-trace-request','binding':client.bound,'requestId':'50','minimumWatermark':'0'})['frames'] for d in f['draws'] if d['incarnation']==peer_identity and d['main'] and not d['popup'] and any(rx<=100<rx+rw and ry<=120<ry+rh for rx,ry,rw,rh in d['input'])),None))
            record('nativeDrawCapturesRestoredFullInputRegion',bool(restored_draw),draw=restored_draw)
            hit,delivered=pointer_recipient(300,300,'SCENE-PEER',b)
            record('restoredInputRegionGivesPointerToPeer',hit,events=delivered,fixture=full_receipt)
            record('restoredInputRegionGivesPeerKeyboard',keyboard_recipient('SCENE-PEER'))
            dispatch('hl.dsp.window.pin({window="address:'+b+'"})');raise_(a)
            ids={w['label']:w['incarnation'] for w in client.snapshot('51')['windows']}
            def fact(response,identity): return next(w for w in response['facts']['windows'] if w['incarnation']==identity)
            before=client.scene_facts('51'); original=fact(before,ids['SCENE-MAX'])
            def effect(number,operation,context=None,identity=None):
                intent={'request':str(number),'generation':str(number),'incarnation':identity or ids['SCENE-MAX'],'operation':operation,'context':context or client.context(client.scene_facts(str(100+number)))}
                outcome=client.effect(intent);report.setdefault('effectRuns',[]).append({'intent':intent,'outcome':outcome});return intent,outcome
            min_intent,min_outcome=effect(1,'minimize',client.context(before))
            record('firstClassMinimizeCommitted',min_outcome['status']=='Committed')
            after=client.scene_facts('52'); minimized=fact(after,ids['SCENE-MAX']);report['minimizeFacts']=after
            record('minimizedHasDistinctNativeState',minimized['minimized'] and not minimized['hidden'])
            record('minimizedNativeEligibilityExcluded',not minimized['acceptsInput'] and not minimized['shouldRenderAny'] and not minimized['shouldRenderOwnMonitor'])
            record('minimizePreservesWorkspaceGeometryMode',all(minimized[key]==original[key] for key in ['workspace','geometry','fullscreenMode']))
            record('focusedMinimizeSelectsCommittedMRUSuccessor',after['facts']['focused']==ids['SCENE-PEER'])
            record('focusSuccessorActualKeyboardBeforeClick',keyboard_recipient('SCENE-PEER'))
            record('minimizedEntryStillEnumerated',next(w for w in client.snapshot('52')['windows'] if w['incarnation']==ids['SCENE-MAX'])['minimized'])
            time.sleep(.25);record('minimizedMAXPixelsExcluded',color(snap('first-class-minimized'),'0,255,0'))
            record('minimizedMAXPointerExcluded',click(300,300)==b)
            record('minimizedMAXKeyboardExcluded',keyboard_recipient('SCENE-PEER'))
            dispatch('hl.dsp.focus({window="address:'+a+'"})')
            record('minimizedDirectFocusRefused',s.data('activewindow').get('address')==b)
            retry=client.effect(min_intent);record('exactMinimizeRetryDeduplicated',retry==min_outcome)
            reordered={key:min_intent[key] for key in reversed(list(min_intent))};reordered['context']={key:min_intent['context'][key] for key in reversed(list(min_intent['context']))}
            record('semanticMinimizeRetryDeduplicated',client.effect(reordered)==min_outcome)
            reused=dict(min_intent,operation='restore');record('requestReuseRefused',client.effect(reused)['status']=='Refused')
            _,stale=effect(2,'restore',client.context(before));record('staleRevisionRestoreRefused',stale['status']=='Refused' and fact(client.scene_facts('53'),ids['SCENE-MAX'])['minimized'])
            _,restored=effect(3,'restore');record('firstClassRestoreCommitted',restored['status']=='Committed')
            current=fact(client.scene_facts('54'),ids['SCENE-MAX']);record('restorePreservesWorkspaceGeometryMode',not current['minimized'] and all(current[key]==original[key] for key in ['workspace','geometry','fullscreenMode']))
            time.sleep(.25);record('restoredMAXPixelsVisible',color(snap('first-class-restored'),'255,0,0'))
            record('restoredMAXActualKeyboardRecipient',keyboard_recipient('SCENE-MAX'))
            raise_(b);_,unfocused=effect(4,'minimize');record('unfocusedMinimizePreservesFocus',unfocused['status']=='Committed' and s.data('activewindow').get('address')==b)
            _,unfocused_restore=effect(5,'restore');record('unfocusedMinimizeRestores',unfocused_restore['status']=='Committed')
            _,dead=effect(6,'minimize',identity='18446744073709551615');record('unknownIncarnationRefused',dead['status']=='Refused')
            _,again=effect(7,'minimize');record('lastFamilySetupMinimizedMAX',again['status']=='Committed')
            _,last=effect(8,'minimize',identity=ids['SCENE-PEER']);last_facts=client.scene_facts('60')
            record('lastFamilyMinimizeClearsApplicationFocus',last['status']=='Committed' and last_facts['facts']['focused'] is None)
            event_file=control.with_suffix('.events.jsonl');before_keys=event_file.read_text().splitlines()
            s.guard();key_process=subprocess.run([str(KEYBOARD)],input='key 30 1\nsleep 50\nkey 30 0\nsleep 100\nsync\n',text=True,capture_output=True,env=s.env,timeout=5)
            delivered_keys=[json.loads(line) for line in event_file.read_text().splitlines()[len(before_keys):]]
            report['noApplicationKeyboard']={'exitCode':key_process.returncode,'stdout':key_process.stdout,'stderr':key_process.stderr,'events':delivered_keys}
            record('lastFamilyNoApplicationKeyboardDelivery',key_process.returncode==0 and not any(e['kind']=='key' for e in delivered_keys))
            _,back_a=effect(9,'restore');_,back_b=effect(10,'restore',identity=ids['SCENE-PEER']);record('lastFamilyRecoveryRestoresBoth',back_a['status']==back_b['status']=='Committed')
            raise_(a)
            # Historical special-workspace regression input, not desired minimize.
            dispatch('hl.dsp.window.move({workspace="special:scene-v9",follow=false,window="address:' + a + '"})')
            time.sleep(.25); inactive = snap('inactive-max')
            record('inactiveMAXPixelsExcluded', color(inactive, '0,255,0'))
            record('inactiveMAXHitExcluded', click(300,300) == b)
            facts = client.scene_facts('1')
            report['inactiveFacts'] = facts
            record('inactiveMAXFocusExcluded', s.data('activewindow').get('address') != a)
            temp = control.with_suffix('.tmp'); temp.write_text(json.dumps({'op':'family'})); temp.replace(control)
            owner, modal = window('SCENE-OWNER')['address'], window('SCENE-MODAL')['address']
            position(owner, 80,80,320,240); position(modal,180,160,180,130); position(b,560,80,160,130)
            time.sleep(.25)
            observations = client.snapshot('1')
            identities = {w['label']:w['incarnation'] for w in observations['windows']}
            family = client.scene_facts('2'); report['familyFacts'] = family
            modal_fact = next(w for w in family['facts']['windows'] if w['incarnation'] == identities['SCENE-MODAL'])
            peer_fact = next(w for w in family['facts']['windows'] if w['incarnation'] == identities['SCENE-PEER'])
            record('nativeModalAncestry', modal_fact['owner'] == identities['SCENE-OWNER'])
            record('sameProcessPeerIndependent', peer_fact['owner'] is None)
            raise_(b); time.sleep(.25)
            parent_pixels = snap('parent-click-point',120,130)
            record('parentClickPointVisible', color(parent_pixels,'255,0,0'))
            event_file=control.with_suffix('.events.jsonl')
            before_events=event_file.read_text().splitlines() if event_file.exists() else []
            record('parentClickRedirectsModalFocus', click(120,130) == modal)
            after_events=event_file.read_text().splitlines() if event_file.exists() else []
            delivered=[json.loads(line) for line in after_events[len(before_events):]]
            record('blockedParentClickNotDelivered',not any(event['kind'] in ('pressed','released') for event in delivered),events=delivered)
            record('parentRedirectActualKeyboardRecipient', keyboard_recipient('SCENE-MODAL'))
            record('peerClickRemainsIndependent', click(620,130) == b)
            record('independentPeerActualKeyboardRecipient', keyboard_recipient('SCENE-PEER'))
            raise_(modal); family_before=client.scene_facts('70')
            owner_id,modal_id=identities['SCENE-OWNER'],identities['SCENE-MODAL']
            original_family={identity:fact(family_before,identity) for identity in [owner_id,modal_id]}
            _,family_min=effect(11,'minimize',identity=owner_id);family_min_facts=client.scene_facts('71');report['familyMinimizeFacts']=family_min_facts
            record('nativeModalFamilyMinimizedTogether',family_min['status']=='Committed' and all(fact(family_min_facts,identity)['minimized'] and not fact(family_min_facts,identity)['acceptsInput'] and not fact(family_min_facts,identity)['shouldRenderOwnMonitor'] for identity in [owner_id,modal_id]))
            temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'late-child'}));temp.replace(control)
            late=window('SCENE-LATE')['address'];time.sleep(.25)
            late_ids={w['label']:w['incarnation'] for w in client.snapshot('73')['windows']};birth_facts=client.scene_facts('73');report['lateBirthFacts']=birth_facts
            late_fact=fact(birth_facts,late_ids['SCENE-LATE'])
            record('newChildOfMinimizedOwnerExcluded',late_fact['minimized'] and not late_fact['acceptsInput'] and not late_fact['shouldRenderOwnMonitor'] and birth_facts['facts']['focused']==identities['SCENE-PEER'])
            lx,ly,lw,lh=late_fact['geometry'];probe_x,probe_y=int(lx+lw/2),int(ly+lh/2)
            time.sleep(.25);late_pixels=snap('new-child-minimized-pixels',probe_x,probe_y)
            record('newChildMinimizedPixelsExcluded',not color(late_pixels,'0,0,255') and not color(late_pixels,'255,0,0'))
            record('newChildMinimizedActualKeyboardExcluded',keyboard_recipient('SCENE-PEER'))
            late_hit=click(probe_x,probe_y);record('newChildMinimizedPointerExcluded',late_hit not in [late,owner,modal])
            raise_(b)
            before_refusal=client.scene_facts('74')
            _,ambiguous=effect(13,'restore',identity=owner_id)
            after_refusal=client.scene_facts('75');report['ambiguousRestore']={'before':before_refusal,'outcome':ambiguous,'after':after_refusal}
            record('ambiguousRestoreRefusedBeforeMutation',ambiguous['status']=='Refused' and ambiguous['reason']=='ambiguous-or-ineligible-restore-focus' and after_refusal['facts']==before_refusal['facts'])
            temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'retire-late'}));temp.replace(control)
            wait(lambda:not any(w['address']==late for w in s.data('clients')))
            record('modalFamilyMinimizeFocusSuccessor',family_min_facts['facts']['focused']==identities['SCENE-PEER'] and keyboard_recipient('SCENE-PEER'))
            time.sleep(.25);family_absent=snap('minimized-modal-point',230,210);record('minimizedModalPixelsExcluded',not color(family_absent,'0,0,255') and not color(family_absent,'255,0,0'))
            _,family_restore=effect(14,'restore',identity=owner_id);family_restored=client.scene_facts('72');report['familyRestoreFacts']=family_restored
            record('nativeModalFamilyRestoredTogether',family_restore['status']=='Committed' and all(not fact(family_restored,identity)['minimized'] and all(fact(family_restored,identity)[key]==original_family[identity][key] for key in ['workspace','geometry','fullscreenMode']) for identity in [owner_id,modal_id]))
            record('modalFamilyRestoreSelectsActualModalKeyboard',family_restored['facts']['focused']==modal_id and keyboard_recipient('SCENE-MODAL'))
            time.sleep(.25);record('restoredModalPixelsVisible',color(snap('restored-modal-point',230,210),'0,0,255'))
            raise_(b)
            click(580,185);time.sleep(.25)
            before_grab=client.scene_facts('80');_,grabbed=effect(15,'minimize',identity=owner_id)
            after_grab=client.scene_facts('81');report['seatGrabRefusal']={'before':before_grab,'outcome':grabbed,'after':after_grab}
            record('actualPopoverGrabRefusesEffect',grabbed['status']=='Refused' and grabbed['reason']=='seat-grab' and before_grab['facts']==after_grab['facts'])
            temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'close-popup'}));temp.replace(control)
            time.sleep(.25)
            _,after_popup=effect(16,'minimize',identity=owner_id);record('popoverClosureAllowsFreshMinimize',after_popup['status']=='Committed')
            _,after_popup_restore=effect(17,'restore',identity=owner_id);record('popoverClosureRestoreKeyboardVerified',after_popup_restore['status']=='Committed' and keyboard_recipient('SCENE-MODAL'))
            raise_(b)
            # Hold one physical-device incarnation across modal retirement.
            fifo = OUTPUT / 'held-pointer.fifo'
            os.mkfifo(fifo, 0o600)
            descriptor = os.open(fifo, os.O_RDWR)
            writer = os.fdopen(descriptor,'w')
            held = s.host.launch('held-pointer', ['/usr/bin/python3','-B',str(ROOT/'pointer_fifo.py'),str(fifo),str(POINTER)],env=s.env)
            apps.append(held)
            try:
                before_events = event_file.read_text().splitlines()
                writer.write('move 120 130\nsleep 100\nbutton 272 1\nsleep 100\n');writer.flush()
                wait(lambda:s.data('activewindow').get('address')==modal)
                record('heldParentPressRedirectsModal',held.poll() is None)
                temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':'retire-modal'}));temp.replace(control)
                wait(lambda:not any(w['address']==modal for w in s.data('clients')))
                writer.write('move 620 130\nsleep 100\nbutton 272 0\nsleep 100\n');writer.flush()
                time.sleep(.35)
                delivered=[json.loads(line) for line in event_file.read_text().splitlines()[len(before_events):]]
                record('modalRetirementHeldReleaseNotDelivered',not any(e['kind'] in ('pressed','released') for e in delivered),events=delivered)
            finally:
                writer.close()
                held.wait(timeout=5)
                fifo.unlink()
            record('heldPointerNormalExit',held.returncode==0)
            record('independentPeerAfterModalRetirement',click(620,130)==b and keyboard_recipient('SCENE-PEER'))
            if full_trace:
                old_peer_id=next(w['incarnation'] for w in client.snapshot('91')['windows'] if w['label']=='SCENE-PEER')
                # Full redraw is only required for this retained-frame experiment.
                click(620,130);time.sleep(.25)
                def trace(kind):return client.request({'protocolVersion':3,'kind':kind,'binding':client.bound,'requestId':'92','minimumWatermark':'0'})
                retained=wait(lambda:(lambda t:t if any(d['incarnation']==old_peer_id for f in t['frames'] for d in f['draws']) else None)(trace('retain-render-trace-request')))
                old_draw=next(d for f in retained['frames'] for d in f['draws'] if d['incarnation']==old_peer_id and d['main'] and not d['popup'])
                position(b,560,80,180,140)
                resized=wait(lambda:(lambda t:t if any(d['incarnation']==old_peer_id and d['main'] and d['box']!=old_draw['box'] for f in t['frames'] for d in f['draws']) else None)(trace('render-trace-request')))
                after_resize=trace('retained-render-trace-request')
                preserved=next(d for f in after_resize['frames'] for d in f['draws'] if d['incarnation']==old_peer_id and d['main'] and not d['popup'])
                record('retainedDrawGeometryImmutableAfterResize',preserved['box']==old_draw['box'] and preserved['input']==old_draw['input'] and preserved['surface']==old_draw['surface'],old=old_draw,retained=preserved)
                current_draw=next(d for f in resized['frames'] for d in f['draws'] if d['incarnation']==old_peer_id and d['main'] and not d['popup'] and d['box']!=old_draw['box'])
                record('freshDrawCapturesResizedBoxAndStableSurface',current_draw['surface']==old_draw['surface'] and current_draw['box'][2]==180 and current_draw['box'][3]==140,new=current_draw)
                frame=resized['frames'][0]
                record('drawCapturesOutputConfiguration',frame['outputConfiguration']==[0,0,800,600,1] and frame['outputTransform']==0 and int(frame['configurationGeneration'])>0,frame=frame)
                def control_peer(op):
                    temp=control.with_suffix('.tmp');temp.write_text(json.dumps({'op':op}));temp.replace(control)
                control_peer('hide-peer');wait(lambda:not any(w['title']=='SCENE-PEER' for w in s.data('clients')))
                hidden=trace('retained-render-trace-request')
                old_draws=[d for f in hidden['frames'] for d in f['draws'] if d['incarnation']==old_peer_id]
                record('retainedDrawKeepsOriginalIdentityAfterUnmap',bool(old_draws) and all(d['retired'] and d['authority']==client.bound['lifetime'] for d in old_draws),trace=hidden)
                control_peer('show-peer');wait(lambda:any(w['title']=='SCENE-PEER' for w in s.data('clients')))
                new_peer_id=next(w['incarnation'] for w in client.snapshot('93')['windows'] if w['label']=='SCENE-PEER')
                remapped=trace('retained-render-trace-request')
                record('retainedDrawNeverRelabeledAfterRemap',new_peer_id!=old_peer_id and any(d['incarnation']==old_peer_id and d['retired'] for f in remapped['frames'] for d in f['draws']) and not any(d['incarnation']==new_peer_id for f in remapped['frames'] for d in f['draws']),oldIdentity=old_peer_id,newIdentity=new_peer_id,trace=remapped)
                time.sleep(.25);fresh=trace('render-trace-request')
                record('freshDrawUsesNewMappedIdentity',any(d['incarnation']==new_peer_id and d['authority']==client.bound['lifetime'] and not d['retired'] for f in fresh['frames'] for d in f['draws']),trace=fresh)
                report['identityTracePackets']=[retained,resized,after_resize,hidden,remapped,fresh]
            temp = control.with_suffix('.tmp'); temp.write_text(json.dumps({'op':'quit'})); temp.replace(control)
            app.wait(timeout=5); record('fixtureNormalExit', app.returncode == 0)
            report['passed'] = True
        finally:
            report['lastNativeState'] = {'clients':s.data('clients'),'active':s.data('activewindow')}
            for process in reversed(apps):
                if process.poll() is None:
                    row = next(row for owned,row in s.host.processes if owned is process)
                    s.host.stop(row,process);process.wait(timeout=5)
            for plugin in reversed(loaded):
                s.guard(); assert s.ctl('plugin','unload',plugin).strip() == 'ok'
            registered = {row['pid'] for _,row in s.host.processes}
            for row in reversed([row for row in s.host.descendants() if row['pid'] not in registered]):
                s.host.stop(row)
except Exception as error:
    report['error'] = repr(error)
    report['traceback'] = traceback.format_exc()
report['privateHost'] = s.evidence if s else None
report['cleanupPassed'] = bool(s and not s.evidence.get('cleanupErrors') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone'))
report['passed'] = report['passed'] and report['cleanupPassed']
if OUTPUT.exists():
    shutil.copytree(OUTPUT, OUT / 'native-evidence', symlinks=True)
report['artifacts'] = {str(path.relative_to(OUT)):host.digest(path) for path in sorted(OUT.rglob('*')) if path.is_file() and not path.is_symlink()}
(OUT / 'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(OUT / 'report.json'),'error':report.get('error')}))
raise SystemExit(not report['passed'])
