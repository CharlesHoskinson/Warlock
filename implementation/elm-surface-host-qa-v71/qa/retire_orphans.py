"""Retire two identified offscreen repo QA daemons; never select desktop clients."""
import json,os,resource,signal,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
root=Path(__file__).resolve().parent
report={'passed':False,'historicalNormalExitAccepted':False,'mainDesktopActions':False,'processes':[]}
try:
 for pid,directory,unit in [(218417,'/tmp/tmp4hr65bwt','qa-harness-892458c371454045901dd8dcfc8a17b1.scope'),(248177,'/tmp/tmpdqw6fruu','qa-harness-e69efa364b264cb692d0e777a6d28882.scope')]:
  proc=Path('/proc')/str(pid);fd=os.pidfd_open(pid)
  try:
   stat=proc.joinpath('stat').read_text();start=stat[stat.rfind(')')+2:].split()[19]
   cmd=proc.joinpath('cmdline').read_bytes().split(b'\0');assert cmd[:6]==[b'qs',b'-p',directory.encode(),b'-d',b'-n',b''],cmd
   assert proc.stat().st_uid==os.getuid() and not Path(directory).exists()
   env=dict(x.split(b'=',1) for x in proc.joinpath('environ').read_bytes().split(b'\0') if b'=' in x)
   assert env.get(b'QT_QPA_PLATFORM')==b'offscreen' and not env.get(b'WAYLAND_DISPLAY') and env.get(b'XDG_RUNTIME_DIR',b'').startswith(b'/run/user/1000/wqa/')
   assert unit in proc.joinpath('cgroup').read_text()
   description=subprocess.run(['systemctl','--user','show',unit,'-p','Description','--value'],capture_output=True,text=True,check=True).stdout.strip()
   assert description.endswith('/implementation/switcher-v1/tests/run_qml_probe.py')
   row={'pid':pid,'startTicks':start,'unit':unit,'description':description,'offscreen':True,'noWaylandDisplay':True,'sourceDirectoryGone':True};report['processes'].append(row)
   assert proc.joinpath('stat').read_text().split(') ',1)[1].split()[19]==start
   signal.pidfd_send_signal(fd,signal.SIGTERM,None,0)
   until=time.monotonic()+5
   while proc.exists() and time.monotonic()<until:time.sleep(.05)
   row['gone']=not proc.exists();assert row['gone']
  finally:os.close(fd)
 report['passed']=True
except Exception as error:report['error']=repr(error)
(root/'orphan-retirement.json').write_text(json.dumps(report,indent=2)+'\n');print(root/'orphan-retirement.json');raise SystemExit(not report['passed'])
