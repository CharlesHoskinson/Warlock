"""Apply independent safety faults to copied Elm, compile, and require rejection.
No JavaScript state-machine replacement; failed mutant traces remain evidence.
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
OUT = ROOT / 'qa' / ('mutations-' + str(time.time_ns()))
OUT.mkdir()
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
report = {'passed':False, 'scope':'Applied compiled Elm safety mutants detected by external fixtures; no native acceptance', 'mutants':[]}
try:
    baseline_path = sorted((ROOT / 'qa').glob('replay-*/report.json'))[-1]
    baseline = json.loads(baseline_path.read_text())
    assert baseline['passed'] and not baseline.get('error')
    report['baselineReport'] = {'path':str(baseline_path.relative_to(ROOT)), 'sha256':sha(baseline_path)}
    report['inputs'] = {**baseline['inputs'], 'qa/mutations.py':sha(ROOT / 'qa/mutations.py')}
    for relative, digest in report['inputs'].items(): assert sha(ROOT / relative) == digest, relative
    source = (ROOT / 'src/Menu.elm').read_text()
    refusal = '( Model { state | menu = Just { menu | status = Refused "Outstanding operation limit reached; reconcile existing requests." } }, [] )'
    definitions = [
        ('ignore-receipt-binding', 'entry.id == intent && entry.binding == receiptBinding',
         'entry.id == intent', 1, 'wrong-original-binding-receipt-cannot-clear-pending'),
        ('evict-unresolved-at-capacity', refusal,
         refusal.replace('state | menu', 'state | outstanding = List.take (maxOutstanding - 1) state.outstanding, menu'),
         1, '64-ledger-budget-keeps-all-unknown-and-definitive-one-frees-slot'),
        ('reset-retirement-ledger', '( Model { state | exhausted = True, menu = Nothing }, [] )',
         '( Model { state | exhausted = False, invalidated = [], retiredOutputs = [], menu = Nothing }, [] )',
         2, '128-tombstones-dedup-safe-129th-exhausts-retaining-late-receipt')]
    for name, original, replacement, count, witness in definitions:
        assert source.count(original) == count, name + ': mutation site changed'
        directory = OUT / name
        directory.mkdir()
        for relative in baseline['inputs']:
            destination = directory / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, destination)
        mutated = source.replace(original, replacement)
        (directory / 'src/Menu.elm').write_text(mutated)
        commands = [
            ('compile', ['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/Replay.elm','--output='+str(directory / 'replay.js')]),
            ('checks', ['node',str(directory / 'qa/replay.cjs'),str(directory / 'replay.js'),str(directory / 'qa/fixtures.json'),str(directory / 'checks.json')])]
        outcome = {'id':name,'passed':False,'witness':witness,'originalMenuSHA256':sha(ROOT / 'src/Menu.elm'),
                   'mutatedMenuSHA256':sha(directory / 'src/Menu.elm'),'commands':[]}
        report['mutants'].append(outcome)
        for stage, command in commands:
            process = subprocess.run(command, cwd=directory, text=True, capture_output=True, timeout=180)
            (directory / (stage+'.stdout')).write_text(process.stdout)
            (directory / (stage+'.stderr')).write_text(process.stderr)
            outcome['commands'].append({'command':command,'exitCode':process.returncode})
            if stage == 'compile': assert process.returncode == 0, process.stdout + process.stderr
            else:
                assert process.returncode != 0 and witness in process.stderr, process.stderr
                outcome.update(passed=True, detected=True)
        print(name, 'DETECTED', flush=True)
    for relative,digest in report['inputs'].items(): assert sha(ROOT / relative) == digest, relative
    report['passed'] = all(mutant['passed'] for mutant in report['mutants'])
except Exception as error: report['error'] = repr(error)
report['artifacts'] = {str(path.relative_to(OUT)):sha(path) for path in OUT.rglob('*') if path.is_file()}
(OUT / 'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(OUT / 'report.json')
raise SystemExit(not report['passed'])
