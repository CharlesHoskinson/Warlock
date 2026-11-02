#!/usr/bin/env python3
"""ROOT-EXECUTED fixed system-manager scope guardian; never a user manager."""
import hashlib, json, os, re, stat, subprocess, sys, time, uuid
from pathlib import Path
BASE=Path('/home/charl/warlock-del010-cross-user-20261102T011435Z')
QA=Path('/home/charl/warlock-live-usability-typed-model-20261102T000451Z/qa-mocks')
RUNNER=BASE/'root-auth-runner.py'
RUNNER_SHA='358e94d5e41391e66de35f708303d790b778dbc8ffd55ea0cd312b8d108fe698'
QA_HASHES={'qa_run.py':'656f118c268e9f762f2d62c859d146043d74c83b72cd5457b779f1e30cb183a1','qa_launch.py':'6ef35104e4082249cfbabb747425210b1ca6fe988f675880a2afc059e13b5b23'}
ENV={'PATH':'/usr/bin:/bin','HOME':'/root','LANG':'C','LC_ALL':'C','XDG_RUNTIME_DIR':'/run/user/0'}
def require(ok,why):
 if not ok: raise RuntimeError(why)
def pin(path):
 path=Path(path);require(path.resolve(strict=True)==path,'Unexpected script symlink')
 info=path.lstat();require(stat.S_ISREG(info.st_mode),'Regular script required')
 return {'path':str(path),'device':info.st_dev,'inode':info.st_ino,'size':info.st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def write(path,value):
 raw=value if isinstance(value,bytes) else (json.dumps(value,indent=2)+'\n').encode()
 fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
 with os.fdopen(fd,'wb') as output: output.write(raw)
def scope_info(unit):
 command=['/usr/bin/systemctl','--system','show',unit,'--no-pager','--property=Id','--property=LoadState','--property=ActiveState','--property=ControlGroup','--property=InvocationID','--property=Description']
 result=subprocess.run(command,stdin=subprocess.DEVNULL,capture_output=True,env=ENV,timeout=5,check=False)
 properties=dict(row.split('=',1) for row in result.stdout.decode().splitlines() if '=' in row)
 return {'argv':command,'returncode':result.returncode,'properties':properties,'stdout':result.stdout.decode(),'stderr':result.stderr.decode()}
def group_members(unit):
 path=Path('/sys/fs/cgroup/qa-harness.slice')/unit
 if not path.exists(): return {'exists':False,'pids':[]}
 require(path.resolve(strict=True)==path and path.is_dir(),'Unexpected owned cgroup path')
 rows=[]
 for member in sorted(path.rglob('cgroup.procs')):
  require(not member.is_symlink(),'Unexpected cgroup membership symlink')
  rows.extend(int(value) for value in member.read_text().split())
 return {'exists':True,'pids':sorted(set(rows))}
def proc_scope_members(unit):
 target='/qa-harness.slice/'+unit
 result={'startedMonotonic':time.monotonic(),'examined':0,'remaining':[],'readErrors':[]}
 for path in Path('/proc').iterdir():
  if not path.name.isdigit(): continue
  try:
   birth=(path/'stat').read_text().rsplit(')',1)[1].split()[19]
   with (path/'cgroup').open() as stream: raw=stream.read(65537)
   require((path/'stat').read_text().rsplit(')',1)[1].split()[19]==birth,'PID birth changed during cgroup scan')
   require(len(raw)<=65536,'Proc cgroup bound')
   result['examined']+=1
   groups=[line.split(':',2)[-1] for line in raw.splitlines()]
   if any(value==target or value.startswith(target+'/') for value in groups): result['remaining'].append({'pid':int(path.name),'birth':birth,'cgroup':raw})
  except (OSError,RuntimeError,IndexError) as error: result['readErrors'].append({'pid':int(path.name),'error':type(error).__name__+': '+str(error)})
 result['finishedMonotonic']=time.monotonic()
 return result
def main():
 require(len(sys.argv)==1 and os.getresuid()==(0,0,0),'Fixed root guardian only')
 os.umask(0o077)
 require(BASE.resolve(strict=True)==BASE and BASE.is_dir(),'Expected unchanged guest source prefix')
 runtime=Path('/run/user/0')
 try: runtime.mkdir(mode=0o700)
 except FileExistsError: pass
 status=runtime.lstat();require(stat.S_ISDIR(status.st_mode) and status.st_uid==0 and stat.S_IMODE(status.st_mode)==0o700,'Existing /run/user/0 must already be root nonsymlink0700')
 require(pin(RUNNER)['sha256']==RUNNER_SHA,'Reviewed runner changed')
 for name,sha in QA_HASHES.items(): require(pin(QA/name)['sha256']==sha,'Unchanged QA helper changed')
 token=uuid.uuid4().hex;attempt=BASE/('root-auth-'+token);attempt.mkdir(mode=0o700)
 unit='qa-harness-del010-'+token+'.scope';description='Warlock DEL010 private '+token
 initial=scope_info(unit);require(initial['properties'].get('LoadState')=='not-found','Refuse preexisting scope')
 env=dict(ENV,WARLOCK_DEL010_ATTEMPT=str(attempt),WARLOCK_DEL010_UNIT=unit)
 argv=['/usr/bin/systemd-run','--scope','--slice=qa-harness.slice','--unit='+unit.removesuffix('.scope'),'--description='+description,'-p','MemoryMax=2G','--','/usr/bin/prlimit','--core=1:1','--','/usr/bin/python3','-B',str(QA/'qa_run.py'),'--inside-scope','--','/usr/bin/python3','-B',str(RUNNER)]
 report={'schema':1,'scope':'VM actual kernel credential component only; no GUI/native provider/release acceptance','passed':False,'nativeAccepted':False,'releaseAccepted':False,'attempt':str(attempt),'unit':unit,'argv':argv,'forced':False,'normal':False,'initialScope':initial,'runnerPin':pin(RUNNER),'guardianPin':pin(Path(__file__).resolve()),'timeoutSeconds':120}
 write(attempt/'guardian-start.json',report)
 out=os.open(attempt/'launcher.stdout',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC,0o600);err=os.open(attempt/'launcher.stderr',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC,0o600)
 child=None;deadline=time.monotonic()+120
 try:
  child=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=out,stderr=err,env=env,start_new_session=True)
  report['launcherPid']=child.pid
  try:
   report['launcherBirth']=Path('/proc/'+str(child.pid)+'/stat').read_text().rsplit(')',1)[1].split()[19]
  except FileNotFoundError: report['launcherBirth']=None
  try: report['returncode']=child.wait(timeout=max(0.001,deadline-time.monotonic()));report['normal']=True
  except subprocess.TimeoutExpired:
   report['forced']=True;observed=scope_info(unit);report['scopeAtTimeout']=observed;props=observed['properties']
   require(props.get('Id')==unit and props.get('Description')==description and props.get('ControlGroup')=='/qa-harness.slice/'+unit and re.fullmatch(r'[0-9a-f]{32}',props.get('InvocationID','')),'Cannot prove ownership of timed-out scope; no kill issued')
   command=['/usr/bin/systemctl','--system','kill','--signal=SIGKILL','--kill-whom=all',unit]
   killed=subprocess.run(command,stdin=subprocess.DEVNULL,capture_output=True,env=ENV,timeout=5,check=False)
   report['kill']={'argv':command,'returncode':killed.returncode,'stdout':killed.stdout.decode(),'stderr':killed.stderr.decode()}
   try: report['returncode']=child.wait(timeout=5)
   except subprocess.TimeoutExpired: report['launcherStillRunning']=True
  report['scopeAfter']=scope_info(unit)
  try: report['membersAfter']=group_members(unit)
  except OSError as error: report['cgroupReadError']=type(error).__name__+': '+str(error)
  report['procScopeScan']=proc_scope_members(unit)
  scan=report['procScopeScan']
  final_scope=report['scopeAfter']['properties']
  inactive=final_scope.get('LoadState')=='not-found' or final_scope.get('ActiveState') in ('inactive','failed')
  report['cleanupConfirmed']=inactive and child.poll() is not None and not report.get('membersAfter',{}).get('pids',[]) and scan['examined']>0 and not scan['remaining'] and not scan['readErrors']
  report['cleanupDisposition']='confirmed-independent-proc-scan' if report['cleanupConfirmed'] else 'unknown-or-processes-remain'
  receipt=attempt/'runner-report.json'
  if receipt.exists():
   info=receipt.lstat();require(stat.S_ISREG(info.st_mode) and info.st_uid==0 and stat.S_IMODE(info.st_mode)==0o600,'Expected private root runner report')
   value=json.loads(receipt.read_text());report['runnerReportPin']=pin(receipt);report['runnerPassed']=value.get('passed') is True;report['contextEvidenceComplete']=value.get('contextEvidenceComplete') is True
  report['sourceStable']=pin(RUNNER)==report['runnerPin'] and pin(Path(__file__).resolve())==report['guardianPin'] and all(pin(QA/name)['sha256']==sha for name,sha in QA_HASHES.items())
  report['passed']=report['normal'] and not report['forced'] and report.get('returncode')==0 and report.get('runnerPassed',False) and report.get('contextEvidenceComplete',False) and report['cleanupConfirmed'] and report['sourceStable']
 except BaseException as problem:
  report['error']=type(problem).__name__+': '+str(problem)
 finally:
  os.close(out);os.close(err);report['finishedMonotonic']=time.monotonic();write(attempt/'guardian-report.json',report)
  print(json.dumps({'passed':report['passed'],'forced':report['forced'],'cleanupConfirmed':report.get('cleanupConfirmed',False),'report':str(attempt/'guardian-report.json'),'nativeAccepted':False,'releaseAccepted':False}),flush=True)
 return 0 if report['passed'] else 1
if __name__=='__main__': raise SystemExit(main())
