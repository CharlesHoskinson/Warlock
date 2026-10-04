"""Two real child outputs/GTK recipients on the reviewed private fake parent seat.

Parent acknowledgments alone never establish output or recipient ownership.
This is not a physical multi-display/hotplug or plugin integration campaign.
"""
import importlib.util, json, os, re, shutil, time, traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result
host = module('multioutput_host', ROOT / 'candidate_host.py')
host.original.qa.require_qa_scope()
inspection = module('multioutput_inspection', ROOT / 'qa/fixture-inspection.py')
interactive = module('multioutput_interactive', ROOT / 'qa/interactive-client.py')
OUT = ROOT / 'qa' / ('native-' + str(time.time_ns())); OUT.mkdir()
OUTPUT = Path('/home/hoskinson/window-integration-qa') / ('elm-parent-multioutput-' + str(time.time_ns()))
report = {'passed': False, 'mainDesktopActions': False, 'releaseAcceptance': False,
          'scope': 'Two nested child outputs on one private 800x600 fake parent output; real GTK ownership, nonzero logical origins, stationary reprojection and focused-output removal. Authority is not loaded. No physical/hardware/full-roadmap acceptance.',
          'checks': [], 'interactiveClients': [], 'fixtures': {}}
s = None; fixtures = {}; controller = None
LUA = b'hl.config({xwayland={enabled=false},animations={enabled=false}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\nhl.monitor({output="WAYLAND-2",mode="800x600@60",position="1000x100",scale=1})\n'
def check(name, value, **data):
    report['checks'].append({'name': name, 'passed': bool(value), **data}); assert value, name
def wait(function):
    deadline = time.monotonic() + 6
    while time.monotonic() < deadline:
        s.guard(); value = function()
        if value: return value
        time.sleep(.04)
    raise RuntimeError('Unchanged six-second observation deadline')
def control(label, op):
    target = OUTPUT / (label + '-control.json'); tmp = target.with_suffix('.tmp')
    tmp.write_text(json.dumps({'op': op})); tmp.replace(target)
def physical(target, sequence, kind, point=None):
    return [e for e in inspection.delivered_since(target, sequence, kind, point, button=1)
            if e.get('eventType') == (4 if kind == 'button-press' else 7)]
def observed(label):
    return inspection.inspect(OUTPUT / (label + '-events.jsonl'), s.data('clients'))
def monitor(name):
    return next((m for m in s.data('monitors') if m['name'] == name), None)
def settled(label):
    value = wait(lambda: observed(label))
    until = time.monotonic() + .25
    while time.monotonic() < until: s.guard(); time.sleep(.04)
    return wait(lambda: observed(label))
def launch(label):
    process = s.host.launch(label, ['/usr/bin/python3', '-B', str(ROOT / 'fixture.py'),
                           str(OUTPUT / (label + '-control.json')), str(OUTPUT / (label + '-events.jsonl'))],
                           env=dict(s.env, WAYLAND_DEBUG='client', GTK_A11Y='none', NO_AT_BRIDGE='1', GSETTINGS_BACKEND='memory', GTK_USE_PORTAL='0'))
    fixtures[label] = process; first = wait(lambda: observed(label))
    check(label + ':exactLaunchedRecipientPID', first['pid'] == process.pid)
    report['fixtures'][label] = {k: first[k] for k in ['pid', 'address', 'title']}
    return first
def recipient_on(label, output):
    current = settled(label); m = monitor(output)
    client = next(c for c in s.data('clients') if c['pid'] == current['pid'] and c['address'] == current['address'])
    check(label + ':actualClientOnOwningOutput', m is not None and client['monitor'] == m['id'], client=client, monitor=m)
    return current, m
def point_from_parent(target, m, parent_point):
    return [m['x'] + parent_point[0] * (m['width'] / m['scale']) / 800 - target['at'][0],
            m['y'] + parent_point[1] * (m['height'] / m['scale']) / 600 - target['at'][1]]
