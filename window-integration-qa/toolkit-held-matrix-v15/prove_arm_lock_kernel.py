"""Scoped actual CPU/kernel lock proof before runtime edits."""
from pathlib import Path
import hashlib,json,os,subprocess
B=Path(__file__).resolve().parent;OLD=B.with_name('toolkit-held-matrix-v14');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=['evaluation_setup.py','run_native.py','qs_lifecycle.py','helper_setup.py','helper_observer.py','private_shell.py','payload-manifest.json','payload/home/.config/omarchy/plugins/hoskinson.windows/widget_v65/Windows.qml']
assert all((B/n).read_bytes()==(OLD/n).read_bytes()for n in files)
formal=json.loads((B/'arm-lock-deadline-formal-before-runtime.json').read_text());assert formal['result']=='pass'
p=subprocess.run(['/usr/bin/python3','-m','unittest','-v','test_arm_lock_candidate'],cwd=B,capture_output=True,text=True,timeout=10)
row=dict(result='pass'if p.returncode==0 else 'fail',exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr,formalSHA256=sha(B/'arm-lock-deadline-formal-before-runtime.json'),actualKernel=True,runtimeUnchangedExactV14=all((B/n).read_bytes()==(OLD/n).read_bytes()for n in files),candidateSHA256=sha(B/'arm_lock_candidate_fixture.py'),testSHA256=sha(B/'test_arm_lock_candidate.py'),nativeLaunch=False)
fd=os.open(B/'arm-lock-kernel-before-runtime.json',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n')
print(json.dumps(row));raise SystemExit(p.returncode!=0)
