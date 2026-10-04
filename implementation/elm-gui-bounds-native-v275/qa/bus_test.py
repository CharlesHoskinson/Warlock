import hashlib,json,os,resource,socket,struct,subprocess,sys,tempfile,time,traceback
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'));import bus_policy
OUT=ROOT/'qa'/('bus-'+str(time.time_ns()));OUT.mkdir(mode=0o700);temporary=tempfile.TemporaryDirectory(prefix='elm-bounds-bus-');runtime=Path(temporary.name);r={'passed':False,'nativeAcceptance':False,'checks':[]};p=None
try:
 address='unix:path='+str(runtime/'bus');config=OUT/'bus.conf';config.write_text(bus_policy.configuration(address));config.chmod(0o600)
 assert '<servicedir' not in config.read_text() and '<include' not in config.read_text();r['checks'].append('no service directory or includes')
 with (OUT/'daemon.stdout').open('wb') as stdout,(OUT/'daemon.stderr').open('wb') as stderr:
  p=subprocess.Popen(['/usr/bin/dbus-daemon','--nofork','--config-file='+str(config)],stdout=stdout,stderr=stderr)
  deadline=time.monotonic()+3
  while not (runtime/'bus').exists() and time.monotonic()<deadline:
   assert p.poll() is None;time.sleep(.01)
  with socket.socket(socket.AF_UNIX) as peer:
   peer.settimeout(1);peer.connect(str(runtime/'bus'));pid,uid,gid=struct.unpack('3i',peer.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12));assert pid==p.pid and uid==os.getuid();r['checks'].append('actual socket credential and owned daemon')
  for service in ['org.a11y.Bus','org.freedesktop.portal.Desktop','org.freedesktop.portal.Documents']:
   before=time.monotonic();c=subprocess.run(['/usr/bin/gdbus','call','--address',address,'--dest','org.freedesktop.DBus','--object-path','/org/freedesktop/DBus','--method','org.freedesktop.DBus.StartServiceByName',service,'0'],capture_output=True,text=True,timeout=3);assert c.returncode!=0 and 'ServiceUnknown' in c.stderr and time.monotonic()-before<3;r['checks'].append(service+' actual unavailable without child activation')
  children=Path('/proc',str(p.pid),'task',str(p.pid),'children').read_text();assert children.strip()=='';r['checks'].append('owned daemon has no activated children')
  p.terminate();assert p.wait(timeout=3)==0;r['checks'].append('normal daemon termination')
 r['passed']=True
except Exception as e:r.update(error=repr(e),traceback=traceback.format_exc())
finally:
 if p is not None and p.poll() is None:p.terminate();p.wait(timeout=3)
 temporary.cleanup();r['privateBusRuntimeGone']=not runtime.exists();r['passed']=r['passed'] and r['privateBusRuntimeGone']
 r['artifacts']={str(f.relative_to(OUT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in OUT.rglob('*') if f.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])
