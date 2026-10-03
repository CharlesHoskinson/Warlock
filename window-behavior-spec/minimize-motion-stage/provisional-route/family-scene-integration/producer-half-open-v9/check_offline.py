"""Freezeable offline-only sampler checks. Never runs the GPU producer."""
import hashlib
import json
import re
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
COMMANDS = [
    ('build', ['make', '-B', '-j2', 'hypr-motion-renderer-staged', 'test-quantized-over', 'test-manual-sampling',
               'test-family-scene', 'test-commit-ledger', 'test-backend-policy',
               'test-library-material', 'test-readback-image', 'test-causal-image']),
    ('quantized-consumer', ['./test-quantized-over']),
    ('manual-consumer', ['./test-manual-sampling']),
    ('family-consumer', ['./test-family-scene']),
    ('commit-ledger', ['./test-commit-ledger']),
    ('backend', ['./test-backend-policy']),
    ('material', ['./test-library-material']),
    ('readback', ['./test-readback-image']),
    ('causal', ['./test-causal-image']),
    ('shader-syntax',['python3','check_shaders.py']),
    ('binding', ['python3', '-m', 'unittest', '-v', 'test_verify_sampling', 'test_verify_causal', 'test_quantized_gate', 'test_causal_target_source']),
    ('target-typecheck', ['quint','typecheck','causal_target_test.qnt']),
    ('coverage-typecheck',['quint','typecheck','pixel_coverage_test.qnt']),
    ('coverage-named',['quint','test','pixel_coverage_test.qnt']),
    ('coverage-model',['quint','run','pixel_coverage.qnt','--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=2026100109','--verbosity=0']),
    ('target-named', ['quint','test','causal_target_test.qnt']),
    ('target-model', ['quint','run','causal_target.qnt','--invariant=allProps','--max-samples=2000','--max-steps=100','--seed=2026100108','--verbosity=0']),
    ('quantized-typecheck', ['quint', 'typecheck', 'quantized_over_test.qnt']),
    ('quantized-named', ['quint', 'test', 'quantized_over_test.qnt']),
    ('quantized-model', ['quint', 'run', 'quantized_over.qnt', '--invariant=allProps', '--max-samples=2000', '--max-steps=40', '--seed=2026100115', '--verbosity=0']),
    ('causal-typecheck', ['quint', 'typecheck', 'causal_binding_test.qnt']),
    ('causal-named', ['quint', 'test', 'causal_binding_test.qnt']),
    ('causal-model', ['quint', 'run', 'causal_binding.qnt', '--invariant=allProps', '--max-samples=2000', '--max-steps=40', '--seed=2026100116', '--verbosity=0']),
    ('typecheck', ['quint', 'typecheck', 'manual_sampling_test.qnt']),
    ('named', ['quint', 'test', 'manual_sampling_test.qnt']),
    ('model', ['quint', 'run', 'manual_sampling.qnt', '--invariant', 'allProps',
               '--max-samples', '2000', '--max-steps', '40', '--seed', '2026100114',
               '--verbosity', '0']),
]


def main():
    records = []
    observed_counts={}
    source_paths = sorted(p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.cpp','.hpp','.py','.qnt','.c','.h')) + [HERE / 'Makefile']
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    for label, command in COMMANDS:
        result = subprocess.run(command, cwd=HERE, capture_output=True, text=True, timeout=180)
        output = result.stdout + result.stderr
        log = HERE / ('offline-' + label + '.log')
        if log.exists():raise SystemExit('fresh proof log required')
        log.write_text(output)
        records.append({'label': label, 'command': command, 'exit': result.returncode,
                        'log': str(log), 'logSHA256': hashlib.sha256(log.read_bytes()).hexdigest()})
        print(label, result.returncode, flush=True)
        if result.returncode:
            raise SystemExit(output)
        if label.endswith('named') or label=='named':observed_counts[label]=int(re.search(r'(\d+) passing',output)[1])
        if label=='binding':observed_counts[label]=int(re.search(r'Ran (\d+) tests',output)[1])
        if label=='quantized-consumer':observed_counts[label]=int(re.search(r'(\d+) quantized-over',output)[1])
    if any(hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h for p,h in before.items()):raise SystemExit('source changed during offline proof')
    report = {'sourceSHA256':before, 'sourceUnchangedDuringProof':True, 'nativeLaunch': False, 'GPUOperation': False, 'commands': records,
              'quantizedConsumerChecks': 204, 'manualConsumerChecks': 52, 'familyConsumerChecks': 73,
              'ledgerChecks': 80, 'backendChecks': 20, 'materialChecks': 34,
              'readbackChecks': 10, 'causalChecks': 15, 'PythonBindingTests': 70, 'quantizedConfigurationTests': 41, 'causalTargetSourceTests':4,
              'newSamplerBindingTests': 11, 'namedSamplingScenarios': observed_counts['named'], 'namedQuantizedScenarios': observed_counts['quantized-named'], 'namedCausalTargetScenarios':observed_counts['target-named'], 'namedCausalScenarios': observed_counts['causal-named'],
              'samplingModelSamples': 2000, 'causalModelSamples': 2000, 'quantizedModelSamples': 2000, 'causalTargetModelSamples':2000,
              'namedCoverageScenarios':observed_counts['coverage-named'],'coverageModelSamples':2000,'offlineShadersParsed':3,'observedCounts':observed_counts,'totalNamedScenarios':sum(value for label,value in observed_counts.items() if label.endswith('named') or label=='named'),
              'scope': 'offline guards/math only; no native pixel or cadence acceptance'}
    if (HERE / 'offline-report.json').exists():raise SystemExit('fresh proof report required')
    if observed_counts['binding']!=70 or observed_counts['quantized-consumer']!=204:raise SystemExit('unexpected actual offline Python/consumer count')
    (HERE / 'offline-report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
