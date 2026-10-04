"""Actual preserved parser: bounded raw integer must fail with typed refusal."""
import hashlib, importlib.util, json, resource, time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'qa' / ('characterization-' + str(time.time_ns()))
OUT.mkdir()
path = ROOT / 'original/journal.py'
spec = importlib.util.spec_from_file_location('preserved_journal', path)
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)
raw = (ROOT / 'input.jsonl').read_bytes()
control = raw.replace(b'9' * 5000, b'1')
report = {'passed': False, 'consumerAccepted': False, 'nativeAcceptance': False}
try:
    assert len(parser.parse(control, pid=1234, started='77')) == 1
    try:
        parser.parse(raw, pid=1234, started='77')
    except Exception as error:
        report.update(exceptionType=type(error).__name__, typedRefused=isinstance(error, parser.Refused),
                      reason=str(error), unsafeWitnessConfirmed=type(error) is ValueError)
    else:
        report['unsafeWitnessConfirmed'] = False
    assert report['unsafeWitnessConfirmed'] is True and report['typedRefused'] is False
    report['passed'] = True
finally:
    report['inputs'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (path, ROOT / 'input.jsonl', Path(__file__))}
    (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'passed': report['passed'], 'report': str(OUT / 'report.json')}))
