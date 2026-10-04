"""Protected parent Weston pointer to nested GTK recipient qualification."""
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
REPO = ROOT.parents[1]
INPUT = REPO/'implementation/elm-parent-input-probe-v10'
BASE = ROOT
spec = importlib.util.spec_from_file_location('parent_input_reviewed_host', BASE/'candidate_host.py')
reviewed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reviewed)
reviewed.original.qa.require_qa_scope()
sys.path.insert(0,str(ROOT))
from pixels import pixels
probe_spec = importlib.util.spec_from_file_location('parent_input_inspection', INPUT/'qa/fixture-inspection.py')
inspection = importlib.util.module_from_spec(probe_spec)
probe_spec.loader.exec_module(inspection)

OUT = ROOT/'qa'/('native-'+str(time.time_ns()))
OUT.mkdir(mode=0o700)
OUTPUT = Path('/home/hoskinson/window-integration-qa')/('elm-parent-input-'+str(time.time_ns()))
BUILD_PATH = sorted((INPUT/'qa').glob('build-*/report.json'))[-1]
BUILD = json.loads(BUILD_PATH.read_text())
MODULE = BUILD_PATH.parent/'parent-input.so'
CLIENT = BUILD_PATH.parent/'parent-input-client'
LUA = b'hl.config({xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'
report = {'passed':False, 'mainDesktopActions':False,
          'scope':'Original V26 actual stationary press/release and cursor campaign on corrected V49 core/plugin/V30 AQ with event-loop monitor reload; no intervening pointer motion after geometry change',
          'checks':[], 'buildReport':str(BUILD_PATH), 'buildSHA256':reviewed.digest(BUILD_PATH),
          'output':str(OUTPUT)}
s = None
fixture = None

def check(name, accepted, **evidence):
    report['checks'].append({'name':name, 'passed':bool(accepted), **evidence})
    if not accepted:
        raise AssertionError(name)

def wait(function, seconds=6):
    deadline = time.monotonic()+seconds
    while time.monotonic()<deadline:
        s.guard()
        result = function()
        if result:
            return result
        time.sleep(.04)
    raise TimeoutError('Unchanged six-second observation deadline')

class ProbeWestonHost(reviewed.ReviewedWestonHost):
    def launch(self, name, command, env=None):
        if name == 'hyprland':
            env = dict(env, WAYLAND_DEBUG='client')
        if name == 'weston':
            check('captureOnlyExactPrivateParent', command[0] == reviewed.original.PREFIX/'usr/bin/weston'
                  and '--backend=headless' in command and '--fake-seat' in command
                  and '--debug' not in command)
            command = [*command, '--debug']
        return super().launch(name, command, env)

class ProbeSession(reviewed.PrivateHyprSession):
    def __init__(self, output, main_env, width, height, nested_lua, mesa_vendor=True):
        super().__init__(output, main_env, width, height, nested_lua, mesa_vendor=mesa_vendor)
        self.host = ProbeWestonHost(output, main_env, width, height, mesa_vendor=mesa_vendor)
        self.evidence = self.host.evidence

