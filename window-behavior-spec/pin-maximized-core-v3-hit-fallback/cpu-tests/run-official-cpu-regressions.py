import hashlib,json,subprocess,time
from pathlib import Path
B=Path(__file__).resolve().parents[1]
own=json.loads((B/'cpu-tests/owning-final-commands.json').read_text())['commands']
base=own[0]['argv'][:own[0]['argv'].index('-c')]+['-I'+str(B/'build-core-make'),'-I'+str(B/'core/src/include')]
records=[];objects=[]
def run(argv,log):
 start=time.monotonic()
 with (B/log).open('wb') as out:p=subprocess.run(argv,cwd=B,stdout=out,stderr=subprocess.STDOUT)
 records.append(dict(argv=argv,exitCode=p.returncode,elapsed=time.monotonic()-start,log=log,logSHA256=hashlib.sha256((B/log).read_bytes()).hexdigest()))
 (B/'cpu-tests/official-cpu-commands.json').write_text(json.dumps(dict(nativeExecuted=False,compositorOnlyConfigConstructor=True,commands=records),indent=2)+'\n')
 print(log,p.returncode,flush=True)
 if p.returncode:raise SystemExit(p.returncode)
for index,source in enumerate(sorted((B/'core/tests').rglob('*.cpp'))):
 obj=B/'cpu-tests'/('official-'+str(index)+'.o');objects.append(str(obj))
 run(base+['-c',str(source),'-o',str(obj)],'cpu-tests/official-compile-'+str(index)+'.log')
link=own[1]['argv'].copy();link[1:4]=objects+['-o',str(B/'cpu-tests/official-cpu-tests')]
link+=subprocess.check_output(['pkg-config','--libs','gtest_main'],text=True).split()
run(link,'cpu-tests/official-link.log')
run([str(B/'cpu-tests/official-cpu-tests'),'--gtest_output=json:'+str(B/'cpu-tests/official-cpu-results.json')],'cpu-tests/official-run.log')
