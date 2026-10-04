"""Validate declarations only; explicitly no transition/model acceptance."""
import hashlib
import json
import resource
import shutil
import subprocess
import time
from pathlib import Path

assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
root = Path(__file__).resolve().parents[1]
out = root / 'qa' / ('typecheck-' + str(time.time_ns()))
out.mkdir()
source = root / 'spec/constraints-sketch.qnt'
shutil.copy2(source, out / 'constraints-sketch.qnt')
tool = shutil.which('quint')
assert tool
command = [tool, 'typecheck', str(out / 'constraints-sketch.qnt')]
result = subprocess.run(command, capture_output=True, text=True, timeout=60)
(out / 'stdout').write_text(result.stdout)
(out / 'stderr').write_text(result.stderr)
report = dict(passed=result.returncode == 0, exitCode=result.returncode,
              command=command, sourceSHA256=hashlib.sha256(source.read_bytes()).hexdigest(),
              scope='Types and grouped state only; explicit approval pending; no logic, simulation, native or release acceptance',
              modelAcceptance=False, nativeAcceptance=False)
(out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(dict(passed=report['passed'], report=str(out / 'report.json'))))
raise SystemExit(result.returncode)
