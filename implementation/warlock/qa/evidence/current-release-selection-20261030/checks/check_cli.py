"""Protected executable CLI refusal checks; no release build is started."""
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys

ROOT = Path('/home/charles/Warlock')
HERE = Path(__file__).resolve().parent
TARGET = ROOT/'implementation/warlock/qa/check-release-repro.py'

def main():
    sys.path.insert(0, str(ROOT/'window-integration-qa'))
    from qa_launch import require_qa_scope
    scope = require_qa_scope()
    assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    before = sha(TARGET)
    directories = set((ROOT/'implementation/warlock/qa/runs').iterdir())
    sample = HERE/'unselected-test-tuple.json'
    sample.write_text('{}\n')
    fifo = HERE/'unselected-pipe'
    os.mkfifo(fifo, 0o600)
    cases = [
        ('help', ['--help'], 0, '--native-tuple-sha256'),
        ('missing hash', ['--native-tuple', str(sample)], 2, 'Both --native-tuple'),
        ('missing path', ['--native-tuple-sha256', '0'*64], 2, 'Both --native-tuple'),
        ('relative path', ['--native-tuple', 'relative.json', '--native-tuple-sha256', '0'*64], 2, 'absolute path'),
        ('short hash', ['--native-tuple', str(sample), '--native-tuple-sha256', 'bad'], 2, 'lowercase SHA-256'),
        ('uppercase hash', ['--native-tuple', str(sample), '--native-tuple-sha256', 'A'*64], 2, 'lowercase SHA-256'),
        ('wrong actual digest', ['--native-tuple', str(sample), '--native-tuple-sha256', '0'*64], 2, 'does not match'),
        ('unreadable tuple', ['--native-tuple', str(HERE/'absent.json'), '--native-tuple-sha256', '0'*64], 2, 'regular file'),
        ('FIFO refused before read', ['--native-tuple', str(fifo), '--native-tuple-sha256', '0'*64], 2, 'regular file'),
        ('probe cannot claim tuple validation', ['--probe', '--native-tuple', str(sample), '--native-tuple-sha256', sha(sample)], 2, 'does not select or validate'),
        ('unknown argument', ['--unknown'], 2, 'unrecognized arguments'),
    ]
    report = dict(passed=False, scope=scope, sourceSHA256=before, checks=[],
                  nativeAcceptance=False, releaseAccepted=False,
                  limits='Only real CLI help/refusals. No valid tuple capture, namespace probe, compiler or isolated build is run.')
    for index, (name, args, expected, message) in enumerate(cases):
        command = ['/usr/bin/python3', '-B', str(TARGET), *args]
        result = subprocess.run(command, capture_output=True, timeout=20)
        for suffix, content in [('stdout', result.stdout), ('stderr', result.stderr)]:
            (HERE/(str(index)+'.'+suffix)).write_bytes(content)
        passed = result.returncode == expected and message in (result.stdout+result.stderr).decode()
        report['checks'].append(dict(name=name, passed=passed, command=command,
                                     exit=result.returncode, expectedExit=expected))
    report['checks'].append(dict(name='No run directories created on rejected/help arguments', passed=directories == set((ROOT/'implementation/warlock/qa/runs').iterdir())))
    report['checks'].append(dict(name='Executed source unchanged', passed=before == sha(TARGET)))
    report['passed'] = all(row['passed'] for row in report['checks'])
    (HERE/'cli-report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(passed=report['passed'], checks=len(report['checks']), report=str(HERE/'cli-report.json'))))
    return 0 if report['passed'] else 1
if __name__ == '__main__':
    sys.exit(main())
