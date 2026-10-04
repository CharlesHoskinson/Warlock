"""Actual dead cgroup descriptor error, with exact transient scope ownership."""
import errno,json,os,resource,subprocess,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('cpu-'+str(time.time_ns()));OUT.mkdir()
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
report={'passed':False,'checks':[]};child=None;fd=None;unit='qa-harness-cgroup-disappear-'+str(time.time_ns())+'.scope'
def check(name,value,**data):report['checks'].append({'name':name,'passed':bool(value),**data});assert value,name
def start(pid):raw=Path('/proc/'+str(pid)+'/stat').read_text();return raw[raw.rfind(')')+2:].split()[19]
try:
 child=subprocess.Popen(['systemd-run','--user','--scope','--quiet','--slice=qa-harness.slice','--unit='+unit,'/usr/bin/python3','-B','-c','import time;time.sleep(30)'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True,start_new_session=True)
 identity=start(child.pid);until=time.monotonic()+3;info={}
 while time.monotonic()<until:
  result=subprocess.run(['systemctl','--user','show',unit,'--property=Id,ControlGroup'],capture_output=True,text=True,timeout=3)
  info=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
  if info.get('ControlGroup','').endswith('/'+unit):break
  time.sleep(.02)
 group=info.get('ControlGroup','');check('exactOwnedScopeContainsUnreapedChild',info.get('Id')==unit and group.endswith('/'+unit) and start(child.pid)==identity and '0::'+group+'\n' in Path('/proc/'+str(child.pid)+'/cgroup').read_text(),unit=unit,group=group,pid=child.pid,start=identity)
 check('parentScopeExcluded',group not in Path('/proc/self/cgroup').read_text())
 path=Path('/sys/fs/cgroup')/group.lstrip('/')/'cgroup.procs';fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC)
 before=os.read(fd,4096).decode();check('heldDescriptorInitiallyListsOwnedChild',str(child.pid) in before.split())
 child.terminate();child.wait(timeout=3);check('ownedChildStopsByDeclaredSignal',child.returncode==-15,exitCode=child.returncode)
 until=time.monotonic()+3
 while path.exists() and time.monotonic()<until:time.sleep(.02)
 check('systemdRemovesEmptyOwnedGroup',not path.exists())
 os.lseek(fd,0,os.SEEK_SET)
 try:report['deadRead']=os.read(fd,4096).decode();report['deadErrno']=None
 except OSError as error:report['deadErrno']=error.errno;report['deadErrorName']=errno.errorcode.get(error.errno)
 check('deadHeldDescriptorReturnsENODEV',report['deadErrno']==errno.ENODEV,errno=report['deadErrno'],name=report.get('deadErrorName'))
 report['passed']=True
except Exception as error:report.update(error=repr(error),traceback=traceback.format_exc())
finally:
 if fd is not None:os.close(fd)
 if child is not None and child.poll() is None:child.terminate();child.wait(timeout=3)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'deadErrno':report.get('deadErrno'),'error':report.get('error')}));raise SystemExit(not report['passed'])
