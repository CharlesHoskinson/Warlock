"""Actual pidfd signaling and retired-fd refusal; no native GUI acceptance."""
import hashlib,json,os,resource,select,signal,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'qa'/('pidfd-'+str(time.time_ns()));out.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'cases':[]}
try:
 assert hasattr(os,'pidfd_open') and hasattr(signal,'pidfd_send_signal')
 for name,code,terminate in [('owned-TERM','import time;time.sleep(5)',True),('normal-retired-fd','import time;time.sleep(.06)',False)]:
  case=out/name;case.mkdir();process=None;fd=None;record={'name':name,'passed':False};report['cases'].append(record);deadline=time.monotonic()+3
  try:
   with (case/'stdout').open('xb') as stdout,(case/'stderr').open('xb') as stderr:
    process=subprocess.Popen(['/usr/bin/python3','-c',code],stdout=stdout,stderr=stderr,start_new_session=True)
    fd=os.pidfd_open(process.pid,0)
    stat=Path('/proc',str(process.pid),'stat').read_text().rsplit(')',1)[1].split();record['identity']={'pid':process.pid,'start':stat[19]}
    fdinfo=Path('/proc/self/fdinfo',str(fd)).read_text();(case/'opened-fdinfo.txt').write_text(fdinfo)
    assert 'Pid:\t'+str(process.pid)+'\n' in fdinfo
    if terminate:signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
    process.wait(timeout=max(.001,deadline-time.monotonic()));record['exitCode']=process.returncode
    assert process.returncode==(-15 if terminate else 0)
    poll=select.poll();poll.register(fd,select.POLLIN);events=poll.poll(max(1,int((deadline-time.monotonic())*1000)));assert events and events[0][0]==fd
    (case/'retired-fdinfo.txt').write_text(Path('/proc/self/fdinfo',str(fd)).read_text())
    try:signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
    except ProcessLookupError:record['retiredSignalRefused']=True
    else:raise AssertionError('retired pidfd accepted a signal')
    record['passed']=True
  finally:
   if process is not None and process.poll() is None:
    if fd is not None:signal.pidfd_send_signal(fd,signal.SIGKILL,None,0)
    else:process.kill()
    process.wait(timeout=.5)
   if fd is not None:os.close(fd);record['descriptorClosed']=True
 report.update(passed=True,sourceSHA256=sha(__file__),pythonSHA256=sha('/usr/bin/python3'))
finally:
 (out/'test.py').write_bytes(Path(__file__).read_bytes());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out/'report.json')
if report['passed']:
 manifest=ROOT/'component-manifest.json';assert not manifest.exists()
 files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file()}
 manifest.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'scope':'Actual kernel pidfd signaling and retired-fd refusal only','files':files,'externalFiles':{'/usr/bin/python3':report['pythonSHA256']},'report':str(out/'report.json')},indent=2)+'\n')
