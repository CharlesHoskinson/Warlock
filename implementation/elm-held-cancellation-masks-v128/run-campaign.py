"""Serial native dispatch only; each case enters the unchanged protected launcher."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
LOOP = REPO / 'implementation/elm-build-loop-v1/loop.py'
for mask in range(1, 8):
    case = ROOT / ('mask-' + str(mask))
    result = subprocess.run(['/usr/bin/python3', '-B', str(LOOP), 'native',
                             '--runner', str(case / 'qa/native.py')], cwd=REPO)
    if result.returncode:
        sys.exit(result.returncode)
    report = sorted((case / 'qa').glob('native-*/report.json'))[-1]
    data = json.loads(report.read_text())
    assert data['passed'] and data['cleanupPassed'] and data['heldMask'] == mask
    print(json.dumps({'mask': mask, 'passed': True, 'report': str(report)}), flush=True)
