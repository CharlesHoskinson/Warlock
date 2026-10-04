"""Explicit Quint scenarios, invariant sampling and negative model controls."""
import hashlib
import json
from pathlib import Path
import resource
import shutil
import subprocess
import time

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa' / ('model-' + str(time.time_ns()))
OUT.mkdir()
source = ROOT / 'spec/parent.qnt'
shutil.copy2(source, OUT / 'parent.qnt')
shutil.copy2(__file__, OUT / 'model.py')
names = ['stationaryScaleTest', 'restoreScaleTest', 'outputRelativeTest',
         'outputOriginChangesTest', 'unfocusedMotionTest', 'focusLeaveBlocksReplayTest',
         'stagedConfigureBlocksTest', 'ackAloneBlocksTest', 'staleCommitBlocksTest',
         'freshCommitAllowsTest', 'deviceRetirementBlocksTest', 'outputRetirementBlocksTest',
         'backendRetirementBlocksTest', 'supersedingWarpBlocksReplayTest',
         'unchangedLayoutNoReplayTest', 'unrelatedLayoutNoReplayTest',
         'clampedCoordinatesTest', 'disabledOutputBlocksTest', 'mirroredOutputBlocksTest']
report = {'passed': False, 'scope': 'Finite parent-coordinate event-loop contract; no native lifecycle or full-program refinement claim',
          'namedScenarios': names, 'commands': [], 'nativeAcceptance': False}


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(name, args, expected=0):
    cmd = [shutil.which('quint'), *args]
    p = subprocess.run(cmd, cwd=OUT, text=True, capture_output=True, timeout=180)
    (OUT / (name + '.stdout')).write_text(p.stdout)
    (OUT / (name + '.stderr')).write_text(p.stderr)
    report['commands'].append({'command': cmd, 'exitCode': p.returncode, 'expected': expected})
    print(name, p.returncode, flush=True)
    assert p.returncode == expected, p.stderr or p.stdout
    return p


try:
    run('version', ['--version'])
    run('typecheck', ['typecheck', 'parent.qnt'])
    run('named', ['test', 'parent.qnt', '--backend=typescript', '--match=^(' + '|'.join(names) + ')$',
                  '--out-itf=named-{test}-{seq}.itf.json', '--seed=36001', '--max-samples=1'])
    traces = list(OUT.glob('named-*.itf.json'))
    assert len(traces) == len(names)
    assert {p.name.split('-')[1] for p in traces} == set(names)
    run('invariants', ['run', 'parent.qnt', '--backend=typescript', '--invariants=safety',
                       '--max-samples=1000', '--max-steps=40', '--seed=36002', '--out-itf=sample-{seq}.itf.json'])
    text = source.read_text()
    mutants = [
        ('unfocused', 'st.backend and st.focus == o and', 'st.backend and true and', 'unfocusedMotionTest'),
        ('origin', 'px: v.x + v.width * st.nx / 4', 'px: v.width * st.nx / 4', 'outputRelativeTest'),
        ('superseding', '{...clear(s), px: x, py: y', '{...s, px: x, py: y', 'supersedingWarpBlocksReplayTest'),
    ]
    for name, before, after, test in mutants:
        assert text.count(before) == 1
        path = name + '.qnt'
        (OUT / path).write_text(text.replace(before, after))
        run(name + '-typecheck', ['typecheck', path])
        run(name + '-rejected', ['test', path, '--backend=typescript', '--match=^' + test + '$',
                                 '--max-samples=1', '--seed=36003'], expected=1)
    report.update(passed=True, sourceSHA256=digest(source), invariantSamples=1000, maxSteps=40,
                  executedNamedScenarios=len(names), mutantsRejected=len(mutants))
except Exception as error:
    report['error'] = repr(error)
report['artifacts'] = {str(p.relative_to(OUT)): digest(p) for p in OUT.rglob('*') if p.is_file()}
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'passed': report['passed'], 'report': str(OUT / 'report.json'), 'error': report.get('error')}))
raise SystemExit(not report['passed'])
