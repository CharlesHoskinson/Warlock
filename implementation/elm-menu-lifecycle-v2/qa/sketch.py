"""Protected types-only check; no transition logic before explicit approval."""
import hashlib
import json
import resource
import shutil
import subprocess
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1)
OUT = ROOT/'qa'/('sketch-'+str(time.time_ns()))
OUT.mkdir()
files = [ROOT/'spec/menu-sketch.qnt', ROOT/'spec/INTAKE.md', Path(__file__)]
inputs = {}
for path in files:
    relative = str(path.relative_to(ROOT))
    inputs[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    destination = OUT/'inputs'/relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
quint = '/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
command = [quint, 'typecheck', 'menu-sketch.qnt']
process = subprocess.run(command, cwd=OUT/'inputs/spec', capture_output=True, text=True, timeout=60)
(OUT/'stdout').write_text(process.stdout)
(OUT/'stderr').write_text(process.stderr)
unchanged = all(hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == digest for relative,digest in inputs.items())
report = {'passed': process.returncode == 0 and unchanged, 'inputs': inputs,
          'command': command, 'exitCode': process.returncode,
          'scope': 'Types only; proposed model awaits approval'}
(OUT/'report.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({'passed':report['passed'], 'report':str(OUT/'report.json')}))
raise SystemExit(not report['passed'])
