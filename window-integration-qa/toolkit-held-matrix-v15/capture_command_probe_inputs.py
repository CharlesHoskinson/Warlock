"""Capture the reviewed QtCore-only probe's compiler source closure; no execution."""
from pathlib import Path
import hashlib,json,os,shlex,subprocess
B=Path(__file__).resolve().parent
inputs={};modes={};links={};records=[]
def add(p):
 p=Path(p)
 if p.is_symlink():links[str(p)]=os.readlink(p);return add(p.resolve())
 inputs[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest();modes[str(p)]=p.stat().st_mode&0o7777
def run(cmd):
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=60);records.append(dict(command=cmd,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0;return p.stdout
flags=shlex.split(run(['/usr/bin/pkg-config','--cflags','Qt6Core']))
dependencies=shlex.split(run(['/usr/bin/c++','-std=c++20','-fPIC','-O2','-M',str(B/'command-declaration-kernel.cpp'),*flags]).replace('\\\n',' '))
assert dependencies.pop(0).endswith(':')
for name in dependencies:add(name)
for name in ('/usr/bin/c++','/usr/bin/pkg-config','/usr/lib/pkgconfig/Qt6Core.pc',str(B/'command-declaration-kernel')):add(name)
loader=json.loads((B/'qt-loader-inputs.json').read_text())
for name,digest in loader['inputs'].items():
 add(name);assert inputs.get(name)==digest
for name,target in loader['symlinks'].items():
 assert os.readlink(name)==target;add(name)
row=dict(result='pass',inputs=inputs,inputModes=modes,symlinks=links,commands=records,scope='compiler -M source closure plus inherited exact Qt loader inputs; QtCore probe only, no GUI execution',nativeLaunched=False)
fd=os.open(B/'command-probe-inputs.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n')
print(json.dumps(dict(result='pass',inputs=len(inputs),modes=len(modes),links=len(links),nativeLaunched=False)))
