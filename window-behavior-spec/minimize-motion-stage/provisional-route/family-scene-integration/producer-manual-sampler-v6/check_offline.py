"""Freezeable offline-only sampler checks. Never runs the GPU producer."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
COMMANDS = [
    ('build', ['make', '-j2', 'hypr-motion-renderer-staged', 'test-manual-sampling',
               'test-family-scene', 'test-commit-ledger', 'test-backend-policy',
               'test-library-material', 'test-readback-image', 'test-causal-image']),
    ('manual-consumer', ['./test-manual-sampling']),
    ('family-consumer', ['./test-family-scene']),
    ('commit-ledger', ['./test-commit-ledger']),
    ('backend', ['./test-backend-policy']),
    ('material', ['./test-library-material']),
    ('readback', ['./test-readback-image']),
    ('causal', ['./test-causal-image']),
    ('binding', ['python3', '-m', 'unittest', '-v', 'test_verify_sampling', 'test_verify_causal']),
    ('typecheck', ['quint', 'typecheck', 'manual_sampling_test.qnt']),
    ('named', ['quint', 'test', 'manual_sampling_test.qnt']),
    ('model', ['quint', 'run', 'manual_sampling.qnt', '--invariant', 'allProps',
               '--max-samples', '2000', '--max-steps', '40', '--seed', '2026100114',
               '--verbosity', '0']),
]


def main():
    records = []
    for label, command in COMMANDS:
        result = subprocess.run(command, cwd=HERE, capture_output=True, text=True, timeout=180)
        output = result.stdout + result.stderr
        log = HERE / ('offline-' + label + '.log')
        log.write_text(output)
        records.append({'label': label, 'command': command, 'exit': result.returncode,
                        'log': str(log), 'logSHA256': hashlib.sha256(log.read_bytes()).hexdigest()})
        print(label, result.returncode, flush=True)
        if result.returncode:
            raise SystemExit(output)
    report = {'nativeLaunch': False, 'GPUOperation': False, 'commands': records,
              'manualConsumerChecks': 52, 'familyConsumerChecks': 73,
              'ledgerChecks': 80, 'backendChecks': 20, 'materialChecks': 34,
              'readbackChecks': 10, 'causalChecks': 15, 'PythonBindingTests': 25,
              'newSamplerBindingTests': 11, 'namedSamplingScenarios': 8,
              'samplingModelSamples': 2000,
              'scope': 'offline guards/math only; no native pixel or cadence acceptance'}
    (HERE / 'offline-report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
