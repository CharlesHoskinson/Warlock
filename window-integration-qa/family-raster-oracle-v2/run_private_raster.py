#!/usr/bin/env python3
"""Whole composite GPU raster on fully private headless GL host/nested Hyprland."""
import argparse
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from compare_scene import verify_scene
from producer_observer import Observer, generated_source
import observations
from raster_oracle import compare, encode_png, png_rgba, render

BASE = Path(__file__).resolve().parent
HOST = BASE.parent / 'private-weston-aq-host-v2'
PACKET = Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/producer-checkpoint-v1.json')
FOUNDATION = BASE.parent/'private-graphics-foundation-v3/attempt-1/report.json'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((BASE / 'frozen-inputs.json').read_text())
    for path, expected in manifest['inputs'].items():
        assert digest(path) == expected, f'frozen input differs: {path}'
    packet = json.loads(PACKET.read_text())
    for path, expected in packet['inputs'].items():
        assert digest(path) == expected, f'producer input differs: {path}'
    foundation=json.loads(FOUNDATION.read_text())
    assert foundation['nativeHostAccepted'] and foundation['result']=='pass','actual private graphics foundation required'
    if not args.execute:
        print(json.dumps({'preflight': 'pass', 'inputs': len(manifest['inputs']), 'producerInputs': len(packet['inputs'])}))
        return 0
    sys.path.insert(0,str(BASE.parent))
    from qa_launch import require_qa_scope
    require_qa_scope()
    sys.path.insert(0, str(HOST))
    from weston_host import PrivateHyprSession
    assert Path(sys.modules[PrivateHyprSession.__module__].__file__).resolve() == HOST / 'weston_host.py'
    os.umask(0o077)
    output = args.output.resolve()
    assert output.parent == BASE and output.name.startswith('attempt-')
    output.mkdir(mode=0o700)
    main_env = dict(os.environ)
    preservation_before=observations.capture(output/'main-before')
    main_before = json.loads(subprocess.check_output(['hyprctl', '-j', 'clients'], env=main_env, text=True, timeout=4))
    report = {'scope': 'full RGBA independent reference for held generated composite source vector; two private outputs with scale1/1.5 and boundary clipping; no native family/window transaction or cadence/hardware-display claim',
              'checks': [], 'mainGUIWrites': False, 'mainRestorationWrites': False,
              'result': 'pending', 'mainClientsBefore': main_before, 'producerPacketSHA256': digest(PACKET)}
    observer = session = None
    def check(name, passed, **details):
        report['checks'].append({'name': name, 'passed': bool(passed), **details})
        assert passed, name
    def close_owned_observer():
        if observer is None:
            return
        try:
            code = observer.close()
            report['producerCleanup'] = {'pid': observer.process.pid, 'exitCode': code,
                                         'gone': not Path(f'/proc/{observer.process.pid}').exists()}
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
    try:
        with PrivateHyprSession(output=output / 'private-session', main_env=main_env, width=320, height=240,
                                nested_lua=(BASE / 'private-nested.lua').read_bytes(),
                                dri_prime='pci-0000_00_02_0', mesa_vendor=True) as session, ExitStack() as resources:
            config_errors=session.ctl('configerrors')
            check('private nested config is valid', not config_errors.strip(), actualConfigErrors=config_errors)
            session.ctl('output', 'create', 'headless', 'ORACLE-SECOND')
            monitors = session.data('monitors')
            report['actualNativeOutputs'] = monitors
            check('actual private adjacent mixed-scale outputs',
                  len(monitors) == 2 and
                  any(m['name'] == 'WAYLAND-1' and m['width'] == 320 and m['height'] == 240 and m['scale'] == 1 and m['x'] == 0 and m['y'] == 0 and m['transform'] == 0 for m in monitors) and
                  any(m['name'] == 'ORACLE-SECOND' and m['width'] == 480 and m['height'] == 360 and m['scale'] == 1.5 and m['x'] == 320 and m['y'] == 0 and m['transform'] == 0 for m in monitors), monitors=monitors)
            for name in ('misc:disable_hyprland_logo', 'misc:disable_splash_rendering'):
                value = session.data('getoption', name)
                check(name + ' actually set', value.get('bool') is True and value.get('set') is True, observed=value)
            observer = Observer(packet['rasterLaunch'], session.env, output)
            # Runs before the private compositor/host context closes, including
            # every pixel/oracle failure; no live renderer is left in a dead bus.
            resources.callback(close_owned_observer)
            outputs = observer.find(lambda r: r.get('event') == 'outputs', 'actual hardware/owned output readiness')['outputs']
            check('reviewed real hardware/material before outputs', any(r.get('event') == 'backendObserved' and r.get('reviewed') is True and r.get('mappedMaterialMatches') is True for r in observer.rows), backend=[r for r in observer.rows if r.get('event') == 'backendObserved'])
            check('complete own output generation vector', {o['name'] for o in outputs} == {'WAYLAND-1', 'ORACLE-SECOND'}, outputs=outputs)
            sources = []
            for i, (width, height, x, y) in enumerate(((96, 80, 272, 32), (72, 48, 304, 56), (48, 32, 328, 68))):
                path = output / f'member-{i}.png'
                generated_source(path, width, height, i)
                sources.append({'stableId': f'abc{i + 1}', 'pid': os.getpid() + i,
                                'path': str(path), 'digest': digest(path), 'pixels': [width, height], 'captureScale': 1,
                                'nativeRect': {'x': x, 'y': y, 'width': width, 'height': height},
                                'atlasRect': {'x': x, 'y': y, 'width': width, 'height': height},
                                'iconRect': {'x': 380 + i * 8, 'y': 196, 'width': 24, 'height': 20},
                                'insets': {'left': 0, 'top': 0, 'right': 0, 'bottom': 0}})
            token = 'abcdef123456-1'
            identities = [{k: m[k] for k in ('stableId', 'pid')} for m in sources]
            observer.send(command='seed', token=token, operation='minimize', durationMs=1000, members=sources,
                          outputs=[{k: o[k] for k in ('name', 'generation')} for o in outputs])
            observer.find(lambda r: r.get('event') == 'seeded' and r.get('token') == token, 'complete immutable seed')
            for index, progress in enumerate((0.0, 0.35)):
                observer.send(command='sample', token=token, identities=identities, progress=progress)
                frames = {o['name']: observer.find(lambda r, name=o['name']: r.get('event') == 'presented' and r.get('accepted') is True and r.get('token') == token and r.get('progress') == progress and r.get('output') == name, f'actual complete held scene on {o["name"]}') for o in outputs}
                observer.send(command='state', observationId=f'held-{index}')
                state = observer.find(lambda r: r.get('event') == 'state' and r.get('observationId') == f'held-{index}', 'actual held state')
                check(f'held scene {index} no native authority', state['nativeReady'] is False and state['nativeEndpoint'] is False and not any(r.get('event') in ('ready', 'endpoint') for r in observer.rows))
                check(f'held scene {index} one upload per complete member', state['uploadCount'] == len(sources))
                for o in state['outputs']:
                    name, frame = o['name'], frames[o['name']]
                    check(f'{index}/{name} immutable buffer extent', frame['bufferWidth'] == o['bufferWidth'] and frame['bufferHeight'] == o['bufferHeight'])
                    image = output / f'actual-{index}-{name}.png'
                    subprocess.run(['grim', '-o', name, str(image)], env=session.env, capture_output=True, check=True, timeout=5)
                    fixture = {'output': o, 'token': token, 'progress': progress, 'members': sources,
                               'diagnosticNoNativeAuthority': True, 'screenshotMapping': 'untransformed-output-buffer',
                               'allowedPresentedSequences': [str(frame['sequence'])], 'backgroundRGBA': [0, 0, 0, 255],
                               'channelTolerance': 0 if progress == 0 and o['scale'] == 1 else 1}
                    current, decoded = verify_scene(fixture, frame)
                    width, height = current['bufferWidth'], current['bufferHeight']
                    expected = render(current, decoded)
                    actual = png_rgba(image, digest(image), (width, height))
                    comparison = compare(actual, expected, width, height, fixture['channelTolerance'])
                    stem = f'{index}-{name}'
                    (output / f'expected-{stem}.png').write_bytes(encode_png(width, height, expected))
                    for prefix, record in (('fixture', fixture), ('presented', frame), ('comparison', comparison)):
                        (output / f'{prefix}-{stem}.json').write_text(json.dumps(record, indent=2) + '\n')
                    check(f'{stem} complete RGBA', comparison['passed'], comparison=comparison)
            observer.send(command='cancel', token=token, identities=identities)
            observer.find(lambda r: r.get('event') == 'cancelled' and r.get('token') == token, 'latest exact scene cancellation')
            check('normal owned renderer exit', observer.close() == 0)
            report['result'] = 'pass'
    except Exception as error:
        report['result'], report['error'] = 'fail', repr(error)
    finally:
        if session:
            report['privateSession'] = session.evidence
    report['mainClientsAfter'] = json.loads(subprocess.check_output(['hyprctl', '-j', 'clients'], env=main_env, text=True, timeout=4))
    identity = lambda rows: sorted((r['address'], r['stableId'], r['pid']) for r in rows)
    report['originalMainIdentitiesPreserved'] = identity(main_before) == identity(report['mainClientsAfter'])
    try:
        report['preservation'],preservation_details=observations.compare(preservation_before,output/'main-after')
        (output/'preservation-details.json').write_text(json.dumps(preservation_details,indent=2)+'\n')
    except Exception as error:
        report['preservationError']=repr(error);report['preservation']={}
    report['frozenSourcesUnchanged'] = all(digest(p) == h for p, h in manifest['inputs'].items()) and all(digest(p) == h for p, h in packet['inputs'].items())
    if not report['originalMainIdentitiesPreserved'] or not report['frozenSourcesUnchanged'] or report.get('producerCleanupError') or report.get('forcedProducerTermination') or not report['preservation'] or not all(report['preservation'].values()):
        report['result'] = 'fail'
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'result': report['result'], 'checks': len(report['checks']), 'error': report.get('error'), 'sourcesUnchanged': report['frozenSourcesUnchanged'], 'reportSHA256': digest(output / 'report.json')}))
    return int(report['result'] != 'pass')


if __name__ == '__main__':
    raise SystemExit(main())
