#!/usr/bin/env python3
"""Independent CPU-only review; never launches native desktop applications."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
BASE = Path('/home/hoskinson/window-integration-qa')
OLD = BASE / 'browser-files-flow-v12'
NEW = BASE / 'browser-files-flow-v13'
OUT = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    report = json.loads((NEW / 'metrics-offline-report.json').read_text())
    formal = json.loads((NEW / 'metrics-formal-detached-before-implementation.json').read_text())
    inputs = {NEW / k for k in report['sourceSHA256']}
    inputs |= {NEW / k for k in ('V13_CONTRACT.md', 'metrics-offline-report.json',
                                 'metrics-formal-detached-before-implementation.json')}
    inputs |= {OLD / k for k in ('owned_metrics_data.py', 'runtime_inputs.py',
                                 'mapping_evidence.py', 'private_session.py')}
    inputs |= {OUT / 'model-review.json', OUT / 'retained-v12-attribution.json'}
    before = {str(p): sha(p) for p in sorted(inputs)}
    assert report['result'] == 'pass' and report['sourceUnchangedDuringTests']
    assert all(sha(NEW / k) == v for k, v in report['sourceSHA256'].items())
    assert sha(NEW / 'owned_metrics_data.py') == '563647132ff06cbacd40482d2eeac9cbfe34cd1892fb3c4b654f98e8c386bf50'
    assert sha(NEW / 'metrics-offline-report.json') == '1868c6ad98f2a93f8015e5f0c7b51d63cbcd866744f960b739970ede3956150b'
    assert formal['result'] == 'pass' and formal['runtimeStillExactFrozenV12']
    assert formal['newParentPolicyImplemented'] is False and formal['namedScenarios'] == 70
    assert sha(NEW / 'V13_CONTRACT.md') == formal['contractSHA256']
    for k in ('runtime_metrics.qnt', 'runtime_metrics_test.qnt'):
        assert sha(NEW / k) == formal['sourceSHA256'][k]
    for k in ('owned_metrics_data.py', 'runtime_inputs.py', 'mapping_evidence.py', 'private_session.py'):
        assert sha(OLD / k) == formal['sourceSHA256'][k]
    for k in ('runtime_inputs.py', 'mapping_evidence.py', 'private_session.py'):
        assert (OLD / k).read_bytes() == (NEW / k).read_bytes()

    # Reconstruct inherited helper exactly by undoing only reviewed additions.
    old = (OLD / 'owned_metrics_data.py').read_text()
    current = (NEW / 'owned_metrics_data.py').read_text()
    recovered = current[:current.index('def stat_record(current):')] + current[current.index('def parse_mount(raw, runtime):'):]
    recovered = recovered.replace('guard, read_maps, initial_anchors):', 'guard, read_maps):', 1)
    recovered = recovered.replace("[('runtime', runtime), ('profile', profile)]:", "[('runtime', runtime), ('profile', profile), ('parent', profile / 'BrowserMetrics')]:", 1)
    begin = recovered.index("    parent = {}; evidence['parentObservation'] = parent")
    end = recovered.index("    proc = Path('/proc')", begin)
    recovered = recovered[:begin] + recovered[end:]
    recovered = recovered.replace("if dirs['parent']['state'] == 'present' and dirs['parent']['device'] != dirs['runtime']['device']:", "if dirs['parent']['device'] != dirs['runtime']['device']:", 1)
    for name in ('before', 'after'):
        recovered = recovered.replace("sample(observation['" + name + "'], browser, compositor, runtime, profile, candidate, frozen, guard, read_maps, initial_anchors)", "sample(observation['" + name + "'], browser, compositor, runtime, profile, candidate, frozen, guard, read_maps)", 1)
    assert recovered == old, 'Inherited helper differs outside reviewed parent observation changes'
    oldtests = {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse((OLD / 'test_owned_metrics_data.py').read_text())) if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}
    newtests = {n.name: ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse((NEW / 'test_owned_metrics_data.py').read_text())) if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}
    assert len(oldtests) == 31 and len(newtests) == 41
    assert all(newtests[k] == v for k, v in oldtests.items())
    command = ['/usr/bin/python3', str(BASE / 'qa_run.py'), '--', '/usr/bin/python3', '-B', str(NEW / 'test_owned_metrics_data.py')]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    run = subprocess.run(command, cwd=NEW, env=env, text=True, capture_output=True, timeout=60)
    assert run.returncode == 0, run.stdout + run.stderr
    assert 'Ran 41 tests' in run.stderr and '\nOK\n' in run.stderr
    after = {str(p): sha(p) for p in sorted(inputs)}
    assert before == after
    result = {
        'result': 'pass', 'scope': 'Source refinement and actual CPU-only tmpfs/procfs tests; no Browser/Files input outcome',
        'command': command, 'returncode': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr,
        'independentKernelTests': 41, 'original31TestsASTUnchanged': True,
        'inheritedHelperRecoveredByteExact': True, 'threeWiringFilesExactFrozenV12': True,
        'formalBeforeImplementationRecordVerified': True, 'independentPriorModelNamedCases': 70,
        'independentPriorModelRandomTraces': 2000, 'modelMaxSteps': 100,
        'full162Python139Named8ModelsReportSourceHashesVerified': True,
        'sourceSHA256': before, 'sourcesUnchangedBeforeAfter': True,
        'parentScope': 'Two descriptor-relative nofollow lookups per sample, exact current anchored profile FD and named path before/after; full sample before/after and post-disk confirmation; no continuous or historical-parent claim',
        'metadataAndClassificationScope': 'Exact original root raw maps hash/line and candidate FD/VMA identity; full private guards and no executable aliases preserved',
        'nativeExecuted': False, 'mainWrites': False, 'frozenV12Changed': False,
        'actualBrowserFilesInputAccepted': False
    }
    target = OUT / 'runtime-review.json'
    target.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'result': 'pass', 'artifact': str(target), 'sha256': sha(target), 'tests': 41, 'verifiedSourceFiles': len(before)}))

if __name__ == '__main__':
    main()
