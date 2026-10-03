#!/usr/bin/env python3
"""Explicit private headless composite GPU raster test; no main GUI writes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import threading
import time

from compare_scene import verify_scene
from raster_oracle import compare, encode_png, png_rgba, render

BASE = Path(__file__).resolve().parent
PACKET = Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/producer-checkpoint-v1.json')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def wait(fn, label, timeout=15):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        value = fn()
        if value:
            return value
        time.sleep(0.03)
    raise AssertionError(label)


class Observer:
    def __init__(self, command, env, output):
        self.rows, self.lock = [], threading.Lock()
        self.error_log = (output / 'producer.stderr').open('w')
        self.process = subprocess.Popen(command, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=self.error_log, text=True, bufsize=1, start_new_session=True)
        self.log = (output / 'producer-events.jsonl').open('w')
        self.thread = threading.Thread(target=self.read, daemon=True)
        self.thread.start()

    def read(self):
        for line in self.process.stdout:
            self.log.write(line)
            self.log.flush()
            row = json.loads(line)
            with self.lock:
                self.rows.append(row)

    def send(self, **row):
        self.process.stdin.write(json.dumps(row, allow_nan=False) + '\n')
        self.process.stdin.flush()

    def find(self, predicate, label):
        def observed():
            with self.lock:
                fatal = next((r for r in self.rows if r.get('event') in ('fatal', 'rejected')), None)
                if fatal:
                    raise AssertionError(f'{label}: {fatal}')
                found = next((r for r in reversed(self.rows) if predicate(r)), None)
            if found:
                return found
            if self.process.poll() is not None:
                raise AssertionError(f'{label}: producer exited {self.process.returncode}')
            return None
        return wait(observed, label)

    def close(self):
        if self.process.poll() is None:
            self.send(command='stop')
            self.process.wait(timeout=5)
        self.thread.join(timeout=2)
        self.process.stdin.close()
        self.process.stdout.close()
        self.log.close()
        self.error_log.close()
        return self.process.returncode


def generated_source(path, width, height, member):
    # Deliberately asymmetric, non-square stripes and three distinct member
    # palettes expose flips, wrong order, dropped child and shifted boundaries.
    colors = ((224, 24, 48), (16, 216, 64), (32, 72, 224))
    rgba = bytearray()
    for y in range(height):
        for x in range(width):
            rgb = colors[member]
            if y < 8:
                rgb = (240, 192 - member * 32, 16 + member * 32)
            elif x < 4 or y >= height - 4 or x >= width - 4:
                rgb = (16, 16, 16)
            elif (x // 8 + y // 8) % 3 == 0:
                rgb = (rgb[0] // 2, rgb[1] // 2, rgb[2] // 2)
            rgba.extend((*rgb, 255))
    path.write_bytes(encode_png(width, height, bytes(rgba)))
    path.chmod(0o600)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((BASE / 'headless-frozen-inputs.json').read_text())
    for path, expected in manifest['inputs'].items():
        assert digest(path) == expected, f'frozen input changed: {path}'
    packet = json.loads(PACKET.read_text())
    for path, expected in packet['inputs'].items():
        assert digest(path) == expected, f'producer source changed: {path}'
    if not args.execute:
        print(json.dumps({'preflight': 'pass', 'inputs': len(manifest['inputs']), 'producerInputs': len(packet['inputs'])}))
        return 0
    os.umask(0o077)
    output = args.output.resolve()
    assert output.parent == BASE and output.name.startswith('attempt-headless-')
    output.mkdir(mode=0o700)
    report = {'scope': 'private headless EGL composite raster, generated immutable source vector; no cadence, physical output or native-window transaction claim',
              'checks': [], 'mainGUIWrites': False, 'mainRestorationWrites': False, 'result': 'pending',
              'producerPacketSHA256': digest(PACKET)}
    compositor = observer = None
    runtime = None
    before_main = json.loads(subprocess.check_output(['hyprctl', '-j', 'clients'], text=True, timeout=4))
    report['mainClientsBefore'] = before_main
    def check(name, passed, **details):
        report['checks'].append({'name': name, 'passed': bool(passed), **details})
        assert passed, name
    with tempfile.TemporaryDirectory(prefix='frh-', dir='/tmp') as temporary:
        runtime = Path(temporary)
        runtime.chmod(0o700)
        config = runtime / 'private-headless.lua'
        config.write_bytes((BASE / 'private-headless.lua').read_bytes())
        env = dict(os.environ, XDG_RUNTIME_DIR=str(runtime), HOME=str(runtime / 'home'),
                   XDG_CONFIG_HOME=str(runtime / 'config'), XDG_CACHE_HOME=str(runtime / 'cache'),
                   XDG_DATA_HOME=str(runtime / 'data'), AQ_BACKENDS='headless', AQ_DRM_DEVICES='/dev/dri/card0',
                   GIO_USE_VFS='local', GTK_USE_PORTAL='0')
        for key in ('WAYLAND_DISPLAY', 'WAYLAND_SOCKET', 'DISPLAY', 'DBUS_SESSION_BUS_ADDRESS',
                    'AT_SPI_BUS_ADDRESS', 'HYPRLAND_INSTANCE_SIGNATURE', 'SESSION_MANAGER'):
            env.pop(key, None)
        for directory in ('home', 'config', 'cache', 'data'):
            (runtime / directory).mkdir()
        try:
            with (output / 'compositor.log').open('w') as log:
                compositor = subprocess.Popen(['dbus-run-session', '--', 'Hyprland', '--config', str(config)],
                                              env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            def instance():
                assert compositor.poll() is None, 'private compositor exited'
                try:
                    instances = json.loads(subprocess.check_output(['hyprctl', 'instances', '-j'], env=env,
                                                                   text=True, stderr=subprocess.DEVNULL, timeout=2))
                except (subprocess.SubprocessError, ValueError):
                    return None
                for row in instances:
                    try:
                        if str(config).encode() in Path(f'/proc/{row["pid"]}/cmdline').read_bytes():
                            return row
                    except FileNotFoundError:
                        continue
                return None
            selected = wait(instance, 'private headless startup')
            report['privateCompositor'] = selected
            private = dict(env, HYPRLAND_INSTANCE_SIGNATURE=selected['instance'], WAYLAND_DISPLAY=selected['wl_socket'])
            def ctl(*arguments):
                return subprocess.check_output(['hyprctl', *map(str, arguments)], env=private, text=True, timeout=4).strip()
            check('headless config has no errors', not ctl('configerrors'))
            monitors = json.loads(ctl('-j', 'monitors'))
            if not monitors:
                ctl('output', 'create', 'headless', 'HEADLESS-1')
                monitors = wait(lambda: json.loads(ctl('-j', 'monitors')), 'first private headless output')
            check('only private headless output exists', len(monitors) == 1 and monitors[0]['name'] == 'HEADLESS-1', monitors=monitors)
            for name, wanted in (('misc:disable_hyprland_logo', True), ('misc:disable_splash_rendering', True)):
                actual = json.loads(ctl('getoption', name, '-j'))
                check(name + ' set in private compositor', actual.get('bool') is wanted and actual.get('set') is True, observed=actual)
            observer = Observer(packet['rasterLaunch'], private, output)
            observed = observer.find(lambda r: r.get('event') == 'outputs', 'actual hardware and private output readiness')['outputs']
            check('producer hardware/material accepted before readiness', any(r.get('event') == 'backendObserved' and r.get('mappedMaterialMatches') is True for r in observer.rows), backend=[r for r in observer.rows if r.get('event') == 'backendObserved'])
            check('producer has exact private output', len(observed) == 1 and observed[0]['name'] == 'HEADLESS-1', outputs=observed)
            sources = []
            for i, (width, height, x, y) in enumerate(((96, 80, 24, 32), (72, 48, 56, 56), (48, 32, 80, 68))):
                path = runtime / f'member-{i}.png'
                generated_source(path, width, height, i)
                sources.append({'stableId': f'abc{i + 1}', 'pid': os.getpid() + i, 'path': str(path), 'digest': digest(path),
                                'nativeRect': {'x': x, 'y': y, 'width': width, 'height': height},
                                'atlasRect': {'x': x, 'y': y, 'width': width, 'height': height},
                                'iconRect': {'x': 240 + i * 8, 'y': 196, 'width': 24, 'height': 20},
                                'insets': {'left': 0, 'top': 0, 'right': 0, 'bottom': 0},
                                'pixels': [width, height], 'captureScale': 1})
                (output / f'member-{i}.png').write_bytes(path.read_bytes())
            token = 'abcdef123456-1'
            identities = [{k: s[k] for k in ('stableId', 'pid')} for s in sources]
            observer.send(command='seed', token=token, operation='minimize', durationMs=1000, members=sources,
                          outputs=[{k: o[k] for k in ('name', 'generation')} for o in observed])
            observer.find(lambda r: r.get('event') == 'seeded' and r.get('token') == token, 'complete source seed')
            for index, progress in enumerate((0.0, 0.35)):
                observer.send(command='sample', token=token, identities=identities, progress=progress)
                frame = observer.find(lambda r: r.get('event') == 'presented' and r.get('accepted') is True and r.get('token') == token and r.get('progress') == progress, 'actual full held scene presentation')
                observer.send(command='state', observationId=f'held-{index}')
                state = observer.find(lambda r: r.get('event') == 'state' and r.get('observationId') == f'held-{index}', 'held scene state')
                check(f'held scene {index} has no native authority', state['nativeReady'] is False and state['nativeEndpoint'] is False and not any(r.get('event') in ('ready', 'endpoint') for r in observer.rows))
                o = state['outputs'][0]
                check(f'held scene {index} exact immutable buffer extent', frame['bufferWidth'] == o['bufferWidth'] and frame['bufferHeight'] == o['bufferHeight'])
                image = output / f'actual-{index}.png'
                subprocess.run(['grim', '-o', o['name'], str(image)], env=private, check=True, timeout=5, capture_output=True)
                fixture = {'output': o, 'token': token, 'progress': progress, 'members': sources,
                           'diagnosticNoNativeAuthority': True, 'screenshotMapping': 'untransformed-output-buffer',
                           'allowedPresentedSequences': [str(frame['sequence'])], 'backgroundRGBA': [0, 0, 0, 255],
                           'channelTolerance': 0 if progress == 0 else 1}
                # Sources remain private and immutable through decode/comparison.
                out, decoded = verify_scene(fixture, frame)
                expected = render(out, decoded)
                width, height = out['bufferWidth'], out['bufferHeight']
                actual = png_rgba(image, digest(image), (width, height))
                comparison = compare(actual, expected, width, height, fixture['channelTolerance'])
                (output / f'expected-{index}.png').write_bytes(encode_png(width, height, expected))
                # Retain source artifact paths that survive private runtime cleanup.
                saved_fixture = {**fixture, 'members': [{**s, 'path': str(output / f'member-{i}.png')} for i, s in enumerate(sources)]}
                (output / f'fixture-{index}.json').write_text(json.dumps(saved_fixture, indent=2) + '\n')
                (output / f'presented-{index}.json').write_text(json.dumps(frame, indent=2) + '\n')
                (output / f'comparison-{index}.json').write_text(json.dumps(comparison, indent=2) + '\n')
                check(f'held scene {index} full RGBA', comparison['passed'], comparison=comparison)
            observer.send(command='cancel', token=token, identities=identities)
            observer.find(lambda r: r.get('event') == 'cancelled' and r.get('token') == token, 'exact scene cancellation')
            check('normal producer stop', observer.close() == 0)
            report['result'] = 'pass'
        except Exception as error:
            report['result'], report['error'] = 'fail', repr(error)
        finally:
            if observer:
                try:
                    code = observer.close()
                    report['producerCleanup'] = {'pid': observer.process.pid, 'exitCode': code, 'gone': not Path(f'/proc/{observer.process.pid}').exists()}
                except Exception as error:
                    report['producerCleanupError'] = repr(error)
                    if observer.process.poll() is None:
                        observer.process.terminate()
                        try:
                            observer.process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            observer.process.kill()
                            observer.process.wait(timeout=5)
                            report['forcedProducerKill'] = True
                    report['forcedProducerTermination'] = True
            if compositor:
                child = report.get('privateCompositor')
                child_alive = bool(child and Path(f'/proc/{child["pid"]}').exists())
                if compositor.poll() is None or child_alive:
                    if child_alive:
                        assert str(config).encode() in Path(f'/proc/{child["pid"]}/cmdline').read_bytes(), 'private cleanup process identity drift'
                        assert os.getpgid(child['pid']) == compositor.pid, 'private cleanup group identity drift'
                    try:
                        os.killpg(compositor.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                    try:
                        compositor.wait(timeout=8)
                    except subprocess.TimeoutExpired:
                        os.killpg(compositor.pid, signal.SIGKILL)
                        compositor.wait(timeout=5)
                        report['forcedCompositorKill'] = True
                    if child:
                        wait(lambda: not Path(f'/proc/{child["pid"]}').exists(), 'private compositor child cleanup', timeout=5)
                report['compositorCleanup'] = {'launcherPID': compositor.pid, 'exitCode': compositor.poll(),
                                               'gone': not Path(f'/proc/{compositor.pid}').exists()}
                if report.get('privateCompositor'):
                    report['privateCompositorPIDGone'] = not Path(f'/proc/{report["privateCompositor"]["pid"]}').exists()
    report['privateRuntimeGone'] = not runtime.exists()
    report['mainClientsAfter'] = json.loads(subprocess.check_output(['hyprctl', '-j', 'clients'], text=True, timeout=4))
    def stable(rows):
        return sorted((r['address'], r['stableId'], r['pid']) for r in rows)
    report['originalMainIdentitiesPreserved'] = stable(before_main) == stable(report['mainClientsAfter'])
    report['frozenSourcesUnchanged'] = all(digest(p) == h for p, h in manifest['inputs'].items()) and all(digest(p) == h for p, h in packet['inputs'].items())
    if (not report['frozenSourcesUnchanged'] or not report['originalMainIdentitiesPreserved']
            or report.get('forcedProducerTermination') or report.get('producerCleanupError')
            or report.get('forcedCompositorKill') or not report['privateRuntimeGone']
            or not report.get('compositorCleanup', {}).get('gone')
            or (report.get('privateCompositor') and not report.get('privateCompositorPIDGone'))):
        report['result'] = 'fail'
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'result': report['result'], 'checks': len(report['checks']), 'error': report.get('error'),
                      'sourcesUnchanged': report['frozenSourcesUnchanged'], 'reportSHA256': digest(output / 'report.json')}))
    return int(report['result'] != 'pass')


if __name__ == '__main__':
    raise SystemExit(main())
