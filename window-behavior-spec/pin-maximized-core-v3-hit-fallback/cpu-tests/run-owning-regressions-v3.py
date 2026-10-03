"""Compile real owning adapters from current generated compiler/link inputs."""
import hashlib,json,shlex,subprocess,time
from pathlib import Path
B=Path(__file__).resolve().parents[1];BUILD=B/'build-core-make'
entry=next(r for r in json.loads((BUILD/'compile_commands.json').read_text()) if r['file'].endswith('/NativePinState.cpp'))
a=shlex.split(entry['command']);base=[];i=0
while i<len(a):
 x=a[i]
 if x in ['-include','-o']:
  i+=2;continue
 if x in ['-c','-DNDEBUG','-O3'] or x==entry['file']:
  i+=1;continue
 base.append(x);i+=1
base+=['-O1','-UNDEBUG']
link=shlex.split((BUILD/'CMakeFiles/Hyprland.dir/link.txt').read_text());tail=[];i=1
while i<len(link):
 x=link[i]
 if x=='-o':i+=2;continue
 if x.endswith('src/main.cpp.o') or x.startswith('-Wl,--dependency-file='):i+=1;continue
 if x.endswith('.a') and not Path(x).is_absolute():x=str(BUILD/x)
 tail.append(x);i+=1
records=[]
def run(argv,log):
 start=time.monotonic()
 with (B/log).open('wb') as f:r=subprocess.run(argv,cwd=B,stdout=f,stderr=subprocess.STDOUT)
 records.append(dict(argv=argv,exitCode=r.returncode,elapsed=time.monotonic()-start,log=log,logSHA256=hashlib.sha256((B/log).read_bytes()).hexdigest()))
 (B/'cpu-tests/owning-final-commands.json').write_text(json.dumps(dict(commands=records,nativeExecuted=False,compilerSource=entry,linkSourceSHA256=hashlib.sha256((BUILD/'CMakeFiles/Hyprland.dir/link.txt').read_bytes()).hexdigest()),indent=2)+'\n')
 print(log,r.returncode,flush=True)
 if r.returncode:raise SystemExit(r.returncode)
for source,name,compilelog,linklog,runlog in [('test_native_owning.cpp','test_native_owning','owning-compile-final.log','owning-link-final.log','owning-run-final.log'),('test_actual_core_policy.cpp','test_actual_core_policy','actual-core-policy-compile.log','actual-core-policy-link.log','actual-core-policy-run.log')]:
 obj='cpu-tests/'+name+'.o';binary='cpu-tests/'+name
 run(base+['-c','cpu-tests/'+source,'-o',obj],'cpu-tests/'+compilelog)
 run([link[0],obj,'-o',binary]+tail,'cpu-tests/'+linklog)
 run([str(B/binary)],'cpu-tests/'+runlog)
