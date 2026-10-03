"""Read-only exact attribution of the immutable root V7 prefix observations."""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent.parent
EVIDENCE = Path('/home/hoskinson/window-integration-qa/family-raster-causal-v7/attempt-1')
sys.path.insert(0, str(BASE / 'producer-causal-v5'))
from verify_causal import bind, compare_observation, read_image
sys.path.insert(0, str(BASE / 'raster-attribution-v6'))
from audit_pixels import exact_pixel, nearest
from compare_scene import verify_scene


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report = {'scope': 'retained-prefix attribution only', 'nativeLaunch': False,
              'GPUOperation': False, 'oracleChanged': False, 'toleranceChanged': False,
              'inputs': {}, 'bindings': [], 'failedFinalPixels': []}
    def load(name):
        path = EVIDENCE / name
        report['inputs'][str(path)] = digest(path)
        return json.loads(path.read_text())

    source_report = load('report.json')
    assert digest(EVIDENCE / 'report.json') == '91910b36f135bd936ce52114343a2523820b207dd6f527b4fb651506a2371acc'
    for scene in ('0-WAYLAND-1', '0-ORACLE-SECOND', '1-WAYLAND-1', '1-ORACLE-SECOND'):
        fixture = load(f'fixture-{scene}.json')
        final = load(f'comparison-raw-{scene}.json')
        presented = load(f'presented-{scene}.json')
        output, sources = verify_scene(fixture, presented)
        sources = [{**m, 'stableId': s['stableId'], 'pid': s['pid']}
                   for m, s in zip(sources, fixture['members'], strict=True)]
        prefixes = {}
        for path in sorted(EVIDENCE.glob(f'causal-{scene}-*.json')):
            observation = load(path.name)
            record = observation['observation']
            binding = observation['binding']
            actual_comparison = compare_observation(record, fixture, binding['fullReadback'],
                binding['swap'], binding['presented'], EVIDENCE / 'owned-readbacks')
            assert actual_comparison == observation['comparison']
            report['bindings'].append({'scene': scene, 'kind': record['kind'],
                'prefixCount': record['prefixCount'], 'comparison': actual_comparison})
            if record['kind'] == 'member-prefix':
                pixels = read_image(EVIDENCE / 'owned-readbacks', record['rgbaFilename'],
                    record['rgbaSHA256'], (output['bufferWidth'], output['bufferHeight']))
                prefixes[record['prefixCount']] = pixels
            for key in ('rgbaFilename', 'nativeRGBAFilename'):
                image = EVIDENCE / 'owned-readbacks' / record[key]
                report['inputs'][str(image)] = digest(image)
        assert set(prefixes) == set(range(1, len(sources) + 1))
        # Root's comparison file has the unchanged full-reference failure list.
        comparison = final.get('comparison', final)
        if 'RGBA' in comparison:
            comparison = comparison['RGBA']
        failures = comparison['firstFailures']
        assert comparison['badPixels'] == len(failures)  # this retained fixture has <=16
        for failure in failures:
            x, y = failure['x'], failure['y']
            base = (y * output['bufferWidth'] + x) * 4
            previous = [0, 0, 0, 0]
            stages = []
            for n, source in enumerate(sources, 1):
                _, sample_steps = exact_pixel(output, [source], x, y)
                observed = list(prefixes[n][base:base + 4])
                if sample_steps:
                    sample = [F(v) for v in sample_steps[0]['sampleRGBA']]
                    rational = [sample[c] + previous[c] * (1 - sample[3] / 255)
                                for c in range(4)]
                    expected_new = [nearest(v) for v in rational]
                    steps = sample_steps[0]
                else:
                    sample = None
                    rational = [F(v) for v in previous]
                    expected_new = previous[:]
                    steps = None
                delta = [a - b for a, b in zip(observed, expected_new, strict=True)]
                stages.append({'prefixCount': n, 'identity': [source['stableId'], source['pid']],
                    'covered': sample is not None, 'actualPreviousPrefixRGBA': previous,
                    'exactSample': steps, 'exactOverActualPrevious': [str(v) for v in rational],
                    'nearestOverActualPreviousRGBA': expected_new,
                    'actualPrefixRGBA': observed, 'newPerDrawDelta': delta})
                previous = observed
            ideal_final, _ = exact_pixel(output, sources, x, y)
            report['failedFinalPixels'].append({'scene': scene, 'pixel': [x, y],
                'idealReferenceRGBA': ideal_final, 'actualFinalPrefixRGBA': previous,
                'accumulatedDelta': [a - b for a, b in zip(previous, ideal_final, strict=True)],
                'stages': stages})
    assert len(report['bindings']) == 18
    assert len(report['failedFinalPixels']) == 9
    del source_report
    report['maximumNewPerDrawChannelDeltaAtFailedCoordinates'] = max(
        abs(d) for p in report['failedFinalPixels'] for s in p['stages']
        for d in s['newPerDrawDelta'])
    assert report['maximumNewPerDrawChannelDeltaAtFailedCoordinates'] == 1
    report['inference'] = ('At all nine retained final failing coordinates, each new draw differs '
        'by at most one channel unit from exact rational sampling/source-over using the ACTUAL '
        'preceding prefix. Consecutive differences accumulate beyond the unchanged full-reference '
        'bound. This is not proof uniquely distinguishing textured sampling, blend or attachment '
        'arithmetic; it is not a replacement acceptance reference. All original failed comparisons '
        'remain failed. Prefixes themselves have no presentation or native authority.')
    for path in (Path(__file__), BASE / 'producer-causal-v5/verify_causal.py',
                 BASE / 'raster-attribution-v6/audit_pixels.py'):
        report['inputs'][str(path)] = digest(path)
    target = Path(__file__).parent / 'retained-v7-prefix-attribution.json'
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'bindings': 18, 'finalFailedCoordinates': 9,
        'maximumNewDelta': 1, 'reportSHA256': digest(target), 'nativeLaunch': False}))


if __name__ == '__main__':
    main()
