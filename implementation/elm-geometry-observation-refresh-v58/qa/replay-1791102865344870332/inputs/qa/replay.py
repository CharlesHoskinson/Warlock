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
         ROOT / 'qa/menu.cjs', ROOT / 'qa/geometry.cjs', ROOT / 'qa/refresh.cjs', ROOT / 'qa/geometry-fixtures.json', ROOT / 'qa/fixtures.json', ROOT / 'qa/replay.py', ROOT / 'qa/upstream.json', ROOT / 'qa/INTEGRATION.md']
for optional in ['upstream.json','qa/mutations.py','qa/freeze.py','qa/scenario-oracle.json','qa/output-scenario-oracle.json']:
    if (ROOT / optional).exists(): files.append(ROOT / optional)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
report = {'passed':False, 'scope':'Production Visible surface controller/MenuBridge plus existing Shell/Effects compiled CPU behavior; no native GUI acceptance',
          'inputs':{str(path.relative_to(ROOT)):sha(path) for path in files}, 'commands':[]}
for path in files:
    destination = INPUT / path.relative_to(ROOT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
try:
    upstream=json.loads((ROOT/'qa/upstream.json').read_text())
    for relative,digest in upstream['files'].items(): assert sha(Path(upstream['parent'])/relative)==digest,relative
    for relative in upstream['unchangedOriginalOracles']: assert sha(ROOT/relative)==upstream['files'][relative],relative
    commands = [
        ('compile', ['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/MenuSurfaceReplay.elm','--output='+str(OUT / 'replay.js')]),
        ('checks', ['node',str(INPUT / 'qa/menu.cjs'),str(OUT / 'replay.js'),str(INPUT / 'qa/fixtures.json'),str(OUT / 'checks.json')]),
        ('geometry-checks', ['node',str(INPUT / 'qa/geometry.cjs'),str(OUT / 'replay.js'),str(INPUT / 'qa/fixtures.json'),str(INPUT / 'qa/geometry-fixtures.json'),str(OUT / 'geometry-checks.json')]),
        ('refresh-checks', ['node',str(INPUT / 'qa/refresh.cjs'),str(OUT / 'replay.js'),str(INPUT / 'qa/fixtures.json'),str(INPUT / 'qa/geometry-fixtures.json'),str(OUT / 'refresh-checks.json')]),
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
    geometry=json.loads((OUT / 'geometry-checks.json').read_text());assert geometry['passed'];report['geometryChecks']=geometry
    refresh=json.loads((OUT / 'refresh-checks.json').read_text());assert refresh['passed'];report['refreshChecks']=refresh
    for relative,digest in report['inputs'].items(): assert sha(ROOT / relative) == digest, relative
except Exception as error:
    report['passed'] = False
    report['error'] = repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}
(OUT / 'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(OUT / 'report.json')
raise SystemExit(not report['passed'])
