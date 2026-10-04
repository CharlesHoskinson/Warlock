"""Protected real cgroup/session-escape cleanup proof, without a GUI."""
import hashlib,json,os,resource,signal,subprocess,time,traceback
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa'/('cpu-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
WORKER=ROOT/'qa/worker.py';unit='qa-harness-shell-cohort-'+str(time.time_ns())+'.scope'
report={'passed':False,'scope':'Real isolated user-scope forced cleanup and outside-peer preservation; no GUI/host/release acceptance','checks':[],'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),WORKER]},'unit':unit,'parentCgroup':Path('/proc/self/cgroup').read_text()};peer=None;job=None;owned=False

def check(name,value,**evidence):report['checks'].append({'name':name,'passed':bool(value),**evidence});assert value,name

def wait(fn,seconds=6):
 until=time.monotonic()+seconds
 while time.monotonic()<until:
  value=fn()
  if value:return value
  time.sleep(.02)
 raise RuntimeError('Observation deadline')

def same(row):
 try:
  raw=Path('/proc/'+str(row['pid'])+'/stat').read_text();fields=raw[raw.rindex(')')+2:].split()
  return fields[19]==row['start'] and fields[0]!='Z'
 except FileNotFoundError:return False

def show():
 result=subprocess.run(['systemctl','--user','show',unit,'--property=Id,ControlGroup,KillMode,TimeoutStopUSec,ActiveState,SubState'],capture_output=True,text=True,timeout=3)
 return {line.split('=',1)[0]:line.split('=',1)[1] for line in result.stdout.splitlines() if '=' in line}
try:
 peer_file=OUT/'peer.json';peer=subprocess.Popen(['/usr/bin/python3','-B',str(WORKER),'peer',str(peer_file)],start_new_session=True)
 peer_row=wait(lambda:json.loads(peer_file.read_text()) if peer_file.exists() else None)
 log=(OUT/'scope.log').open('w')
 command=['systemd-run','--user','--scope','--quiet','--slice=qa-harness.slice','--unit='+unit,'--property=KillMode=control-group','--property=TimeoutStopSec=5s','/usr/bin/python3','-B',str(WORKER),'cohort',str(OUT/'cohort.json')]
 report['command']=command
 job=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 main=wait(lambda:json.loads((OUT/'cohort.json').read_text()) if (OUT/'cohort.json').exists() else None)
 helper=wait(lambda:json.loads((OUT/'cohort.helper.json').read_text()) if (OUT/'cohort.helper.json').exists() else None)
 properties=show();report['properties']=properties
 check('exactOwnedQAScopeIdentified',properties.get('Id')==unit and properties.get('ControlGroup','').endswith('/'+unit) and '/qa-harness.slice/' in properties['ControlGroup'])
 check('controlledMainAndDetachedHelperShareOnlyOwnedCgroup',main['cgroup']==helper['cgroup'] and properties['ControlGroup'] in main['cgroup'] and peer_row['cgroup']!=main['cgroup'] and report['parentCgroup']!=main['cgroup'])
 owned=True
 check('helperEscapedProcessGroupButNotCgroup',helper['pgid']!=main['pgid'] and helper['pid']==main['helper'],main=main,helper=helper,peer=peer_row)
 check('exactCoreLimitInheritedByEveryWorker',main['core']==helper['core']==peer_row['core']==[1,1])
 check('stopPolicyIsWholeCgroupWithOriginalFiveSecondGrace',properties['KillMode']=='control-group' and properties['TimeoutStopUSec']=='5s')
 started=time.monotonic();stopped=subprocess.run(['systemctl','--user','stop',unit],capture_output=True,text=True,timeout=9)
 report['stop']={'exitCode':stopped.returncode,'stdout':stopped.stdout,'stderr':stopped.stderr,'elapsedSeconds':time.monotonic()-started}
 job.wait(timeout=4);log.close()
 check('forcedScopeStopRemovesMainAndDetachedHelper',not same(main) and not same(helper),jobExitCode=job.returncode,stop=report['stop'])
 check('outsidePeerAndOriginalQAScopePreserved',same(peer_row) and Path('/proc/self/cgroup').read_text()==report['parentCgroup'])
 report['postStopProperties']=show();report['passed']=True
except Exception as error:report.update(error=repr(error),traceback=traceback.format_exc())
finally:
 if owned:
  subprocess.run(['systemctl','--user','stop',unit],capture_output=True,timeout=9)
  subprocess.run(['systemctl','--user','reset-failed',unit],capture_output=True,timeout=3)
 if job and job.poll() is None:job.terminate();job.wait(timeout=4)
 if peer and peer.poll() is None:peer.terminate();peer.wait(timeout=4)
 if peer:report['peerNormalExit']=peer.returncode==0;report['passed']=report['passed'] and peer.returncode==0
report['artifacts']={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'error':report.get('error'),'report':str(OUT/'report.json')}));raise SystemExit(not report['passed'])
