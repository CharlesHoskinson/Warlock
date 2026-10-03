"""Append-only qualification of compiled Elm scene admission and Quint model."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import time

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa' / ('run-' + str(time.time_ns()))
OUT.mkdir()
inputs = {}
for path in [ROOT / 'elm.json', *sorted((ROOT / 'src').glob('*.elm')),
             *sorted((ROOT / 'qa').glob('*.py')), *sorted((ROOT / 'qa').glob('*.cjs')),
             *sorted((ROOT / 'spec').glob('*.qnt'))]:
    relative = path.relative_to(ROOT)
    destination = OUT / 'inputs' / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
    inputs[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
records = []
report = {'passed': False, 'inputs': inputs,
          'observedUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'scope': 'CPU admission prototype only; not native canonical scene, pixels, hit dispatch or focus acceptance'}

def run(name, command, env=None):
    process = subprocess.run(command, cwd=OUT / 'inputs', env=env,
                             capture_output=True, text=True, timeout=180)
    (OUT / (name + '.stdout')).write_text(process.stdout)
    (OUT / (name + '.stderr')).write_text(process.stderr)
    records.append({'name': name, 'command': command, 'exitCode': process.returncode})
    print(name, process.returncode, flush=True)
    if process.returncode:
        raise RuntimeError(process.stderr or process.stdout)

try:
    run('elm-version', ['npm', 'exec', '--yes', '--package=elm@0.19.2-0', '--', 'elm', '--version'])
    run('compile', ['npm', 'exec', '--yes', '--package=elm@0.19.2-0', '--', 'elm', 'make', 'src/Replay.elm', '--output=' + str(OUT / 'replay.js')])
    run('elm-admission', ['node', 'qa/check.cjs'], dict(os.environ, ELM_REPLAY=str(OUT / 'replay.js'), ELM_REPORT=str(OUT / 'elm-report.json')))
    quint = '/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
    run('quint-version', [quint, '--version'])
    run('quint-typecheck', [quint, 'typecheck', 'spec/scene.qnt'])
    traces = OUT / 'traces'
    traces.mkdir()
    run('quint-tests', [quint, 'test', 'spec/scene.qnt', '--match', 'Test$', '--seed', '610601', '--max-samples', '1', '--out-itf', str(traces / 'named-{test}-{seq}.itf.json')])
    run('quint-invariants', [quint, 'run', 'spec/scene.qnt', '--invariants', 'safety', '--seed', '610602', '--max-samples', '1000', '--max-steps', '40', '--out-itf', str(traces / 'sample-{seq}.itf.json')])
    run('quint-elm-conformance', ['node', 'qa/check.cjs'], dict(os.environ, ELM_REPLAY=str(OUT / 'replay.js'), ELM_REPORT=str(OUT / 'conformance-report.json'), QUINT_TRACES=str(traces)))
    mutations = [
        ('owner-exclusion-removed', 'Just parent -> find candidate parent |> Maybe.map (eligible candidate) |> Maybe.withDefault False', 'Just parent -> True', 'flags-'),
        ('modal-block-removed', 'not focusEligible || modalBlocksFocus', 'not focusEligible', 'modal-blocked-parent')]
    for name, before, after, witness in mutations:
        folder = OUT / name
        shutil.copytree(OUT / 'inputs', folder)
        source = folder / 'src/Scene.elm'
        original = source.read_text()
        assert original.count(before) == 1
        source.write_text(original.replace(before, after))
        process = subprocess.run(['npm', 'exec', '--yes', '--package=elm@0.19.2-0', '--', 'elm', 'make', 'src/Replay.elm', '--output=' + str(folder / 'replay.js')], cwd=folder, capture_output=True, text=True, timeout=180)
        (OUT / (name + '-derivative-compile.stdout')).write_text(process.stdout)
        (OUT / (name + '-derivative-compile.stderr')).write_text(process.stderr)
        assert process.returncode == 0, process.stderr
        records.append({'name': name + '-derivative-compile', 'exitCode': process.returncode})
        process = subprocess.run(['node', str(folder / 'qa/check.cjs')], cwd=folder,
            env=dict(os.environ, ELM_REPLAY=str(folder / 'replay.js'), ELM_REPORT=str(folder / 'unexpected-pass.json')),
            capture_output=True, text=True, timeout=180)
        (OUT / (name + '.stdout')).write_text(process.stdout)
        (OUT / (name + '.stderr')).write_text(process.stderr)
        assert process.returncode == 1 and 'AssertionError' in process.stderr and witness in process.stderr, process.stderr
        records.append({'name': name, 'exitCode': process.returncode, 'expectedAssertionFailure': witness})
    report['passed'] = json.loads((OUT / 'elm-report.json').read_text())['passed']
except Exception as error:
    report['error'] = str(error)
report['commands'] = records
report['artifacts'] = {str(path.relative_to(OUT)): hashlib.sha256(path.read_bytes()).hexdigest()
                       for path in sorted(OUT.rglob('*')) if path.is_file()}
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(str(OUT / 'report.json'), flush=True)
raise SystemExit(not report['passed'])
