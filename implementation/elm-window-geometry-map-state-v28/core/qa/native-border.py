"""Reviewed real xdg maximize/restore roundtrip, private host only.

No menu transport/authority claim. Request barriers, configure/ACK/buffer records,
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


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('geometry_private_host', ROOT / 'candidate_host.py')
host = importlib.util.module_from_spec(spec)
spec.loader.exec_module(host)
host.original.qa.require_qa_scope()
OUT = ROOT / 'qa' / ('native-' + str(time.time_ns()))
OUT.mkdir()
OUTPUT = Path('/home/hoskinson/window-integration-qa') / ('elm-xdg-maximize-' + str(time.time_ns()))
LUA = b'hl.config({xwayland={enabled=false},animations={enabled=false},general={border_size=1}})\nhl.monitor({output="WAYLAND-1",mode="800x600@60",position="0x0",scale=1})\n'
report = {'passed': False, 'mainDesktopActions': False, 'menuTransportIntegrated': False,
          'scope': 'Real xdg maximize, duplicate maximize, restore, duplicate restore with exact ordinary placement and independent interior pixels', 'checks': []}
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
    report['latestNativeObservation'] = {'observedMonotonicNs': time.monotonic_ns(), 'window': row}
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


try:
    core = json.loads((ROOT / 'native-build-report.json').read_text())
    fixture = json.loads((ROOT / 'client-build-report.json').read_text())
    assert core['result'] == fixture['result'] == 'pass'
    assert host.digest(core['binary']) == core['sha256'] and host.digest(core['buildReport']) == core['buildReportSHA256']
    assert host.digest(core['closureReport']) == core['closureReportSHA256'] and json.loads(Path(core['closureReport']).read_text())['passed']
    assert host.digest(fixture['client']) == fixture['clientSHA256'] and host.digest(fixture['buildReport']) == fixture['buildReportSHA256']
    build = json.loads(Path(fixture['buildReport']).read_text())
    assert build['passed']
    for path, digest in build['inputs'].items():
        assert host.digest(path) == digest, path
    for section in ['dependencies', 'tools', 'linkedLibraries']:
        for path, digest in build[section].items():
            assert host.digest(path) == digest, path
    for rel, digest in build['artifacts'].items():
        assert host.digest(Path(fixture['buildReport']).parent / rel) == digest, rel
    source_inputs = [Path(__file__), ROOT / 'candidate_host.py', ROOT / 'native-build-report.json', ROOT / 'client-build-report.json', ROOT / 'link-build-report.json', ROOT / 'aq-tuple.json', ROOT / 'qa/xdg-max-client.c', Path('/usr/bin/grim'), Path('/usr/bin/magick')]
    report['inputs'] = {str(path): host.digest(path) for path in source_inputs}
    report['clientBuild'] = fixture
    report['coreBuild'] = core
    shutil.copy2(__file__, OUT / 'native.py')
    with host.PrivateHyprSession(OUTPUT, dict(os.environ), 800, 600, LUA, mesa_vendor=True) as session:
        try:
            check('exactReviewedCoreMapped', session.evidence['hyprlandMaps']['files'].get(str(Path(core['binary']).resolve())) == core['sha256'])
            check('exactReviewedPrivateAquamarineMapped', session.evidence['privateAquamarine']['mappedVerified'] is True)
            client_log = OUTPUT / 'xdg-max-client.log'
            fd = os.open(client_log, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            output_stream = os.fdopen(fd, 'wb')
            session.host.logs.append(output_stream)
            client = subprocess.Popen([fixture['client']], stdin=subprocess.PIPE, stdout=output_stream, stderr=subprocess.STDOUT,
                                      env=dict(session.env, WAYLAND_DEBUG='1'), cwd=session.host.runtime, start_new_session=True)
            client_identity = host.original.process(client.pid)
            client_identity.update(name='xdg-max-client', command=[fixture['client']], log=str(client_log))
            session.host.processes.append((client, client_identity))
            session.host.evidence['xdgMaxClient'] = client_identity
            wait(lambda: any(row['event'] == 'ready' for row in events()))
            native = wait(native_window)
            check('exactPersistentOrdinaryFixtureIdentity', native['pid'] == client.pid and native['class'] == 'elm-maximize-probe' and native['xwayland'] is False, native=native)
            report['fixtureIdentity'] = {'pid': client.pid, 'address': native['address'], 'title': native['title']}
            address = native['address']
            border_option = session.data('getoption', 'general:border_size')
            check('exactNativeBorderPolicy', border_option.get('int') == 1, option=border_option)
            selector = json.dumps('address:' + address)
            for operation, fields in [('float', 'action="enable"'), ('resize', 'x=320,y=180,relative=false'), ('move', 'x=83,y=61,relative=false')]:
                expression = 'hl.dsp.window.' + operation + '({' + fields + ',window=' + selector + '})'
                code = 'local r=hl.dispatch(' + expression + '); if type(r)~="table" or r.ok~=true then error("placement dispatch refused") end'
                receipt = session.ctl('eval', code).strip()
                check('ordinaryPlacementDispatch:' + operation, receipt == 'ok', expression=expression, receipt=receipt)
            initial = wait(lambda: settled(0) if native_window() and native_window()['at'] == [83, 61] and native_window()['size'] == [320, 180] and native_window()['floating'] else None)
            request('sync')
            native, buffer = wait(lambda: settled(0))
            check('actualOrdinaryPlacementReadback', native['at'] == [83, 61] and native['size'] == [320, 180] and native['floating'] is True, native=native)
            validate_pixels('ordinary', native, buffer)
            maximized = None
            for name, command, mode, changed in [('maximize', 'maximize', 1, True),
                                                   ('duplicate-maximize', 'maximize', 1, False),
                                                   ('restore', 'unmaximize', 0, True),
                                                   ('duplicate-restore', 'unmaximize', 0, False)]:
                operation_deadline = time.monotonic() + 6
                packet = request(command, deadline=operation_deadline)
                native, buffer = wait(lambda: settled(mode, packet['sequence'] if changed else None), deadline=operation_deadline)
                if mode == 1:
                    check(name + ':actualMaximizedNativeAndClientModes', native['fullscreen'] == 1 and native['fullscreenClient'] == 1 and
                          native['at'] == [1, 1] and native['size'] == [798, 598], native=native, buffer=buffer)
                    if maximized is None:
                        maximized = {'at': native['at'], 'size': native['size']}
                    else:
                        check(name + ':duplicatePreservesMaximizedGeometry', native['at'] == maximized['at'] and native['size'] == maximized['size'])
                else:
                    check(name + ':exactNativeOrdinaryRestoration', native['at'] == [83, 61] and native['size'] == [320, 180] and
                          native['fullscreen'] == 0 and native['fullscreenClient'] == 0 and native['floating'] is True, native=native, buffer=buffer)
                validate_pixels(name, native, buffer, deadline=operation_deadline)
            client.stdin.write(b'quit\n')
            client.stdin.flush()
            client.stdin.close()
            client.wait(timeout=5)
            check('xdgClientNormalExit', client.returncode == 0 and any(row['event'] == 'normalexit' for row in events()))
            wait(lambda: not any(row.get('address') == address for row in session.data('clients')))
            check('actualNativeWindowRetiredBeforeHostStop', not any(row.get('address') == address for row in session.data('clients')))
            for path, digest in report['inputs'].items():
                assert host.digest(path) == digest, path
            report['passed'] = True
        finally:
            if client is not None and client.poll() is None:
                try:
                    client.stdin.write(b'quit\n')
                    client.stdin.flush()
                    client.stdin.close()
                    client.wait(timeout=5)
                except Exception as error:
                    report['clientCleanupError'] = repr(error)
            registered = {row['pid'] for proc, row in session.host.processes}
            for descendant in reversed([row for row in session.host.descendants() if row['pid'] not in registered]):
                session.host.stop(descendant)
except Exception as error:
    report.update(passed=False, error=repr(error), traceback=traceback.format_exc())
finally:
    if OUTPUT.exists():
        shutil.copytree(OUTPUT, OUT / 'native-evidence', dirs_exist_ok=True)
    if session is not None:
        report['privateHost'] = session.evidence
        report['cleanupPassed'] = not any(session.evidence.get(key) for key in ('cleanupErrors', 'unexpectedInnerDescendants', 'remainingDescendants')) and bool(session.evidence.get('runtimeGone'))
    else:
        report['cleanupPassed'] = False
    report['passed'] = report['passed'] and report['cleanupPassed'] and not report.get('clientCleanupError')
    report['artifacts'] = {str(path.relative_to(OUT)): host.digest(path) for path in sorted(OUT.rglob('*')) if path.is_file()}
    (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'report': str(OUT / 'report.json'), 'error': report.get('error')}), flush=True)
raise SystemExit(not report['passed'])