try:
    check('reviewedProbeBuild', BUILD['passed'])
    for path, digest in BUILD['inputs'].items():
        check('frozenBuildInput:'+Path(path).name, reviewed.digest(path)==digest)
    for name, digest in BUILD['binaries'].items():
        check('frozenBinary:'+name, reviewed.digest(BUILD_PATH.parent/name)==digest)
    reviewed.base.verify_inputs()
    reviewed.base.aq_tuple()
    source_inputs = {str(p):reviewed.digest(p) for p in [ROOT/'qa/native.py', ROOT/'fixture.py', BASE/'candidate_host.py', BASE/'base_host.py', BASE/'aq-tuple.json', BASE/'native-build-report.json', ROOT/'pixels.py', INPUT/'qa/fixture-inspection.py']}
    report['sourceInputs'] = source_inputs
    shutil.copy2(__file__, OUT/'native.py')
    shutil.copy2(ROOT/'fixture.py', OUT/'fixture-source.py')
    with ProbeSession(OUTPUT, dict(os.environ), 800, 600, LUA) as s:
        try:
            parent = next(row for proc,row in s.host.processes if row['name']=='weston')
            maps = s.evidence['westonMaps']['files']
            check('exactParentInputModuleMapped', maps.get(str(MODULE.resolve()))==BUILD['binaries']['parent-input.so'],
                  parent=parent, module=str(MODULE))
            env = dict(s.env, GTK_A11Y='none', NO_AT_BRIDGE='1', GSETTINGS_BACKEND='memory', GTK_USE_PORTAL='0', WAYLAND_DEBUG='client')
            control = OUTPUT/'fixture-control.json'
            events = OUTPUT/'fixture-events.jsonl'
            fixture = s.host.launch('fixture', ['/usr/bin/python3','-B',str(ROOT/'fixture.py'),str(control),str(events)],env=env)

            def observed():
                return inspection.inspect(events, s.data('clients'))

            first = wait(observed)
            check('exactFixtureNativeIdentity',first['pid']==fixture.pid and first['title']==inspection.TITLE,
                  address=first['address'])
            report['devicesBeforeInput'] = s.data('devices')
            report['cursorBeforeInput'] = s.data('cursorpos')
            parent_env = dict(s.host.env, ELM_PARENT_INPUT_QA='1')
            check('parentClientRouting',parent_env['WAYLAND_DISPLAY']=='weston-host'
                  and parent_env['XDG_RUNTIME_DIR']==str(s.host.runtime))
            def cursor_control(kind):
                before = inspection.receipts(events)[-1]['sequence']
                temp = control.with_suffix('.tmp')
                temp.write_text(json.dumps({'op':'cursor','cursor':kind,'requestId':kind}))
                temp.replace(control)
                wait(lambda:any(row['sequence']>before and row['kind']=='cursor-set'
                     and row['cursorKind']==kind for row in inspection.receipts(events)))
                time.sleep(.15)

            def parent_capture(label):
                folder = OUTPUT/('capture-'+label)
                folder.mkdir(mode=0o700)
                env = dict(parent_env, XDG_PICTURES_DIR=str(folder))
                tool = reviewed.original.PREFIX/'usr/bin/weston-screenshooter'
                result = subprocess.run([str(tool)], env=env, capture_output=True, text=True, timeout=5)
                check(label+':parentCaptureExit', result.returncode==0,
                      exitCode=result.returncode, stdout=result.stdout, stderr=result.stderr,
                      toolSHA256=reviewed.digest(tool))
                images = list(folder.glob('*.png'))
                check(label+':oneParentFrame', len(images)==1)
                return images[0]

            def assert_cursor(label, coords, mode, scale):
                frame = parent_capture(label+'-custom')
                image = pixels(frame)
                factor = [800/(mode[0]/scale),600/(mode[1]/scale)]
                expected = [coords[0]-7*factor[0], coords[1]-5*factor[1],
                            coords[0]+17*factor[0], coords[1]+15*factor[1]]
                check(label+':actualParentCursorPixels', image['dimensions']==[800,600] and len(image['components'])==1
                      and image['magenta']>100 and image['cyan']>4,
                      image=image, expectedBounds=expected, parentPoint=coords, factor=factor)
                check(label+':parentCursorHotspot', all(abs(a-b)<=2 for a,b in zip(image['bounds'],expected)),
                      image=image,expectedBounds=expected,parentPoint=coords,factor=factor)
            last_parent_point = []

            def inject(label, mode, scale):
                monitor = wait(lambda:next((m for m in s.data('monitors') if m['name']=='WAYLAND-1'
                                      and m['width']==mode[0] and m['height']==mode[1]
                                      and m['scale']==scale and m['transform']==0),None))
                target = wait(observed)
                # The child reports its mode before the parent has necessarily
                # delivered the matching frame callback and input mapping.
                time.sleep(.25)
                target = wait(observed)
                if last_parent_point:
                    assert_cursor(label+'-stationary-after-mode', last_parent_point, mode, scale)
                    # A resize or scale change must not require device motion
                    # before a press targets the cursor's visible parent point.
                    before_stationary = wait(observed)
                    expected_stationary = [last_parent_point[0]*(mode[0]/scale)/800-target['at'][0],
                                           last_parent_point[1]*(mode[1]/scale)/600-target['at'][1]]
                    check(label+':stationaryPointInsideObservedRecipient',
                          all(0<value<limit for value,limit in zip(expected_stationary,target['size'])),
                          expected=expected_stationary,parentPoint=last_parent_point,target=target)
                    result = subprocess.run([str(CLIENT)], input='press 272\nrelease 272\nquit\n',
                                            text=True,capture_output=True,env=parent_env,timeout=5)
                    ack = [json.loads(line) for line in result.stdout.splitlines()]
                    check(label+':stationaryButtonParentExit', result.returncode==0 and len(ack)==3
                          and ack[0].get('ready') is True and all(row.get('accepted') is True for row in ack[1:]),
                          exitCode=result.returncode,ack=ack,stderr=result.stderr)
                    stationary = wait(lambda:observed() if observed()
                       and inspection.delivered_since(observed(),before_stationary['sequence'],'button-press',expected_stationary,button=1)
                       and inspection.delivered_since(observed(),before_stationary['sequence'],'button-release',expected_stationary,button=1) else None)
                    check(label+':stationaryPressReleaseAtVisibleCursor',
                          stationary['address']==first['address'] and stationary['pid']==fixture.pid,
                          expected=expected_stationary,parentPoint=last_parent_point,receipt=stationary)

                point = [target['size'][0]/3,target['size'][1]/3]
                parent_point = inspection.parent_point(target,point,monitor,[800,600])
                coords = [round(value) for value in parent_point]
                check(label+':boundedParentPoint', all(0<value<limit for value,limit in zip(coords,[800,600])),
                      parentPoint=parent_point, widgetPoint=point, monitor=monitor, target=target)
                command = 'motion '+str(coords[0])+' '+str(coords[1])+'\npress 272\nrelease 272\nquit\n'
                result = subprocess.run([str(CLIENT)], input=command, text=True, capture_output=True,
                                        env=parent_env, timeout=5)
                acknowledgments = [json.loads(line) for line in result.stdout.splitlines()]
                check(label+':parentInjectionNormalExit',result.returncode==0 and len(acknowledgments)==4
                      and acknowledgments[0].get('ready') is True
                      and all(row.get('accepted') is True for row in acknowledgments[1:]),
                      command=command, acknowledgments=acknowledgments, stderr=result.stderr,
                      exitCode=result.returncode)
                report[label+'CursorAfterInput'] = s.data('cursorpos')
                receipt = wait(lambda:observed() if observed() and inspection.delivered_since(
                    observed(),target['sequence'],'button-press',point,button=1)
                    and inspection.delivered_since(observed(),target['sequence'],'button-release',point,button=1) else None)
                press = inspection.delivered_since(receipt,target['sequence'],'button-press',point,button=1)
                release = inspection.delivered_since(receipt,target['sequence'],'button-release',point,button=1)
                check(label+':exactGtkRecipient',bool(press and release)
                      and press[0]['sequence']<release[-1]['sequence']
                      and press[0]['eventWindowReference']==release[-1]['eventWindowReference']
                      and receipt['pid']==target['pid'] and receipt['address']==target['address'],
                      point=point, parentPoint=parent_point, press=press, release=release,
                      monitor=monitor, nativeWindow={'at':target['at'],'size':target['size'],'address':target['address']})

                assert_cursor(label+'-existing-after-input', coords, mode, scale)
                cursor_control('custom')
                time.sleep(.2)
                assert_cursor(label+'-replacement', coords, mode, scale)
                cursor_control('blank')
                hidden = pixels(parent_capture(label+'-blank'))
                check(label+':cursorActuallyHidden', len(hidden['components'])==0,image=hidden)
                cursor_control('custom')
                before_motion = observed()
                moved = [coords[0]+43, coords[1]+31]
                result = subprocess.run([str(CLIENT)], input='motion '+str(moved[0])+' '+str(moved[1])+'\nquit\n',
                                        text=True, capture_output=True, env=parent_env, timeout=5)
                ack = [json.loads(line) for line in result.stdout.splitlines()]
                check(label+':movementNormalExit', result.returncode==0 and len(ack)==2
                      and ack[0].get('ready') is True and ack[1].get('accepted') is True,
                      exitCode=result.returncode, acknowledgment=ack, stderr=result.stderr)
                expected_widget = [moved[i]/factor for i,factor in enumerate([800/(mode[0]/scale),600/(mode[1]/scale)])]
                expected_widget = [expected_widget[i]-target['at'][i] for i in range(2)]
                wait(lambda:inspection.delivered_since(observed(),before_motion['sequence'],'motion',expected_widget))
                time.sleep(.2)
                assert_cursor(label+'-moved', moved, mode, scale)
                last_parent_point[:] = moved


            inject('original800x600',[800,600],1)
            for label,mode,scale in [('shrunk640x480',[640,480],1),
                                     ('scaled960x640',[960,640],2),
                                     ('restored800x600',[800,600],1),
                                     ('scaleOnly800x600',[800,600],2),
                                     ('restoreScaleOnly800x600',[800,600],1)]:
                expression = ('hl.monitor({output="WAYLAND-1",mode="'+str(mode[0])+'x'+str(mode[1])
                              +'@60",position="0x0",scale='+str(scale)+',transform=0})')
                answer = s.ctl('eval',expression).strip()
                check(label+':modeRequested',answer=='ok',response=answer)
                inject(label,mode,scale)
            temp = control.with_suffix('.tmp')
            temp.write_text(json.dumps({'op':'quit','requestId':'parent-input-native'}))
            temp.replace(control)
            fixture.wait(timeout=5)
            check('fixtureNormalExit',fixture.returncode==0)
            records = inspection.receipts(events)
            check('fixtureEmittedNormalExit',bool(records) and records[-1]['kind']=='normal-exit',
                  finalRecord=records[-1] if records else None)
            for path,digest in BUILD['inputs'].items():
                check('unchangedBuildInput:'+Path(path).name,reviewed.digest(path)==digest)
            for path,digest in source_inputs.items():
                check('unchangedSource:'+Path(path).name,reviewed.digest(path)==digest)
            report['passed'] = True
        finally:
            if fixture and fixture.poll() is None:
                temp=control.with_suffix('.tmp')
                temp.write_text(json.dumps({'op':'quit','requestId':'parent-input-cleanup'}))
                temp.replace(control)
                try:
                    fixture.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    owned=next(row for proc,row in s.host.processes if proc is fixture)
                    s.host.stop(owned,fixture)
                    fixture.wait(timeout=5)
            registered={row['pid'] for proc,row in s.host.processes}
            for descendant in reversed([row for row in s.host.descendants() if row['pid'] not in registered]):
                s.host.stop(descendant)
except Exception as error:
    report.update(passed=False,error=repr(error),traceback=traceback.format_exc())
report['privateHost'] = s.evidence if s else None
report['cleanupPassed'] = bool(s and not s.evidence.get('cleanupErrors')
    and not s.evidence.get('unexpectedInnerDescendants') and not s.evidence.get('remainingDescendants')
    and s.evidence.get('runtimeGone'))
report['passed'] = report['passed'] and report['cleanupPassed']
if OUTPUT.exists():
    shutil.copytree(OUTPUT,OUT/'native-evidence',symlinks=True)
report['artifacts']={str(path.relative_to(OUT)):hashlib.sha256(path.read_bytes()).hexdigest()
                     for path in OUT.rglob('*') if path.is_file() and not path.is_symlink()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}))
raise SystemExit(not report['passed'])
