"""Actual private daemon activation/authentication/wait-status CPU test; no GUI."""
import hashlib,json,os,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,private_runtime
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from private_bus import Activations,Refused
from activation_import import identity
ROOT=Path(__file__).resolve().parent;OUT=ROOT/('private-bus-'+str(time.time_ns()));OUT.mkdir();runtime=private_runtime();report={'passed':False,'nativeAcceptance':False,'actualPrivateBusNoGUI':True,'checks':[]};bus=None;manager=None;ignore='--ignore-term' in sys.argv
try:
 service=OUT/'actual-service.py';service.write_text('''from gi.repository import Gio,GLib
import os,signal
loop=GLib.MainLoop()
signal.signal(signal.SIGTERM,signal.SIG_IGN if os.environ.get('CPU_IGNORE_TERM')=='1' else lambda *_:loop.quit())
bus=Gio.DBusConnection.new_for_address_sync(os.environ['DBUS_SESSION_BUS_ADDRESS'],Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
bus.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','RequestName',GLib.Variant('(su)',('org.elm.CPUActivation',0)),None,Gio.DBusCallFlags.NONE,1000,None)
loop.run()
bus.close_sync(None)
''')
 manager=Activations(runtime,OUT);config=manager.install({'org.elm.CPUActivation':(['/usr/bin/python3','-B',str(service)],service)})
 env=dict(os.environ,XDG_RUNTIME_DIR=str(runtime),DBUS_SESSION_BUS_ADDRESS='unix:path='+str(runtime/'bus'),CPU_IGNORE_TERM='1' if ignore else '0')
 with (OUT/'bus.stdout').open('wb') as out,(OUT/'bus.stderr').open('wb') as err:
  bus=subprocess.Popen(['/usr/bin/dbus-daemon','--nofork','--config-file='+str(config),'--address='+env['DBUS_SESSION_BUS_ADDRESS']],env=env,stdout=out,stderr=err,start_new_session=True)
  deadline=time.monotonic()+3
  while not (runtime/'bus').exists():assert time.monotonic()<deadline and bus.poll() is None;time.sleep(.01)
  manager.connect(identity(bus.pid),deadline)
  assert manager.call('StartServiceByName',('org.elm.CPUActivation',0),'(su)',deadline)[0]==1
  proof=manager.authenticate('org.elm.CPUActivation',deadline);assert proof['identity']['pid']!=bus.pid
  report['checks'].append({'name':'real private daemon activated unchanged pinned command; authenticated connection PID/start/UID','passed':True,'proof':proof})
  try:manager.authenticate('org.freedesktop.DBus',deadline)
  except Refused:pass
  else:raise AssertionError('foreign connection cannot authenticate as activation child')
  report['checks'].append({'name':'bus owner is not an activation child','passed':True})
  try:cleanup=manager.close(time.monotonic()+3)
  except Refused as error:
   if not ignore:raise
   report['callerRefusedFallback']=repr(error);cleanup=json.loads((OUT/'activation-cleanup.json').read_text())
  else:assert not ignore,'ignoreTERM fallback must fail caller cleanup gate'
  assert len(cleanup)==1
  terminal=cleanup[0]['terminal'];assert terminal['childExitCode']==(-9 if ignore else 0) and terminal['cancelled'] is True and terminal['fallback'] is ignore
  report['checks'].append({'name':('actual ignoreTERM service forces real SIGKILL and caller refuses positive cleanup' if ignore else 'real SIGTERM handler exits0 and supervisor reaps actual wait status, cancellation remains explicit'),'passed':True,'cleanup':cleanup})
  bus.terminate();assert bus.wait(timeout=1)==0
  report['checks'].append({'name':'owned private bus normal shutdown exit0','passed':True})
 report['passed']=True
finally:
 if manager and hasattr(manager,'busrow'):
  try:manager.close(time.monotonic()+3)
  except Exception as error:report['repeatedExpectedFallbackRefusal' if ignore else 'cleanupError']=repr(error)
 if bus and bus.poll() is None:bus.kill();bus.wait(timeout=1)
 shutil.rmtree(runtime)
 paths=[Path(__file__),ROOT/'private_bus.py',ROOT/'activation-supervisor.py',ROOT/'activation_import.py',Path('/usr/bin/dbus-daemon'),Path('/usr/bin/python3'),Path('/usr/share/dbus-1/session.conf')]
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
