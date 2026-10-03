"""Actual QtCore-only mutable declaration/kernel-argv probe; no GUI/native plugin."""
from pathlib import Path
import hashlib,json,os,shlex,subprocess
B=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();records=[]
def run(command):
 p=subprocess.run(command,capture_output=True,text=True,timeout=60);records.append(dict(command=command,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));return p
flags=run(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core']);assert flags.returncode==0
binary=B/'command-declaration-kernel';assert not binary.exists()
build=run(['/usr/bin/c++','-std=c++20','-fPIC','-O2','-o',str(binary),str(B/'command-declaration-kernel.cpp'),*shlex.split(flags.stdout)])
result='fail';evidence=None
if build.returncode==0:
 actual=run([str(binary)])
 if actual.returncode==0:evidence=json.loads(actual.stdout);result='pass'
primary=Path('/home/hoskinson/src/quickshell-accessibility/src/io/process.cpp');text=primary.read_text()
checks={k:v in text for k,v in {'declaredPropertyMutable':'QList<QString> Process::command() const { return this->mCommand; }','activeGuard':'if (this->process != nullptr || !this->isPostReload || !this->targetRunning','copiesLaunchArguments':'auto args = this->mCommand.sliced(1);','startsCopiedArguments':'this->process->start(cmd, args);'}.items()}
row=dict(result=result if all(checks.values())else 'fail',records=records,actual=evidence,primarySourceSHA256=sha(primary),primaryChecks=checks,binarySHA256=sha(binary)if binary.exists()else None,nativeGuiLaunch=False,actualQuickshellExecuted=False,markerRuntimeNotChanged=True)
fd=os.open(B/'command-declaration-kernel-final-before-correction.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w')as out:json.dump(row,out,indent=2);out.write('\n')
print(json.dumps({k:v for k,v in row.items()if k!='records'}));raise SystemExit(row['result']!='pass')
