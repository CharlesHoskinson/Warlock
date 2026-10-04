"""Deterministic unread pipe cut and blocked output deadline oracles."""
import hashlib,importlib.util,json,os,resource,shutil,signal,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('edges-'+str(time.time_ns()));(OUT/'inputs/qa').mkdir(parents=True)
for p in [ROOT/'qa/relay.py',ROOT/'qa/test.py',Path(__file__)]:shutil.copy2(p,OUT/'inputs/qa'/p.name)
spec=importlib.util.spec_from_file_location('edge_relay',OUT/'inputs/qa/relay.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
checks=[];children=[]
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
def worker(name,code):
 p=OUT/name;p.mkdir(mode=0o700);c=subprocess.Popen([sys.executable,'-B',str(OUT/'inputs/qa/test.py'),'worker',str(p),code],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE);children.append(c)
 end=time.monotonic()+3
 while not (p/'actor.json').exists():
  assert c.poll() is None and time.monotonic()<end;time.sleep(.005)
 return c,p
report={'passed':False,'scope':'Synthetic owned subprocess transport adversaries, no native acceptance','checks':checks}
try:
 c,p=worker('backlog','import sys\nfor line in sys.stdin.buffer:sys.stdout.buffer.write(line);sys.stdout.buffer.flush()');marker=r.actor_status(p)
 os.kill(c.pid,signal.SIGSTOP)
 # Wait for kernel-confirmed stopped relay, rather than an arbitrary sleep.
 end=time.monotonic()+2
 while Path('/proc',str(c.pid),'stat').read_text().rsplit(')',1)[1].split()[0] not in ('T','t'):
  assert time.monotonic()<end;time.sleep(.001)
 raw=b'known unread parent input\n';c.stdin.write(raw);c.stdin.flush();r.close_stdin(p);os.kill(c.pid,signal.SIGCONT)
 out,err=c.communicate(timeout=5)
 check('kernel queued pre-cut bytes are forwarded exactly',out==raw)
 check('controlled backlog cut exits normally',c.returncode==0 and not err and r.exit_status(p)['stdinClosed'] is True)
 check('backlog actor identities gone',r.start(marker['child']['pid']) is None and r.start(marker['relay']['pid']) is None)
 c,p=worker('blocked','import sys\nsys.stdin.buffer.read()\nsys.stdout.buffer.write(b"x"*200000);sys.stdout.buffer.flush()');marker=r.actor_status(p);r.close_stdin(p);began=time.monotonic()
 # Deliberately do not consume relay stdout; the process must terminate itself.
 c.wait(timeout=5);elapsed=time.monotonic()-began
 check('non-draining host cannot defeat absolute EOF deadline',c.returncode!=0 and elapsed<4.5)
 out,err=c.communicate(timeout=1)
 check('blocked output records deadline refusal',b'Broker EOF deadline' in err)
 check('blocked output cannot publish normal status',not (p/'exit.json').exists())
 check('blocked output child terminated and reaped',r.start(marker['child']['pid']) is None)
 report['passed']=True
except Exception as error:report['error']=repr(error)
finally:
 for c in children:
  if c.poll() is None:
   os.kill(c.pid,signal.SIGCONT);c.terminate();c.wait(timeout=4)
 report['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file()}
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
