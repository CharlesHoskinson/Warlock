"""Actual compiled admission bind failure/correction/retry against held/private locks."""
import fcntl,hashlib,json,os,resource,selectors,shlex,shutil,subprocess,tempfile,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('retry-'+str(time.time_ns()));OUT.mkdir();inputs=OUT/'inputs';inputs.mkdir()
sources=[Path(__file__),ROOT/'qa/retry.c',SOURCE/'native/surface.h',SOURCE/'native/host-journal.h']
for p in sources:shutil.copy2(p,inputs/p.name)
report={'passed':False,'checks':[],'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},'scope':'Compiled actual C admission resources and real filesystem/flock; native GUI acceptance separate'}
def check(name,value,**evidence):report['checks'].append({'name':name,'passed':bool(value),**evidence});assert value,name
def line(process):
 with selectors.DefaultSelector() as selector:
  selector.register(process.stdout,selectors.EVENT_READ);assert selector.select(3),'child observation deadline'
 return json.loads(process.stdout.readline())
try:
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','json-glib-1.0'],text=True))
 compile=subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-Wno-unused-function',str(inputs/'retry.c'),'-o',str(OUT/'retry'),*flags],capture_output=True,text=True,timeout=30)
 (OUT/'compile.stdout').write_text(compile.stdout);(OUT/'compile.stderr').write_text(compile.stderr);assert compile.returncode==0,compile.stderr
 for fault in ['held','public']:
  with tempfile.TemporaryDirectory(prefix='elm-admission-retry-') as temp:
   runtime=Path(temp);runtime.chmod(0o700);namespace=runtime/'elm-window-recovery/alpha/71';namespace.mkdir(parents=True,mode=0o700);namespace.parent.chmod(0o700);namespace.parent.parent.chmod(0o700)
   config=runtime/'config.json';config.write_text(json.dumps({'runtime':str(runtime),'instance':'alpha'}));config.chmod(0o600)
   target=namespace/'host-writer.lock';fd=os.open(target,os.O_CREAT|os.O_RDWR,0o600)
   if fault=='held':fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
   else:target.chmod(0o644)
   child=subprocess.Popen([str(OUT/'retry'),str(config),json.dumps({'lifetime':'71','session':'2','frontend':'3'})],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
   try:
    first=line(child);check(fault+'FirstBindRefused',first['first']==0,receipt=first)
    # Correct the cause even on the historical source so its failed retry is observed.
    if fault=='held':fcntl.flock(fd,fcntl.LOCK_UN)
    else:target.chmod(0o600)
    child.stdin.write('r');child.stdin.flush();second=line(child)
    last=json.loads(child.stdout.readline());child.wait(timeout=3)
    check(fault+'RetryAfterActualCorrection',second['retry']==1,receipt=second,exitCode=child.returncode)
    check(fault+'InstanceContextRetained',first['instanceRetained']==1)
    check(fault+'FailedLifetimeResourcesRetired',first['lifetimeRetired']==1)
    check(fault+'ForeignLifetimeRefused',second['foreignLifetimeRefused']==1)
    check(fault+'SameLifetimeBindIdempotent',second['sameLifetimeIdempotent']==1)
    check(fault+'FinalCloseReleasesAllResources',last['closed']==1 and child.returncode==0)
   finally:
    if child.poll() is None:child.kill();child.wait(timeout=3)
    os.close(fd)
 report['passed']=True
except Exception as error:report.update(error=repr(error),traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
