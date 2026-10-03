from pathlib import Path
import hashlib, json, os, subprocess, sys
sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
B = Path(__file__).resolve().parent
O = B / 'formal-before-runtime-v1'
O.mkdir(mode=0o700)
checks = []
sources = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in B.iterdir() if p.is_file()}
for label, cmd in [('typecheck', ['quint', 'typecheck', str(B/'focus_observation.qnt')]),
                   ('test', ['quint', 'test', str(B/'focus_observation.qnt')]),
                   ('run', ['quint', 'run', str(B/'focus_observation.qnt'), '--invariant=safe',
                            '--max-samples=2000', '--max-steps=100', '--seed=20261002', '--verbosity=1'])]:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    p = O / (label+'.log')
    with p.open('x') as f:
        f.write(r.stdout+r.stderr); f.flush(); os.fsync(f.fileno())
    checks.append({'command': cmd, 'exitCode': r.returncode, 'log': str(p),
                   'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    if r.returncode: break
unchanged = all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in sources.items())
row = {'result': 'pass' if len(checks)==3 and not any(c['exitCode'] for c in checks) and unchanged else 'fail',
       'checks': checks, 'sourceSHA256': sources, 'sourceUnchanged': unchanged,
       'runtimeChanged': False, 'nativeAccepted': False}
with (O/'report.json').open('x') as f:
    json.dump(row,f,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
print(json.dumps({k:v for k,v in row.items() if k not in ('checks','sourceSHA256')}))
raise SystemExit(row['result']!='pass')
