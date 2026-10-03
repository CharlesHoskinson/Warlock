#!/usr/bin/env python3
"""Whole composite GPU raster on fully private headless GL host/nested Hyprland."""
import argparse
from contextlib import ExitStack
import hashlib
import json
import os
import stat
import re
from pathlib import Path
import subprocess
import sys
import importlib.util

from compare_scene import verify_scene
from producer_observer import Observer, generated_source
import observations
from raster_oracle import compare, encode_png, png_rgba, render
from cursor_fixture import require_invisible_private_cursor, require_deterministic_owned_raster
from precision_fixture import require_explicit_high_precision
from readback_evidence import verify_readback, record_pixels, all_pixels_accepted
from verify_causal_target import verify_target

BASE = Path(__file__).resolve().parent
HOST = BASE.parent / 'private-weston-aq-host-v4'
CAUSAL = Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/producer-production-default-v10')
PACKET = CAUSAL / 'manifest-v10.json'
PRODUCER = CAUSAL / 'hypr-motion-renderer-staged'
FOUNDATION = BASE.parent/'private-graphics-foundation-v3/attempt-1/report.json'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def frozen_inputs_exact(manifest):
    return all(digest(path) == expected for path, expected in manifest['inputs'].items()) and all(
        Path(path).is_symlink() and os.readlink(path) == expected
        for path, expected in manifest.get('symlinks',manifest.get('links', {})).items()) and all(
        stat.S_IMODE(Path(path).stat().st_mode)==expected
        for path, expected in manifest.get('inputModes',{}).items())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((BASE / 'frozen-inputs.json').read_text())
    assert frozen_inputs_exact(manifest), 'frozen raster inputs or loader links changed'
    packet = json.loads(PACKET.read_text())
    assert frozen_inputs_exact(packet), 'producer bytes modes or loader links changed'
    for path, expected in packet['inputs'].items():
        assert digest(path) == expected, f'producer input differs: {path}'
    spec = importlib.util.spec_from_file_location('_causal_verifier', CAUSAL / 'verify_causal.py')
    causal = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(causal)
    sys.path.insert(0,str(CAUSAL))
    spec=importlib.util.spec_from_file_location('_quantized_configuration',CAUSAL/'verify_quantized_over.py')
    quantized=importlib.util.module_from_spec(spec);spec.loader.exec_module(quantized)
    shader_hashes=quantized.shader_digests((CAUSAL/'QuantizedOver.hpp').read_text())
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
    import weston_host
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
              'nativeTransportAccepted': False, 'nativeOutputFeedbackProof': False, 'result': 'pending', 'mainClientsBefore': main_before, 'producerPacketSHA256': digest(PACKET)}
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
            xwayland = session.data('getoption', 'xwayland:enabled')
            check('actual private Xwayland disabled', xwayland.get('bool') is False, observed=xwayland)
            aq = BASE.parent/'aquamarine-nested-lifecycle-v1/prefix/lib/libaquamarine.so.0.15.0'
            mappings = weston_host.original.mapped_files(session.evidence['compositorPID'])
            check('actual mandatory-parent lifecycle Aquamarine mapped privately',
                  mappings['files'].get(str(aq)) == digest(aq), mappedSHA256=mappings['files'].get(str(aq)))
            cursor_option = require_invisible_private_cursor(session)
            check('actual private cursor suppressed before full image capture', True, observed=cursor_option)
            readiness = session.evidence.get('ipcReadiness', [])
            check('private readiness has complete exact child read-only reply',
                  len(readiness) == 1 and readiness[0]['peer']['pid'] == session.evidence['compositorPID'] and
                  readiness[0]['peer']['uid'] == os.getuid() and readiness[0]['request'] == 'j/version' and
                  readiness[0]['completeServerEOF'] is True, observed=readiness)
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
            readback_directory = output / 'owned-readbacks'
            readback_directory.mkdir(mode=0o700)
            observer = Observer([str(PRODUCER), '--raster-fixture', '--causal-readback-dir', str(readback_directory)], session.env, output)
            # Runs before the private compositor/host context closes, including
            # every pixel/oracle failure; no live renderer is left in a dead bus.
            resources.callback(close_owned_observer)
            outputs = observer.find(lambda r: r.get('event') == 'outputs', 'actual hardware/owned output readiness')['outputs']
            from verify_production_pipeline import verify_selection
            selected=verify_selection(observer.rows,'diagnostic-default')
            check('actual repaired default pipeline selected without experimental flag',selected['actualModeSelectionGate'],observed=selected)
            raster_state = require_deterministic_owned_raster(observer.rows)
            check('actual producer GL_DITHER disabled before source upload', True, observed=raster_state)
            shader_precision = require_explicit_high_precision(observer.rows)
            check('actual vertex and fragment precision satisfy explicit highp contract', True, observed=shader_precision)
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
                readbacks = {o['name']: observer.find(lambda r, name=o['name']: r.get('event') == 'ownedFramebufferReadback' and r.get('token') == token and r.get('progress') == progress and r.get('output') == name, f'actual owned pre-swap readback on {o["name"]}') for o in outputs}
                frames = {o['name']: observer.find(lambda r, name=o['name']: r.get('event') == 'presented' and r.get('accepted') is True and r.get('token') == token and r.get('sequence') == readbacks[name]['sequence'] and r.get('output') == name, f'actual matching readback presentation on {o["name"]}') for o in outputs}
                if index == 0:
                    check('actual primary parent output presentation', frames['WAYLAND-1']['accepted'] is True)
                    report['nativeOutputFeedbackProof'] = True
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
                    readback = readbacks[name]
                    raw_actual, readback_png_digest = verify_readback(readback, frame, readback_directory)
                    swap = observer.find(lambda r: r.get('event') == 'swap' and r.get('sequence') == frame['sequence'] and r.get('output') == name, 'matching owned readback swap')
                    check(f'{index}/{name} exact readback successful swap', swap.get('success') is True and all(swap.get(key) == frame.get(key) for key in ('token', 'digest', 'generation', 'progress', 'members', 'bufferWidth', 'bufferHeight')))
                    configuration=quantized.verify(observer.rows,readback,sources,shader_hashes)
                    check(f'{index}/{name} actual immutable per-layer ping-pong configuration',
                          configuration['actualConfigurationGate'] and configuration['nativeAuthority'] is False
                          and configuration['pixelProof'] is False,observed=configuration)
                    matching=[r for r in observer.rows if r.get('event')=='quantizedOverFrameConfigured' and r.get('sequence')==readback['sequence']]
                    (output/f'quantized-configuration-{index}-{name}.json').write_text(json.dumps(
                        {'configuration':configuration,'actualEvent':matching[0],
                         'binding':{'readback':readback,'swap':swap,'presented':frame},
                         'expectedShaderSHA256':list(shader_hashes)},indent=2)+'\n')
                    raw_expected = render(current, decoded, (0, 0, 0, 0))
                    raw_comparison = compare(raw_actual, raw_expected, width, height, fixture['channelTolerance'])
                    expected = render(current, decoded)
                    actual = png_rgba(image, digest(image), (width, height))
                    comparison = compare(actual, expected, width, height, fixture['channelTolerance'])
                    stem = f'{index}-{name}'
                    (output / f'expected-{stem}.png').write_bytes(encode_png(width, height, expected))
                    (output / f'expected-raw-{stem}.png').write_bytes(encode_png(width, height, raw_expected))
                    for prefix, record in (('readback', readback), ('comparison-raw', raw_comparison)):
                        (output / f'{prefix}-{stem}.json').write_text(json.dumps(record, indent=2) + '\n')
                    for prefix, record in (('fixture', fixture), ('presented', frame), ('comparison', comparison)):
                        (output / f'{prefix}-{stem}.json').write_text(json.dumps(record, indent=2) + '\n')
                    record_pixels(report['checks'], f'{stem} complete producer RGBA', raw_comparison, readbackPNG_SHA256=readback_png_digest)
                    record_pixels(report['checks'], f'{stem} complete composed RGBA', comparison)
                    records = [r for r in observer.rows if r.get('event') == 'ownedCausalReadback'
                               and r.get('output') == name and r.get('sequence') == frame['sequence']]
                    prefixes = [r.get('prefixCount') for r in records if r.get('kind') == 'member-prefix']
                    controls = [tuple(c.get('index') for c in r.get('controls', []))
                                for r in records if r.get('kind') == 'constant-control']
                    check(f'{stem} complete unique actual prefix and control vector',
                          prefixes == [1, 2, 3] and controls == ([(1,), (0, 1), (0, 1, 2)] if index == 0 else [])
                          and len(records) == (6 if index == 0 else 3))
                    for serial, record in enumerate(records):
                        shader_events = [r for r in observer.rows if r.get('event') == 'quantizedOverExperiment']
                        assert len(shader_events) == 1
                        target_binding = verify_target(record, matching[0], shader_events[0]['copyProgram'], quantized.copy_state)
                        check(f'{stem}/{serial} actual current prefix copy to default read target',
                              target_binding['actualCausalTargetBound'] and not target_binding['pixelProof']
                              and not target_binding['nativeAuthority'], observed=target_binding)
                        result = causal.compare_observation(record, fixture, readback, swap, frame, readback_directory)
                        retained = {'observation': record, 'comparison': result,
                                    'targetBinding': target_binding,
                                    'binding': {'fullReadback': readback, 'swap': swap, 'presented': frame}}
                        (output / f'causal-{stem}-{serial}.json').write_text(json.dumps(retained, indent=2) + '\n')
                        record_pixels(report['checks'], f'{stem}/{serial} complete causal RGBA', result['RGBA'])
                        record_pixels(report['checks'], f'{stem}/{serial} complete native-format causal RGBA', result['nativeRGBA'])
                        check(f'{stem}/{serial} actual complete read-format equality', result['readFormatCompleteEquality'])
            observer.send(command='cancel', token=token, identities=identities)
            observer.find(lambda r: r.get('event') == 'cancelled' and r.get('token') == token, 'latest exact scene cancellation')
            check('normal owned renderer exit', observer.close() == 0)
            final_checks = [r for r in report['checks'] if 'comparison' in r and
                            ('complete producer RGBA' in r['name'] or 'complete composed RGBA' in r['name'])]
            report['fullFinalRasterAccepted'] = all_pixels_accepted(final_checks)
            report['causalDiagnosticAccepted'] = all_pixels_accepted(report['checks'], expected_count=44)
            report['result'] = 'pass' if report['causalDiagnosticAccepted'] else 'fail'
            if report['result'] == 'fail':
                report['error'] = 'Full RGBA comparison failed; all independent planned pixel observations retained'
    except Exception as error:
        report['result'], report['error'] = 'fail', repr(error)
    finally:
        if session:
            report['privateSession'] = session.evidence
    evidence_file = output/'private-session/host-evidence.json'
    if evidence_file.exists():
        report['privateSession'] = json.loads(evidence_file.read_text())
    evidence = report.get('privateSession', {})
    cleanup = not evidence.get('cleanupErrors') and evidence.get('remainingDescendants') == [] and evidence.get('unexpectedInnerDescendants') == [] and evidence.get('runtimeGone') is True
    report['normalPrivateHostCleanup'] = bool(cleanup)
    protocol_log = (output/'private-session/hyprland.log').read_text() if (output/'private-session/hyprland.log').exists() else ''
    archived = list((output/'private-session/runtime-archive/hypr').glob('*/hyprland.log'))
    archive_log = archived[0].read_text() if len(archived) == 1 else ''
    weston_log = (output/'private-session/weston-renderer.log').read_text() if (output/'private-session/weston-renderer.log').exists() else ''
    forbidden = r'\[libseat\]|DRM Backend failed|Starting the DRM backend|enabling fallbacks|error [0-9]+:|Broken pipe|parent transport failed|xdg_surface[^\n]*never[^\n]*configured'
    backend_clean = not re.search(forbidden, protocol_log+'\n'+archive_log+'\n'+weston_log, re.I)
    backend_selected = 'Private AQ_BACKENDS=wayland: mandatory parent, no DRM or libseat backend' in archive_log
    ack_observed = 'Output WAYLAND-1: configure surface with ' in archive_log
    report['actualParentBackend'] = {'clean': backend_clean, 'mandatorySelected': backend_selected, 'configureAckObserved': ack_observed}
    report['mainClientsAfter'] = json.loads(subprocess.check_output(['hyprctl', '-j', 'clients'], env=main_env, text=True, timeout=4))
    identity = lambda rows: sorted((r['address'], r['stableId'], r['pid']) for r in rows)
    report['originalMainIdentitiesPreserved'] = identity(main_before) == identity(report['mainClientsAfter'])
    try:
        report['preservation'],preservation_details=observations.compare(preservation_before,output/'main-after')
        (output/'preservation-details.json').write_text(json.dumps(preservation_details,indent=2)+'\n')
    except Exception as error:
        report['preservationError']=repr(error);report['preservation']={}
    report['frozenSourcesUnchanged'] = frozen_inputs_exact(manifest) and all(digest(p) == h for p, h in packet['inputs'].items())
    if not report['originalMainIdentitiesPreserved'] or not report['frozenSourcesUnchanged'] or report.get('producerCleanupError') or report.get('forcedProducerTermination') or not report['preservation'] or not all(report['preservation'].values()) or not cleanup or not backend_clean or not backend_selected or not ack_observed:
        report['result'] = 'fail'
    report['nativeTransportAccepted'] = bool(report['nativeOutputFeedbackProof'] and cleanup and backend_clean and backend_selected and ack_observed and report['frozenSourcesUnchanged'] and report['preservation'] and all(report['preservation'].values()) and report.get('producerCleanup',{}).get('exitCode') == 0 and not report.get('forcedProducerTermination'))
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'result': report['result'], 'checks': len(report['checks']), 'error': report.get('error'), 'sourcesUnchanged': report['frozenSourcesUnchanged'], 'reportSHA256': digest(output / 'report.json')}))
    return int(report['result'] != 'pass')


if __name__ == '__main__':
    raise SystemExit(main())
