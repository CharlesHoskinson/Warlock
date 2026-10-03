#!/usr/bin/env python3
"""Compare a whole held diagnostic scene against frozen independent sources."""
import argparse
import hashlib
import json
import os
from pathlib import Path

from raster_oracle import compare, encode_png, png_rgba, premultiply, render


def verify_scene(fixture, presented):
    output = fixture['output']
    if presented.get('event') != 'presented' or presented.get('accepted') is not True:
        raise ValueError('requires actual accepted own presentation evidence')
    if presented.get('token') != fixture['token']:
        raise ValueError('scene token differs from frozen fixture')
    if presented.get('output') != output['name'] or presented.get('generation') != output['generation']:
        raise ValueError('actual presented output/generation differs')
    if str(presented.get('sequence', '')) not in fixture['allowedPresentedSequences']:
        raise ValueError('actual sequence was not independently captured for this screenshot')
    if int(presented.get('timestampNs', 0)) <= 0 or int(presented.get('submittedNs', 0)) <= 0:
        raise ValueError('missing actual submission/presentation timestamp')
    if int(presented['timestampNs']) < int(presented['submittedNs']):
        raise ValueError('presentation precedes submission')
    if float(presented.get('progress', -1)) != float(fixture['progress']):
        raise ValueError('actual held progress differs from predeclared fixture')
    if fixture.get('diagnosticNoNativeAuthority') is not True:
        raise ValueError('requires explicit diagnostic-only fixture')
    if output.get('transform') != 0 or fixture.get('screenshotMapping') != 'untransformed-output-buffer':
        raise ValueError('scanout transform mapping needs separate native proof')
    expected = [{k: m[k] for k in ('stableId', 'pid', 'digest')} for m in fixture['members']]
    frames = presented.get('members', [])
    actual = [{k: m.get(k) for k in ('stableId', 'pid', 'digest')} for m in frames]
    if not expected or actual != expected:
        raise ValueError('complete ordered actual scene source vector differs')
    if len({m['stableId'] for m in expected}) != len(expected):
        raise ValueError('fixture contains duplicate identities')
    sources = []
    for immutable, actual_frame in zip(fixture['members'], frames, strict=True):
        width, height = immutable['pixels']
        raw = png_rgba(Path(immutable['path']), immutable['digest'], (width, height))
        sources.append({'pixels': (width, height), 'premultiplied': premultiply(raw),
                        'rectangle': actual_frame['rectangle']})
    return output, sources


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fixture', type=Path, required=True)
    parser.add_argument('--presented', type=Path, required=True)
    parser.add_argument('--screenshot', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    fixture_bytes, frame_bytes = args.fixture.read_bytes(), args.presented.read_bytes()
    fixture, frame = json.loads(fixture_bytes), json.loads(frame_bytes)
    output, sources = verify_scene(fixture, frame)
    width, height = output['bufferWidth'], output['bufferHeight']
    image_digest = hashlib.sha256(args.screenshot.read_bytes()).hexdigest()
    actual = png_rgba(args.screenshot, image_digest, (width, height))
    expected = render(output, sources, tuple(fixture['backgroundRGBA']))
    result = compare(actual, expected, width, height, fixture['channelTolerance'])
    result.update({'scope': 'full raster held diagnostic scene; no cadence/native authority claim',
                   'fixtureSHA256': hashlib.sha256(fixture_bytes).hexdigest(),
                   'presentedEvidenceSHA256': hashlib.sha256(frame_bytes).hexdigest(),
                   'screenshotSHA256': image_digest,
                   'token': frame['token'], 'output': frame['output'], 'generation': frame['generation'],
                   'actualPresentedSequence': frame['sequence'], 'progress': frame['progress'],
                   'memberCount': len(sources)})
    os.umask(0o077)
    args.output.mkdir(mode=0o700, exist_ok=False)
    (args.output / 'expected.png').write_bytes(encode_png(width, height, expected))
    (args.output / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return int(not result['passed'])


if __name__ == '__main__':
    raise SystemExit(main())
