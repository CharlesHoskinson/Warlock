"""Actual late private D-Bus activation after provisional drain; no GUI."""
import hashlib,json,os,resource,shutil,signal,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,private_runtime
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from private_bus import Activations,Refused,bounded_gio
from activation_import import identity,live
from gi.repository import Gio,GLib
ROOT=Path(__file__).resolve().parent;OUT=ROOT/('post-retirement-'+str(time.time_ns()));OUT.mkdir();report={'passed':False,'nativeAcceptance':False,'actualPrivateBusOnly':True,'checks':[]}
try:
 for name,ignore in [('late-normal',False),('late-fallback',True)]:
  case=OUT/name;case.mkdir(mode=0o700);runtime=private_runtime();manager=None;bus=None;wrapper=None;controller=None
  try:
   service=case/'service.py';service.write_text('''from gi.repository import Gio,GLib
import os,signal
loop=GLib.MainLoop();ignore=os.environ.get('CPU_IGNORE_TERM')=='1'
signal.signal(signal.SIGTERM,signal.SIG_IGN if ignore else lambda *_:loop.quit())
bus=Gio.DBusConnection.new_for_address_sync(os.environ['DBUS_SESSION_BUS_ADDRESS'],Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
bus.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','RequestName',GLib.Variant('(su)',('org.elm.LateActivation',0)),None,Gio.DBusCallFlags.NONE,1000,None)
if not ignore:GLib.timeout_add(150,lambda:(loop.quit(),False)[1])
loop.run();bus.close_sync(None)
''')
   manager=Activations(runtime,case);config=manager.install({'org.elm.LateActivation':(['/usr/bin/python3','-B',str(service)],service)});env=dict(os.environ,XDG_RUNTIME_DIR=str(runtime),DBUS_SESSION_BUS_ADDRESS='unix:path='+str(runtime/'bus'),CPU_IGNORE_TERM='1' if ignore else '0')
   with (case/'bus.stdout').open('wb') as out,(case/'bus.stderr').open('wb') as err:
    bus=subprocess.Popen(['/usr/bin/dbus-daemon','--nofork','--config-file='+str(config),'--address='+env['DBUS_SESSION_BUS_ADDRESS']],env=env,stdout=out,stderr=err,start_new_session=True)
    deadline=time.monotonic()+3
    while not (runtime/'bus').exists():assert time.monotonic()<deadline and bus.poll() is None;time.sleep(.01)
    busrow=identity(bus.pid);manager.connect(busrow,deadline)
    controller=bounded_gio(lambda c:Gio.DBusConnection.new_for_address_sync(env['DBUS_SESSION_BUS_ADDRESS'],Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,c),deadline)
    provisional=manager.close(deadline);assert provisional==[]
    # Another real private bus client starts a real service after provisional close.
    result=bounded_gio(lambda c:controller.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','StartServiceByName',GLib.Variant('(su)',('org.elm.LateActivation',0)),None,Gio.DBusCallFlags.NONE,1000,c),deadline).unpack();assert result==(1,)
    snapshots=manager.snapshots();assert len(snapshots)==1;wrapper=snapshots[0][2][0]['identity']
    try:manager.final_after_retirement(busrow)
    except Refused:pass
    else:raise AssertionError('live bus cannot qualify final gate')
    if not ignore:
     while live(wrapper):assert time.monotonic()<deadline;time.sleep(.01)
    bounded_gio(lambda c:controller.close_sync(c),deadline);controller=None
    bus.terminate();assert bus.wait(timeout=max(.001,deadline-time.monotonic()))==0
    if ignore:
     try:manager.final_after_retirement(busrow)
     except Refused:pass
     else:raise AssertionError('late live wrapper must refuse after bus retirement')
     if live(wrapper):os.kill(wrapper['pid'],signal.SIGTERM)
     while live(wrapper):assert time.monotonic()<deadline;time.sleep(.01)
     try:manager.final_after_retirement(busrow)
     except Refused:pass
     else:raise AssertionError('real late fallback must refuse final gate')
     final=json.loads((case/'activation-post-retirement.json').read_text());assert final['passed'] is False and final['records'][0]['terminal']['fallback'] is True
    else:
     final=manager.final_after_retirement(busrow);assert final['passed'] and len(final['records'])==1 and final['records'][0]['terminal']['childExitCode']==0
     wrong=dict(busrow,start=str(int(busrow['start'])+1))
     try:manager.final_after_retirement(wrong)
     except Refused:pass
     else:raise AssertionError('wrong original bus identity must refuse')
     manager.final_after_retirement(busrow)
    assert time.monotonic()<deadline
    report['checks'].append({'name':name,'passed':True,'provisionalCount':0,'finalCount':1,'busExitCode':bus.returncode,'case':str(case),'actualWrapper':wrapper})
  finally:
   if wrapper and live(wrapper):os.kill(wrapper['pid'],signal.SIGTERM);time.sleep(.6)
   if bus and bus.poll() is None:bus.terminate();bus.wait(timeout=1)
   if controller:
    try:bounded_gio(lambda c:controller.close_sync(c),time.monotonic()+.5)
    except Exception:pass
   shutil.rmtree(runtime)
 report['passed']=True
finally:
 report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'private_bus.py',ROOT/'activation-supervisor.py',ROOT/'owned_bus_host.py',Path('/usr/bin/dbus-daemon')]};(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json')
