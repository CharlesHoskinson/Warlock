"""Compile production bridge/taskbar/apps and replay actual engine-generated effects.
Protected CPU-only QA. Frozen inputs and failed diagnostics are preserved.
"""
import hashlib
import json
import resource
import shutil
import subprocess
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
OUT = ROOT / 'qa' / ('replay-' + str(time.time_ns()))
OUT.mkdir()
INPUT = OUT / 'inputs'
INPUT.mkdir()
files = [ROOT / 'elm.json', *sorted((ROOT / 'src').glob('*.elm')),
         ROOT / 'qa/replay.cjs', ROOT / 'qa/fixtures.json', ROOT / 'qa/replay.py']
for optional in ['upstream.json','qa/mutations.py','qa/freeze.py']:
    if (ROOT / optional).exists(): files.append(ROOT / optional)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
report = {'passed':False, 'scope':'Production TaskbarShell/MenuBridge/NativeProvider plus existing Shell/Effects compiled CPU behavior; no native GUI acceptance',
          'inputs':{str(path.relative_to(ROOT)):sha(path) for path in files}, 'commands':[]}
for path in files:
    destination = INPUT / path.relative_to(ROOT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
try:
    commands = [
        ('compile', ['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/BridgeReplay.elm','--output='+str(OUT / 'replay.js')]),
        ('checks', ['node',str(INPUT / 'qa/replay.cjs'),str(OUT / 'replay.js'),str(INPUT / 'qa/fixtures.json'),str(OUT / 'checks.json')]),
        ('main-compile', ['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Main.elm','--output='+str(OUT / 'main.js')]),
        ('popup-compile', ['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Popup.elm','--output='+str(OUT / 'popup.js')])]
    for name, command in commands:
        process = subprocess.run(command, cwd=INPUT, capture_output=True, text=True, timeout=180)
        (OUT / (name+'.stdout')).write_text(process.stdout)
        (OUT / (name+'.stderr')).write_text(process.stderr)
        report['commands'].append({'command':command,'exitCode':process.returncode})
        print(name,process.returncode,flush=True)
        assert process.returncode == 0, process.stdout + process.stderr
    checks = json.loads((OUT / 'checks.json').read_text())
    assert checks['passed']
    report.update(checks)
    for relative,digest in report['inputs'].items(): assert sha(ROOT / relative) == digest, relative
except Exception as error:
    report['passed'] = False
    report['error'] = repr(error)
(OUT / 'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(OUT / 'report.json')
raise SystemExit(not report['passed'])