def click(label, output, other, parent_point=None, motion=True, case='click'):
    before, m = recipient_on(label, output); other_before = settled(other)
    if parent_point is None:
        parent_point = [round(v) for v in inspection.parent_point(before, [before['size'][0]/2, before['size'][1]/2], m, [800,600])]
    expected = point_from_parent(before, m, parent_point)
    check(case + ':interiorExpectedRecipientPoint', all(0 < v < before['size'][i] for i,v in enumerate(expected)), expected=expected, recipient=before)
    if motion: controller.send('motion %d %d' % tuple(parent_point))
    controller.send('press 272'); controller.send('release 272')
    def delivered():
        current = observed(label)
        return current if current and physical(current, before['sequence'], 'button-release', expected) else None
    try:
        after = wait(delivered)
    except RuntimeError:
        prior = observed(label)
        report['failedStationaryDelivery'] = {'case':case, 'cursor':s.data('cursorpos'),
            'expected':expected, 'observedCounts':prior['counts'], 'newPhysicalEvents':physical(prior,before['sequence'],'button-press')+physical(prior,before['sequence'],'button-release')}
        # Diagnose after the original deadline; this deliberately added motion
        # never qualifies the failed stationary-input oracle.
        controller.send('motion %d %d' % (parent_point[0]+1,parent_point[1]+1))
        diag_expected = point_from_parent(prior,m,[parent_point[0]+1,parent_point[1]+1])
        controller.send('press 272'); controller.send('release 272')
        def diagnostic_received():
            value = observed(label)
            return value if value and physical(value,prior['sequence'],'button-release',diag_expected) else None
        value = wait(diagnostic_received)
        report['afterRealMotionDiagnostic'] = {'recipient':label, 'expected':diag_expected,
            'press':physical(value,prior['sequence'],'button-press',diag_expected),
            'release':physical(value,prior['sequence'],'button-release',diag_expected),
            'cursor':s.data('cursorpos')}
        raise RuntimeError('Original stationary delivery failed; actual new physical motion restores recipient delivery')
    other_after = settled(other)
    presses = physical(after, before['sequence'], 'button-press', expected)
    releases = physical(after, before['sequence'], 'button-release', expected)
    check(case + ':exactPhysicalGTKPair', len(presses) == len(releases) == 1 and
          after['counts']['button-press'] == before['counts']['button-press'] + 1 and
          after['counts']['button-release'] == before['counts']['button-release'] + 1,
          press=presses, release=releases, parentPoint=parent_point, expected=expected, monitor=m)
    check(case + ':otherRecipientGetsNoButtons', other_after['counts']['button-press'] == other_before['counts']['button-press'] and
          other_after['counts']['button-release'] == other_before['counts']['button-release'],
          before=other_before['counts'], after=other_after['counts'])
    expected_global = [m['x'] + parent_point[0]*(m['width']/m['scale'])/800,
                       m['y'] + parent_point[1]*(m['height']/m['scale'])/600]
    cursor = s.data('cursorpos')
    check(case + ':actualCursorIncludesOwningOutputOrigin', all(abs(cursor[k] - expected_global[i]) <= 2 for i,k in enumerate(['x','y'])), cursor=cursor, expected=expected_global)
    return parent_point
def mode(output, width, height, scale, x, y, label):
    receipt = s.ctl('eval', f'hl.monitor({{output="{output}",mode="{width}x{height}@60",position="{x}x{y}",scale={scale},transform=0}})').strip()
    check(label + ':monitorRequestAdmitted', receipt == 'ok', receipt=receipt)
    return wait(lambda: next((m for m in s.data('monitors') if m['name'] == output and m['width'] == width and
                             m['height'] == height and m['scale'] == scale and m['x'] == x and m['y'] == y), None))
