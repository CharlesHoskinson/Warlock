import hashlib,importlib.util,json,os,resource,shutil,subprocess,sys,time
from pathlib import Path
if len(sys.argv)==5 and sys.argv[1]=='--child':
 spec=importlib.util.spec_from_file_location('guard',sys.argv[2]);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);print('before-open',flush=True);result=g.pinned(sys.argv[3],sys.argv[4],time.monotonic()+0.15);print('returned',result,flush=True);raise SystemExit(0)
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent/'elm-own-popup-runtime-closure-guard-v326/guard.py';OUT=ROOT/('fifo-'+str(time.time_ns()));OUT.mkdir(mode=0o700);captured=OUT/'guard.py';shutil.copy2(SOURCE,captured);captured.chmod(0o444)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={'passed':False,'nativeAcceptance':False,'scope':'Actual guarded open original150ms deadline with owned regular/FIFO CPU helper; no compositor/host operation','sourceSHA256':sha(captured),'cases':[]}
try:
 for mode in ['regular','fifo']:
  target=OUT/(mode+'.target')
  if mode=='regular':target.write_bytes(b'owned');expected=sha(target)
  else:os.mkfifo(target,0o600);expected='0'*64
  stdout=OUT/(mode+'.stdout');stderr=OUT/(mode+'.stderr')
  with stdout.open('wb') as out,stderr.open('wb') as err:
   command=[sys.executable,'-B',str(Path(__file__)), '--child',str(captured),str(target),expected];child=subprocess.Popen(command,stdout=out,stderr=err);began=time.monotonic();proc=Path('/proc')/str(child.pid);start=proc.joinpath('stat').read_text().split(')')[-1].split()[19];timed_out=False
   try:code=child.wait(timeout=0.8)
   except subprocess.TimeoutExpired:timed_out=True;child.terminate();code=child.wait(timeout=2)
  row={'mode':mode,'command':command,'pid':child.pid,'start':start,'exitCode':code,'timedOut':timed_out,'originalDeadlineSeconds':0.15,'boundedOwnerTimeoutSeconds':0.8,'elapsed':time.monotonic()-began,'stdout':str(stdout),'stderr':str(stderr)};r['cases'].append(row)
  if mode=='regular':assert code==0 and not timed_out
  else:assert timed_out and code==-15 and b'before-open' in stdout.read_bytes();target.unlink()
 r['passed']=True
except Exception as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');print('PASS actual FIFO blocks beyond original deadline' if r['passed'] else r['error'])
if not r['passed']:raise SystemExit(1)
