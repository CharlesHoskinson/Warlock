"""Actual private relay subprocesses and file-control adversaries; no native broker execution."""
import hashlib,importlib.util,json,os,resource,shutil,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p):
 spec=importlib.util.spec_from_file_location('actual_relay',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
if len(sys.argv)>1 and sys.argv[1]=='worker':
 r=load(Path(__file__).with_name('relay.py'));r.pump([sys.executable,'-B','-c',sys.argv[3]],sys.argv[2]);raise SystemExit(0)
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('test-'+str(time.time_ns()));(OUT/'inputs/qa').mkdir(parents=True)
for p in [Path(__file__),ROOT/'qa/relay.py']:shutil.copy2(p,OUT/'inputs/qa'/p.name)
r=load(OUT/'inputs/qa/relay.py');checks=[];processes=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def refuses(fn):
 try:fn();return False
 except (r.RelayFailure,OSError,ValueError):return True
def wait(p,child):
 end=time.monotonic()+3
 while time.monotonic()<end:
  if p.exists():return
  assert child.poll() is None,'relay exited early'
  time.sleep(.005)
 raise RuntimeError('CPU actor readiness')
seq=0
def worker(code):
 global seq
 seq+=1;ctl=OUT/('control-'+str(seq));ctl.mkdir(mode=0o700)
 proc=subprocess.Popen([sys.executable,'-B',str(OUT/'inputs/qa/test.py'),'worker',str(ctl),code],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 processes.append(proc);wait(ctl/'actor.json',proc);return proc,ctl
report={'passed':False,'scope':'Actual relay subprocess/pipe ownership and strict private controls; no native GUI or compositor acceptance','checks':checks}
try:
 echo='import sys\nfor line in sys.stdin.buffer: sys.stdout.buffer.write(line);sys.stdout.buffer.flush()'
 child,ctl=worker(echo);marker=r.actor_status(ctl)
 check('exact real relay PID/start and owned child live',marker['relay']['pid']==child.pid and r.start(child.pid)==marker['relay']['start'] and r.start(marker['child']['pid'])==marker['child']['start'])
 payload=b'{"kind":"actual-frame"}\n'+b'x'*16000+b'\n';child.stdin.write(payload);child.stdin.flush()
 check('public EOF request binds exact live actor',r.close_stdin(ctl)==marker)
 check('duplicate control never replays EOF',refuses(lambda:r.close_stdin(ctl)))
 child.stdin.close();child.stdin=None;out,err=child.communicate(timeout=5)
 check('all raw bytes forwarded without synthesis',out==payload)
 check('relay exits normally after child normal EOF',child.returncode==0 and not err)
 status=r.exit_status(ctl);check('explicit exact normal child exit proof',status=={**marker,'childExit':0,'stdinClosed':True})
 check('both original processes gone',r.start(marker['child']['pid']) is None and r.start(marker['relay']['pid']) is None)
 child,ctl=worker(echo);child.stdin.write(b'host EOF\n');child.stdin.close();child.stdin=None;out,err=child.communicate(timeout=5)
 check('natural host EOF exits both normally and forwards final bytes',child.returncode==0 and out==b'host EOF\n' and r.exit_status(ctl)['childExit']==0)
 child,ctl=worker(echo);gate=ctl/'gate.json';gate.write_text(json.dumps({'action':'close','relay':{'pid':child.pid,'start':'0'},'child':r.actor_status(ctl)['child']}));gate.chmod(0o600)
 child.stdin.close();child.stdin=None;out,err=child.communicate(timeout=5)
 check('wrong start refuses without invented output',child.returncode!=0 and out==b'' and not (ctl/'exit.json').exists())
 child,ctl=worker(echo);gate=ctl/'gate.json';gate.unlink();gate.write_text('{"action":"forward"}');gate.chmod(0o600)
 child.stdin.close();child.stdin=None;out,err=child.communicate(timeout=5)
 check('gate inode replacement refuses',child.returncode!=0 and out==b'')
 child,ctl=worker('import sys\nsys.stdin.buffer.read()\nsys.exit(7)');r.close_stdin(ctl);child.stdin.close();child.stdin=None;out,err=child.communicate(timeout=5)
 check('nonzero child exit cannot publish normal status',child.returncode!=0 and not (ctl/'exit.json').exists())
 for raw,label in [(b'{"x":1,"x":2}','duplicate keys'),(b'x'*4097,'oversized record')]:check(label+' refused',refuses(lambda:r.decode(raw)))
 check('extra control fields refused',refuses(lambda:r.exact({'action':'forward','extra':True},['action'])))
 bad=OUT/'public';bad.mkdir(mode=0o755);check('public directory refuses',refuses(lambda:r.directory(bad)))
 link=OUT/'dir-link';link.symlink_to(ctl,target_is_directory=True);check('symlink directory refuses',refuses(lambda:r.directory(link)))
 private=OUT/'private.json';private.write_text('{}');private.chmod(0o644);check('public file refuses',refuses(lambda:r.read_private(private)))
 private.chmod(0o600);os.link(private,OUT/'hardlink.json');check('hardlinked file refuses',refuses(lambda:r.read_private(private)))
 private.unlink();private=OUT/'link.json';private.symlink_to(ctl/'actor.json');check('symlink file refuses',refuses(lambda:r.read_private(private)))
 report['passed']=True
except Exception as error:report['error']=repr(error)
finally:
 for p in processes:
  if p.poll() is None:
   if p.stdin and not p.stdin.closed:p.stdin.close()
   try:p.wait(timeout=4)
   except subprocess.TimeoutExpired:p.terminate();p.wait(timeout=4)
 report['processExitCodes']=[p.returncode for p in processes]
 report['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
