"""Protected opt-in store regression; never enables the daemon or native actions."""
import hashlib
import json
import pathlib
import subprocess
import sys
import time
from qa_launch import require_qa_scope

scope = require_qa_scope()
ROOT = pathlib.Path(__file__).resolve().parents[1]
CASES = ROOT / 'qa/cancellation-store-cases'
OUT = ROOT / 'qa/runs' / ('cancellation-store-' + str(time.time_ns()))
OUT.mkdir(parents=True)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

paths = [ROOT / 'adapter' / name for name in [
    'cancellation_ledger.py', 'cancellation_legacy.py', 'recovery_store.py',
    'cancellation_endpoint.py', 'effect_endpoint.py', 'endpoint.py',
    'recovery_journal.py', 'durable_ledger.py', 'admission_ledger.py',
    'retirement_ledger.py', 'delivery_ledger.py', 'workspace_navigation.py',
    'reconciliation.py', 'grant_endpoint.py']]
paths += sorted(CASES.glob('*.py')) + [pathlib.Path(__file__)]
inputs = {str(p.relative_to(ROOT)): sha(p) for p in paths}
report = {'passed': False, 'scope': scope, 'inputs': inputs, 'commands': [],
          'nativeAcceptance': False, 'originalAcceptance': False,
          'completeRuntimeClosureClaimed': False,
          'limits': 'Actual opt-in store with filesystem faults, exact capacity boundaries and strict native-response doubles; daemon/C/Elm consumers disabled. No actual native transport, all64-slot, power-loss or release proof.'}
commands = [('base', []), ('legacy_restart', ['--expect-fixed']),
            ('typed_restart', []), ('provenance', ['--expect-fixed']),
            ('provenance_positive', []), ('faults', []), ('capacity', []),
            ('legacy_isolation', []), ('namespace_ownership', [])]
try:
    for name, extra in commands:
        args = [sys.executable, '-B', str(CASES / (name + '.py')), *extra]
        result = subprocess.run(args, capture_output=True, timeout=60)
        (OUT / (name + '.stdout')).write_bytes(result.stdout)
        (OUT / (name + '.stderr')).write_bytes(result.stderr)
        command = {'name': name, 'argv': args, 'exitCode': result.returncode,
                   'stdoutSHA256': sha(OUT / (name + '.stdout')),
                   'stderrSHA256': sha(OUT / (name + '.stderr'))}
        report['commands'].append(command)
        if result.returncode:
            raise RuntimeError(name + ' failed')
        outcome = json.loads(result.stdout)
        if outcome.get('passed') is not True:
            raise RuntimeError(name + ' did not report passing assertions')
        command['observations'] = outcome
    for path in paths:
        if sha(path) != inputs[str(path.relative_to(ROOT))]:
            raise RuntimeError('Input changed during run: ' + str(path))
    report['passed'] = True
except Exception as error:
    report['error'] = repr(error)
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'passed': report['passed'], 'report': str(OUT / 'report.json'),
                  'error': report.get('error')}))
sys.exit(0 if report['passed'] else 1)
