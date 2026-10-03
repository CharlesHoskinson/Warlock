"""Protected CPU QA: freeze source and original native packet report, compile, replay."""
import hashlib
import json
import resource
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
OUT = ROOT / 'qa' / ('elm-' + str(time.time_ns()))
INPUT = OUT / 'inputs'
INPUT.mkdir(parents=True)
NATIVE = ROOT.parent / 'elm-surface-facts-v20' / 'qa' / 'native-1791066071820282438' / 'report.json'
paths = [ROOT / 'elm.json', ROOT / 'qa/elm.cjs', ROOT / 'qa/elm.py', *sorted((ROOT / 'src').glob('*.elm'))]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
report = {'passed': False, 'scope': 'CPU typed diagnostic validation only; historical native evidence replayed, no new native run',
          'mainDesktopActions': False, 'inputs': {str(path.relative_to(ROOT)): sha(path) for path in paths},
          'nativeReportSource': str(NATIVE), 'nativeReportSHA256': sha(NATIVE), 'commands': []}
try:
    for name in ['src', 'elm.json']:
        source = ROOT / name
        if source.is_dir():
            shutil.copytree(source, INPUT / name)
        else:
            shutil.copy2(source, INPUT / name)
    for name in ['elm.cjs', 'elm.py']:
        shutil.copy2(ROOT / 'qa' / name, INPUT / name)
    frozen_native = INPUT / 'native-report.json'
    shutil.copy2(NATIVE, frozen_native)
    native = json.loads(frozen_native.read_text())
    assert native['passed'] and native['cleanupPassed'] and not native.get('error')
    assert len(native['captures']) + len(native['identityTracePackets']) == 18
    assert sha(frozen_native) == report['nativeReportSHA256']
    commands = [('compile', ['npm', 'exec', '--yes', '--package=elm@0.19.2-0', '--', 'elm', 'make', 'src/Replay.elm', '--output=' + str(OUT / 'replay.js')]),
                ('checks', ['node', str(INPUT / 'elm.cjs'), str(OUT / 'replay.js'), str(frozen_native), str(OUT / 'checks.json')])]
    for name, command in commands:
        process = subprocess.run(command, cwd=INPUT, capture_output=True, text=True, timeout=180)
        (OUT / (name + '.stdout')).write_text(process.stdout)
        (OUT / (name + '.stderr')).write_text(process.stderr)
        report['commands'].append({'command': command, 'exitCode': process.returncode})
        print(name, process.returncode, flush=True)
        assert process.returncode == 0, process.stderr
    checks = json.loads((OUT / 'checks.json').read_text())
    assert checks['passed']
    assert all(sha(path) == report['inputs'][str(path.relative_to(ROOT))] for path in paths), 'Source changed during QA'
    assert sha(NATIVE) == report['nativeReportSHA256'], 'Original native report changed'
    report.update(passed=True, checks=checks['checks'], nativeCaptures=checks['nativeCaptures'], checksSHA256=sha(OUT / 'checks.json'), replaySHA256=sha(OUT / 'replay.js'))
except Exception as error:
    report['error'] = repr(error)
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(OUT / 'report.json', flush=True)
raise SystemExit(not report['passed'])
