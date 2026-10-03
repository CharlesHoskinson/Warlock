"""Create a read-only provenance packet; never invokes native code."""
import hashlib
import json
from pathlib import Path
from verify_sampling import fragment_digest

HERE = Path(__file__).resolve().parent
BASE = HERE.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    target = HERE / 'manifest-v6.json'
    checkpoint = HERE / 'checkpoint-v6.json'
    if target.exists() or checkpoint.exists():
        raise SystemExit('fresh immutable freeze destination required')
    inherited = json.loads((BASE / 'producer-causal-v5/manifest-v5.json').read_text())
    inputs = dict(inherited['inputs'])
    if len(inputs) != 262:
        raise SystemExit('unexpected original V5 frozen input count')
    for filename, expected in inputs.items():
        if sha(Path(filename)) != expected:
            raise SystemExit('original V5 frozen input changed: ' + filename)
    for directory in (HERE, BASE / 'raster-attribution-v7'):
        for path in sorted(directory.iterdir()):
            if path.is_file():
                inputs[str(path)] = sha(path)
    attribution = json.loads((BASE / 'raster-attribution-v7/retained-v7-prefix-attribution.json').read_text())
    for filename, expected in attribution['inputs'].items():
        if sha(Path(filename)) != expected:
            raise SystemExit('retained native attribution input changed: ' + filename)
        inputs[filename] = expected
    evidence = Path('/home/hoskinson/window-integration-qa/family-raster-causal-v7/attempt-1')
    for n in range(3):
        path = evidence / f'member-{n}.png'
        inputs[str(path)] = sha(path)
    binary = HERE / 'hypr-motion-renderer-staged'
    packet = {
        'scope': 'explicit four-center sampler diagnostic only; no native execution or repair acceptance',
        'nativeLaunch': False, 'GPUOperation': False,
        'original262InputsUnchanged': True, 'binary': str(binary), 'binarySHA256': sha(binary),
        'fragmentSHA256': fragment_digest((HERE / 'SamplingExperiment.hpp').read_text()),
        'launch': [str(binary), '--raster-fixture', '--causal-readback-dir',
                   '<existing-private-0700-directory>', '--manual-bilinear-experiment'],
        'readinessAuthority': False, 'endpointAuthority': False,
        'pixelComparisonsUnchanged': True, 'toleranceChanged': False,
        'samplingGetterSchema': {
            'event': 'samplingConfigured', 'policy': 'four-nearest-centers-highp-bilinear-v1',
            'sourceDigest': 'actual immutable family PNG SHA256 or empty for controls',
            'pixels': 'actual decoded/uploaded extent', 'controlIndex': '-1 family; 0/1/2 1x1 controls',
            'minFilter': 9728, 'magFilter': 9728, 'wrapS': 33071, 'wrapT': 33071,
            'extentUniform': 'actual queried uniform must exactly equal source extent',
            'inspectionError': 0, 'nativeAuthority': False, 'pixelProof': False},
        'offlineReport': str(HERE / 'offline-report.json'),
        'retainedAttribution': str(BASE / 'raster-attribution-v7/retained-v7-prefix-attribution.json'),
        'inputs': inputs,
    }
    target.write_text(json.dumps(packet, indent=2) + '\n')
    report = {'manifest': str(target), 'manifestSHA256': sha(target), 'inputCount': len(inputs),
              'binarySHA256': sha(binary), 'fragmentSHA256': packet['fragmentSHA256'],
              'nativeLaunch': False, 'currentStageFrozen': True,
              'offline': json.loads((HERE / 'offline-report.json').read_text()),
              'pending': 'root source review and unchanged full native image campaign; no native grant assumed'}
    checkpoint.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'manifestSHA256': sha(target), 'checkpointSHA256': sha(checkpoint),
                      'binarySHA256': sha(binary), 'fragmentSHA256': packet['fragmentSHA256'],
                      'inputs': len(inputs)}))


if __name__ == '__main__':
    main()
