"""Real subprocess qualification of sealed runtime/restart/cancellation policy."""
import hashlib,json,os,resource,shutil,signal,subprocess,time,traceback
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('cpu-'+str(time.time_ns()));OUT.mkdir()
program=ROOT/'supervisor.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'scope':'Actual synthetic subprocess and capsule refusal tests; not native GUI/release acceptance','inputs':{str(program):sha(program),str(Path(__file__)):sha(Path(__file__))},'checks':[]}
worker="#!/usr/bin/python3\nimport json,os,signal,sys,time\nfrom pathlib import Path\nfolder=Path(os.environ['CASE_DIRECTORY']);counter=folder/'count.txt';n=int(counter.read_text())+1 if counter.exists() else 1;counter.write_text(str(n))\nmode=os.environ['CASE_MODE']\ndef stop(sig,frame):sys.exit(3 if mode=='cancel-restart' else 0)\nsignal.signal(signal.SIGTERM,signal.SIG_IGN if mode=='ignore-stop' else stop)\n(folder/('ready-'+str(n))).write_text(str(os.getpid()))\nif mode=='restart':sys.exit(3 if n==1 else 0)\nif mode=='fail':sys.exit(1)\nif mode=='tamper-restart':\n (folder/'adapter/daemon.py').write_text('modified')\n sys.exit(3)\nif mode in ['wait','cancel-restart','ignore-stop']:\n while True:time.sleep(.02)\nsys.exit(0)\n"
def prepare(name,mode):
 folder=OUT/name;folder.mkdir();(folder/'assets').mkdir();(folder/'adapter').mkdir()
 host=folder/'host';host.write_text(worker);host.chmod(0o700)
 asset=folder/'assets/index.html';asset.write_text('controlled asset')
 backend=folder/'adapter/daemon.py';backend.write_text('controlled backend')
 manifest={'schema':1,'scope':'synthetic supervisor CPU fixture','host':str(host),'assets':str(folder/'assets'),'backend':str(backend),'coreSHA256':'0'*64,'files':{str(p):sha(p) for p in [host,asset,backend]}}
 capsule=folder/'manifest.json';capsule.write_text(json.dumps(manifest));capsule.chmod(0o600)
 authority=folder/'authority.json';authority.write_text(json.dumps({'runtime':str(folder),'instance':'controlled','pid':1,'expected_start':'1','binary_sha256':'0'*64}));authority.chmod(0o600)
 env=dict(os.environ,CASE_MODE=mode,CASE_DIRECTORY=str(folder),PYTHONDONTWRITEBYTECODE='1')
 return folder,capsule,authority,env

def check(name,value,**evidence):
 report['checks'].append({'name':name,'passed':bool(value),**evidence});assert value,name

def execute(name,mode,expected,count,mutation=None,stop=False):
 folder,capsule,authority,env=prepare(name,mode)
 if mutation:mutation(folder,capsule,authority)
 log=folder/'stdout.log'
 with log.open('w') as stream:
  child=subprocess.Popen(['/usr/bin/python3','-B',str(program),'--manifest',str(capsule),'--authority-config',str(authority)],env=env,stdout=stream,stderr=subprocess.STDOUT)
  try:
   if stop:
    until=time.monotonic()+3
    while not (folder/'ready-1').exists() and child.poll() is None and time.monotonic()<until:time.sleep(.01)
    assert (folder/'ready-1').exists(),'controlled child not ready'
    child.send_signal(signal.SIGTERM)
   code=child.wait(timeout=9)
  finally:
   if child.poll() is None:child.terminate();child.wait(timeout=8)
 text=log.read_text();exits=[json.loads(line.split(': ',1)[1]) for line in text.splitlines() if line.startswith('supervisor-host-exit: ')]
 starts=[json.loads(line.split(': ',1)[1]) for line in text.splitlines() if line.startswith('supervisor-host-start: ')]
 actual=int((folder/'count.txt').read_text()) if (folder/'count.txt').exists() else 0
 check(name,code==expected and actual==count and all(not Path('/proc/'+str(row['pid'])).exists() for row in starts),exitCode=code,launchCount=actual,starts=starts,exits=exits)
 return exits
try:
 execute('normal-exit','normal',0,1)
 execute('native-restart-only','restart',0,2)
 execute('failure-not-retried','fail',1,1)
 execute('tampered-next-generation-refused','tamper-restart',2,1)
 execute('modified-binary-refused','normal',2,0,lambda folder,capsule,authority:(folder/'host').write_text('modified'))
 execute('unsealed-adapter-entry-refused','normal',2,0,lambda folder,capsule,authority:(folder/'adapter/selectors.py').write_text('unsealed'))
 execute('duplicate-manifest-member-refused','normal',2,0,lambda folder,capsule,authority:capsule.write_text(capsule.read_text()[:-1]+',"schema":1}'))
 execute('public-authority-refused','normal',2,0,lambda folder,capsule,authority:authority.chmod(0o644))
 execute('symlink-backend-refused','normal',2,0,lambda folder,capsule,authority:((folder/'adapter/daemon.py').unlink(),(folder/'adapter/daemon.py').symlink_to(folder/'assets/index.html')))
 normal=execute('normal-stop-forwarded','wait',0,1,stop=True);check('normal-stop-not-forced',len(normal)==1 and normal[0]['exitCode']==0 and not normal[0]['forced'])
 cancelled=execute('stop-cancels-restart-request','cancel-restart',0,1,stop=True);check('cancelled-restart-exit-retained',len(cancelled)==1 and cancelled[0]['exitCode']==3 and cancelled[0]['stopping'])
 forced=execute('unresponsive-stop-escalates','ignore-stop',1,1,stop=True);check('forced-stop-is-failure',len(forced)==1 and forced[0]['forced'] and forced[0]['exitCode']==-9)
 report['passed']=True
except Exception as error:report.update(error=repr(error),traceback=traceback.format_exc())
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