try:
    desc = json.loads((ROOT/'parent-probe-build.json').read_text()); build_path = Path(desc['buildReport'])
    assert host.digest(build_path) == desc['buildReportSHA256']
    build = json.loads(build_path.read_text()); assert build['passed']
    for rel, sha in build['inputs'].items(): assert host.digest(ROOT/rel) == sha, rel
    for key in ['client', 'module']: assert host.digest(build[key]) == build[key+'SHA256']
    paths = [p for p in ROOT.rglob('*') if p.is_file() and not p.is_relative_to(ROOT/'qa')]
    paths += [Path(__file__), ROOT/'qa/fixture-inspection.py', ROOT/'qa/interactive-client.py']
    report['inputs'] = {str(p): host.digest(p) for p in paths}
    report.update(buildReport=str(build_path), buildReportSHA256=host.digest(build_path))
    shutil.copy2(__file__, OUT/'native.py')
    with host.PrivateHyprSession(OUTPUT, dict(os.environ), 800, 600, LUA, mesa_vendor=True) as s:
        try:
            core = json.loads((ROOT/'native-build-report.json').read_text())
            check('exactReviewedCoreMapped', s.evidence['hyprlandMaps']['files'].get(str(Path(core['binary']).resolve())) == core['sha256'])
            check('exactSafeParentModuleMapped', s.evidence['westonMaps']['files'].get(str(Path(build['module']).resolve())) == build['moduleSHA256'])
            first = launch('recipient-one')
            controller = interactive.InteractiveClient(s.host, host.original, build_path, host.digest(build_path), guard=s.guard, name='multioutput-controller')
            report['interactiveClients'].append(controller.evidence)
            controller.send('motion 400 300')
            receipt = s.ctl('output', 'create', 'wayland', 'WAYLAND-2').strip()
            check('secondActualOutputCreateAdmitted', receipt == 'ok', receipt=receipt)
            second_monitor = wait(lambda: monitor('WAYLAND-2'))
            check('twoActualOutputsWithDistinctIdentities', len(s.data('monitors')) == 2 and second_monitor['id'] != monitor('WAYLAND-1')['id'], monitors=s.data('monitors'))
            mode('WAYLAND-2', 800, 600, 1, 1000, 100, 'secondOutputInitial')
            # Require actual parent wl_pointer.enter for the newly mapped surface.
            wire = OUTPUT/'hyprland.log'
            wait(lambda: 'set_title("aquamarine - WAYLAND-2")' in wire.read_text(errors='replace'))
            controller.send('motion 401 301')
            wait(lambda: s.data('cursorpos')['x'] >= 1000 and s.data('cursorpos')['y'] >= 100)
            launch('recipient-two'); recipient_on('recipient-one', 'WAYLAND-1'); recipient_on('recipient-two', 'WAYLAND-2')
            anchor = click('recipient-two', 'WAYLAND-2', 'recipient-one', case='secondOutputNonzeroOrigin')
            for label, width, height, scale, x, y in [
                    ('secondScale',800,600,2,1000,100), ('secondModeAndOrigin',960,640,2,1200,200),
                    ('secondRestore',800,600,1,1000,100)]:
                mode('WAYLAND-2',width,height,scale,x,y,label)
                click('recipient-two','WAYLAND-2','recipient-one',anchor,motion=False,case=label+':stationary')
            # Mutating the background output must not steal the focused output's anchor.
            mode('WAYLAND-1',640,480,1,-800,0,'backgroundOutputMove')
            click('recipient-two','WAYLAND-2','recipient-one',anchor,motion=False,case='backgroundChangeIsolation')
            mode('WAYLAND-1',800,600,1,0,0,'backgroundOutputRestore')
            before_destroy = wire.read_text(errors='replace')
            receipt = s.ctl('output','destroy','WAYLAND-2').strip()
            check('focusedOutputDestroyAdmitted', receipt == 'ok', receipt=receipt)
            wait(lambda: len(s.data('monitors')) == 1 and monitor('WAYLAND-2') is None)
            check('bothRecipientsSurviveFocusedOutputRemoval', all(p.poll() is None for p in fixtures.values()), clients=s.data('clients'))
            wait(lambda: bool(re.search(r'wl_pointer[#@][0-9]+\.enter\(', wire.read_text(errors='replace')[len(before_destroy):])))
            receipt = s.ctl('eval', f'hl.dispatch(hl.dsp.focus({{window="address:{first["address"]}"}}))').strip()
            check('survivingFirstRecipientFocusAdmitted',receipt=='ok',receipt=receipt)
            wait(lambda: s.data('activewindow').get('address') == first['address'])
            click('recipient-one','WAYLAND-1','recipient-two',case='survivingOutputAfterRetirement')
            check('actualDeviceStillExactlyOne',len(s.data('devices')['mice'])==1)
            controller.quit(); check('parentControllerNormalExit',controller.process.returncode==0); controller=None
            for label, process in fixtures.items():
                control(label,'quit'); process.wait(timeout=5); check(label+':normalExit',process.returncode==0)
            wait(lambda: s.data('clients') == [])
            for path, sha in report['inputs'].items(): assert host.digest(path) == sha, path
            report['passed'] = True
        finally:
            report['terminalNativeState'] = {name:s.data(name) for name in ['monitors','clients','devices','cursorpos']}
            if controller is not None: controller.quit()
            for label, process in fixtures.items():
                if process.poll() is None: control(label,'quit'); process.wait(timeout=5)
            registered = {row['pid'] for proc,row in s.host.processes}
            for child in reversed([row for row in s.host.descendants() if row['pid'] not in registered]): s.host.stop(child)
except Exception as error:
    report['error'] = repr(error); report['traceback'] = traceback.format_exc()
finally:
    if OUTPUT.exists(): shutil.copytree(OUTPUT, OUT/'native-evidence', dirs_exist_ok=True)
    report['privateHost'] = s.evidence if s is not None else None
    report['cleanupPassed'] = bool(s is not None and not s.evidence.get('cleanupErrors') and
                                   not s.evidence.get('unexpectedInnerDescendants') and not s.evidence.get('remainingDescendants') and s.evidence.get('runtimeGone'))
    report['passed'] = report['passed'] and report['cleanupPassed']
    report['artifacts'] = {str(p.relative_to(OUT)):host.digest(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}),flush=True)
raise SystemExit(not report['passed'])
