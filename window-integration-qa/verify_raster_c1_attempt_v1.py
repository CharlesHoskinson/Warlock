#!/usr/bin/env python3
"""Independent, read-only pixel replay and closure audit after a terminal run."""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import stat
import sys


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def gone(row):
    path = Path('/proc') / str(row['pid']) / 'stat'
    if not path.exists():
        return True
    text = path.read_text()
    return text[text.rindex(')') + 2:].split()[19] != str(row['start'])


def main():
    base, attempt = map(lambda s: Path(s).resolve(), sys.argv[1:])
    assert base.parent == Path('/home/hoskinson/window-integration-qa')
    assert base.name.startswith(('family-raster-causal-v', 'family-raster-sampler-v','family-raster-quantized-v','family-raster-default-readback-v','family-raster-production-default-v','family-raster-c1-v'))
    assert attempt.parent == base
    report = json.loads((attempt / 'report.json').read_text())
    manifest = json.loads((base / 'frozen-inputs.json').read_text())
    sys.path.insert(0, str(base))
    import run_private_raster as runner
    from compare_scene import verify_scene
    from raster_oracle import render, compare, png_rgba
    from readback_evidence import verify_readback
    spec = importlib.util.spec_from_file_location('_root_causal', runner.CAUSAL / 'verify_causal.py')
    causal = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(causal)
    event_path = attempt / 'producer-events.jsonl'
    events = [json.loads(line) for line in event_path.read_text().splitlines()]
    assert all(isinstance(row, dict) for row in events)
    fixtures = sorted(attempt.glob('fixture-*.json'))
    replays = []
    causal_count = 0
    target_bindings = []
    for fixture_path in fixtures:
        stem = fixture_path.stem.removeprefix('fixture-')
        fixture = json.loads(fixture_path.read_text())
        presented = json.loads((attempt / f'presented-{stem}.json').read_text())
        readback = json.loads((attempt / f'readback-{stem}.json').read_text())
        assert presented in events and readback in events
        output, sources = verify_scene(fixture, presented)
        actual, _ = verify_readback(readback, presented, attempt / 'owned-readbacks')
        raw = compare(actual, render(output, sources, (0, 0, 0, 0)), output['bufferWidth'], output['bufferHeight'], fixture['channelTolerance'])
        image = attempt / f'actual-{stem}.png'
        composed = compare(png_rgba(image, sha(image), (output['bufferWidth'], output['bufferHeight'])), render(output, sources), output['bufferWidth'], output['bufferHeight'], fixture['channelTolerance'])
        for label, result in (('raw', raw), ('composed', composed)):
            target = attempt / (f'comparison-raw-{stem}.json' if label == 'raw' else f'comparison-{stem}.json')
            assert result == json.loads(target.read_text()), str(target)
            replays.append({'name': f'{stem}/{label}', 'passed': result['passed'], 'comparison': result})
        for path in sorted(attempt.glob(f'causal-{stem}-*.json')):
            retained = json.loads(path.read_text())
            binding = retained['binding']
            assert retained['observation'] in events
            assert all(binding[k] in events for k in ('fullReadback', 'swap', 'presented'))
            assert binding['fullReadback'] == readback and binding['presented'] == presented
            if base.name.startswith(('family-raster-default-readback-v','family-raster-production-default-v','family-raster-c1-v')):
                sys.path.insert(0, str(runner.CAUSAL))
                from verify_quantized_over import copy_state
                from verify_causal_target import verify_target
                matching = [e for e in events if e.get('event') == 'quantizedOverFrameConfigured'
                            and e.get('sequence') == readback['sequence']]
                shaders = [e for e in events if e.get('event') == 'quantizedOverExperiment']
                assert len(matching) == len(shaders) == 1
                target = verify_target(retained['observation'], matching[0], shaders[0]['copyProgram'], copy_state)
                assert target == retained['targetBinding']
                target_bindings.append(target)
            result = causal.compare_observation(retained['observation'], fixture, readback, binding['swap'], presented, attempt / 'owned-readbacks')
            assert result == retained['comparison'], str(path)
            assert result['readFormatCompleteEquality']
            for key in ('RGBA', 'nativeRGBA'):
                replays.append({'name': path.name + '/' + key, 'passed': result[key]['passed'], 'comparison': result[key]})
            causal_count += 1
    host = report['privateSession']
    identities = host['observedDescendantIdentities'] + [host[k] for k in ('privateBus', 'weston', 'hyprland')]
    processes = [{'pid': p['pid'], 'start': p['start'], 'gone': gone(p)} for p in identities]
    sys.path.insert(0, str(base.parent / 'qt-modal-private-v9'))
    transport_spec = importlib.util.spec_from_file_location('_root_transport', base.parent / 'qt-modal-private-v9/run_native.py')
    transport_module = importlib.util.module_from_spec(transport_spec)
    transport_spec.loader.exec_module(transport_module)
    archived = [Path(p['archive']) for p in host['archivedRuntime'] if Path(p['archive']).name == 'hyprland.log']
    assert len(archived) == 1
    logs = [archived[0], attempt / 'private-session/weston-renderer.log']
    transport = transport_module.transport_log_gate([p.read_text() for p in logs])
    checks = {
        'allFrozenInputsExact': all(sha(p) == h for p, h in manifest['inputs'].items()),
        'allFrozenLinksExact': all(Path(p).is_symlink() and os.readlink(p) == t for p, t in manifest['symlinks'].items()),
        'allDeclaredFrozenModesExact': all(stat.S_IMODE(Path(p).stat().st_mode) == mode for p, mode in manifest.get('inputModes', {}).items()),
        'all15MainPreservation': len(report['preservation']) == 15 and all(report['preservation'].values()),
        'allRecordedPIDStartGone': all(p['gone'] for p in processes),
        'actualProducerNormalWaitZeroAndGone': report['producerCleanup']['exitCode'] == 0 and not Path('/proc', str(report['producerCleanup']['pid'])).exists() and not report.get('producerCleanupError') and not report.get('forcedProducerTermination'),
        'ownedRuntimeGone': host['runtimeGone'] and not Path(host['runtime']).exists(),
        'strictHostCleanup': not any(host[k] for k in ('remainingDescendants', 'unexpectedInnerDescendants', 'cleanupErrors')),
        'archivedMandatoryParentTransportHealthy': transport['passed'],
        'all44ImagesIndependentlyReplayed': len(fixtures) == 4 and causal_count == 18 and len(replays) == 44,
        'allActualEventsValidAndNoAuthority': not any(e.get('event') in ('fatal', 'rejected', 'ready', 'endpoint') for e in events),
    }
    sampling = None
    quantized_configurations=[]
    if base.name.startswith('family-raster-sampler-v'):
        from sampler_evidence import verify_sampler, fragment_digest
        sampling = verify_sampler(events, fixture['members'], fragment_digest(runner.CAUSAL / 'SamplingExperiment.hpp'))
        checks['actualSamplerIndependentlyBound'] = sampling['configurationAccepted']
    if base.name.startswith(('family-raster-quantized-v','family-raster-default-readback-v','family-raster-production-default-v','family-raster-c1-v')):
        sys.path.insert(0,str(runner.CAUSAL))
        spec=importlib.util.spec_from_file_location('_root_quantized',runner.CAUSAL/'verify_quantized_over.py')
        quantized=importlib.util.module_from_spec(spec);spec.loader.exec_module(quantized)
        expected_shaders=quantized.shader_digests((runner.CAUSAL/'QuantizedOver.hpp').read_text())
        for fixture_path in fixtures:
            stem=fixture_path.stem.removeprefix('fixture-')
            fixture=json.loads(fixture_path.read_text());readback=json.loads((attempt/f'readback-{stem}.json').read_text())
            retained=json.loads((attempt/f'quantized-configuration-{stem}.json').read_text())
            actual=quantized.verify(events,readback,fixture['members'],expected_shaders)
            assert actual==retained['configuration'] and retained['actualEvent'] in events
            assert retained['expectedShaderSHA256']==list(expected_shaders)
            assert retained['binding']['readback']==readback
            assert all(retained['binding'][key] in events for key in ('swap','presented'))
            quantized_configurations.append(actual)
        checks['all4ActualQuantizedFramesIndependentlyBound']=len(quantized_configurations)==4 and all(c['actualConfigurationGate'] and not c['pixelProof'] and not c['nativeAuthority'] for c in quantized_configurations)
    if base.name.startswith(('family-raster-default-readback-v','family-raster-production-default-v','family-raster-c1-v')):
        checks['all18CausalDefaultTargetsIndependentlyBound'] = len(target_bindings) == 18 and all(
            t['actualCausalTargetBound'] and not t['pixelProof'] and not t['nativeAuthority'] for t in target_bindings)
    if base.name.startswith(('family-raster-production-default-v','family-raster-c1-v')):
        from verify_production_pipeline import verify_selection
        selected=verify_selection(events,'diagnostic-default')
        checks['actualDefaultRoleWithoutExperimentIndependentlyVerified']=selected['actualModeSelectionGate']
    completion = {
        'updatedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'reportSHA256': sha(attempt / 'report.json'), 'manifestSHA256': sha(base / 'frozen-inputs.json'),
        'inputCount': len(manifest['inputs']), 'linkCount': len(manifest['symlinks']),
        'independentChecks': checks, 'allIndependentChecks': all(checks.values()),
        'replayedComparisons': replays, 'processes': processes, 'transport': transport,
        'sampling': sampling, 'eventsSHA256': sha(event_path), 'logSHA256': {str(p): sha(p) for p in logs},
        'quantizedConfigurations':quantized_configurations,
        'causalTargetBindings': target_bindings,
        'rasterAccepted': all(checks.values()) and all(p['passed'] for p in replays),
        'physicalCadenceAccepted': False, 'fullWindowsParityAccepted': False,
        'mainGUIWrites': False, 'mainRestorationWrites': False,
    }
    path = attempt / 'root-completion.json'
    with path.open('x') as stream:
        json.dump(completion, stream, indent=2); stream.write('\n')
    path.chmod(0o600)
    print(json.dumps({'artifact': str(path), 'allIndependentChecks': completion['allIndependentChecks'], 'replayed': len(replays), 'rasterAccepted': completion['rasterAccepted']}))
    return int(not completion['allIndependentChecks'])


if __name__ == '__main__':
    raise SystemExit(main())
