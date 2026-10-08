"""Bounded actual private PipeWire and login1 protocols, current adapter admission."""
import copy,importlib.util,json,os,pathlib,subprocess,sys,tempfile,time
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from system_menu import Menu,Refused
spec=importlib.util.spec_from_file_location('system_fixture',ROOT/'qa/system-menu-provider.py');fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
checks=[]
def check(name,value):
 assert value,name
 checks.append(name)
class Client:
 bound={'lifetime':'1','session':'1','frontend':'1'}
 def verify_process(self):pass
 def verify_paths(self):pass
serial=10
def request(intent=None):
 global serial
 serial+=1
 return {'protocolVersion':3,'kind':'system-menu-effect' if intent else 'system-menu-request','binding':Client.bound,'requestId':str(serial),**({'intent':intent} if intent else {})}
def effect(menu,snapshot,operation,value=0):return menu.effect(request({'service':snapshot['service'],'revision':snapshot['revision'],'operation':operation,'value':value}),Client())
def wait(fn):
 end=time.monotonic()+3
 while time.monotonic()<end:
  result=fn()
  if result:return result
  time.sleep(.01)
 raise AssertionError('Private native provider deadline')
children=[];streams=[];environment=os.environ.copy()
with tempfile.TemporaryDirectory(prefix='warlock-system-') as temporary:
 root=pathlib.Path(temporary);os.chmod(root,0o700)
 env=fixture.audio_config(root,os.environ)
 def launch(args):
  stream=open(root/('child-'+str(len(children))+'.log'),'wb');streams.append(stream)
  child=subprocess.Popen(args,env=env,stdout=stream,stderr=stream);children.append(child);return child
 try:
  bus=launch(['dbus-daemon','--session','--nofork','--address=unix:path='+str(root/'bus')]);wait(lambda:(root/'bus').exists());env['DBUS_SESSION_BUS_ADDRESS']='unix:path='+str(root/'bus');env['DBUS_SYSTEM_BUS_ADDRESS']=env['DBUS_SESSION_BUS_ADDRESS']
  core=launch(['/usr/bin/pipewire','-c',str(root/'core.conf')]);wait(lambda:(root/'warlock-audio').exists())
  pulse=launch(['/usr/bin/pipewire-pulse','-c',str(root/'pulse.conf')]);wait(lambda:(root/'pulse/native').exists())
  provider=launch(['/usr/bin/python3','-B',str(ROOT/'qa/system-menu-provider.py'),str(root/'state.json')]);wait(lambda:(root/'state.json').exists())
  subprocess.run(["/usr/bin/pactl","--server="+env["PULSE_SERVER"],"set-default-sink","warlock.null"],env=env,check=True,capture_output=True,timeout=2)
  wait(lambda:json.loads(subprocess.run(["/usr/bin/pactl","--server="+env["PULSE_SERVER"],"--format=json","info"],env=env,check=True,capture_output=True,text=True,timeout=1).stdout)["default_sink_name"]=="warlock.null")
  os.environ.update(env)
  with Menu() as menu:
   observed=menu.read(request(),Client())['snapshot'];print('OBSERVED',json.dumps(observed),file=sys.stderr)
   check('Real private audio exposes current volume',observed['volume'] is not None)
   check('Absent native network service is unavailable',observed['network'] is None)
   check('Native power capabilities are observed, including refused shutdown',observed['power']=={'suspend':'yes','reboot':'yes','poweroff':'no'})
   check('Own native session state is observed',observed['session'] is not None and not observed['session']['locked'])
   result=effect(menu,observed,'volume-set',25);check('Volume commit follows actual native readback',result['status']=='Committed' and result['snapshot']['volume']['percent']==25)
   duplicate=effect(menu,observed,'volume-set',25);check('Old revision never replays volume change',duplicate['status']=='Refused')
   current=result['snapshot'];muted=effect(menu,current,'volume-mute',1);check('Mute commit follows actual native readback',muted['status']=='Committed' and muted['snapshot']['volume']['muted'])
   check('Unavailable network request has no effect',effect(menu,muted['snapshot'],'network-enable',0)['status']=='Refused' and json.loads((root/'state.json').read_text())['calls']==[])
   locked=effect(menu,muted['snapshot'],'session-lock');check('Lock commit follows own-session LockedHint',locked['status']=='Committed' and locked['snapshot']['session']['locked'])
   submitted=effect(menu,locked['snapshot'],'suspend');check('Power return is Submitted rather than invented observed transition',submitted['status']=='Submitted')
   before=json.loads((root/'state.json').read_text())['calls'];check('Duplicate power intent dispatches once',effect(menu,locked['snapshot'],'suspend')['status']=='Refused' and json.loads((root/'state.json').read_text())['calls']==before)
   check('Refused native capability never submits',effect(menu,submitted['snapshot'],'poweroff')['status']=='Refused' and json.loads((root/'state.json').read_text())['calls']==before)
   import gi
   gi.require_version('Gio','2.0');from gi.repository import Gio,GLib
   def mode(value):menu.call('org.warlock.SystemFixture','/org/warlock/SystemFixture','org.warlock.SystemFixture','Mode','(s)',(value,),'()',time.monotonic()+1)
   mode('refused');refused=effect(menu,menu.observe(),'reboot');check('Explicit native denial is Refused',refused['status']=='Refused')
   mode('unknown');unknown=effect(menu,menu.observe(),'session-logout');check('Lost native response is Unknown',unknown['status']=='Unknown')
   before=json.loads((root/'state.json').read_text())['calls'];check('Unknown does not replay with another request ID',effect(menu,unknown['snapshot'],'session-logout')['status']=='Refused' and json.loads((root/'state.json').read_text())['calls']==before)
   bad=request({'service':menu.service,'revision':str(menu.revision),'operation':'volume-set','value':25});bad['intent']['path']='/tmp/foreign'
   try:menu.effect(bad,Client());raise AssertionError('Frontend path accepted')
   except Refused:checks.append('Frontend cannot choose commands, paths or native session identities')
   mode('network');network=menu.observe();check('Available native network shows current state and permission',network['network']=={'enabled':True,'state':'Connected','permission':'yes'})
   disabled=effect(menu,network,'network-enable',0);check('Network commit follows actual owner-bound readback',disabled['status']=='Committed' and disabled['snapshot']['network']['enabled'] is False)
   before=json.loads((root/'state.json').read_text())['calls'];check('Old network revision never replays Enable',effect(menu,network,'network-enable',0)['status']=='Refused' and json.loads((root/'state.json').read_text())['calls']==before)
   enabled=effect(menu,disabled['snapshot'],'network-enable',1);check('Fresh explicit network enable observes current state',enabled['status']=='Committed' and enabled['snapshot']['network']['enabled'] is True)
   provider.terminate();provider.wait(timeout=2);current=menu.observe();check('Disappearing native owner withdraws session/power',current['session'] is None and current['power'] is None)
  # Preserve a refusing system-bus override; no fallback to the private session.
  os.environ['DBUS_SYSTEM_BUS_ADDRESS']='unix:path='+str(root/'absent')
  with Menu() as absent:check('Refusing system-bus override never falls back',absent.observe()['power'] is None)
 except Exception:
  for i,stream in enumerate(streams):
   stream.flush();print('CHILD',i,(root/('child-'+str(i)+'.log')).read_text()[-1800:],file=sys.stderr)
  raise
 finally:
  os.environ.clear();os.environ.update(environment)
  for child in reversed(children):
   if child.poll() is None:child.terminate()
   try:child.wait(timeout=3)
   except subprocess.TimeoutExpired:child.kill();child.wait()
  for stream in streams:stream.close()
print(json.dumps({'passed':True,'checks':checks,'scenario':'ux-032','evidenceScope':'Actual private native audio and D-Bus protocol providers; no GUI, hardware or release acceptance'}))
