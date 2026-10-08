"""Actual C observer on a private session bus; no host settings or activation."""
import json,os,pathlib,select,shlex,subprocess,tempfile,threading,time
from gi.repository import Gio,GLib

ROOT=pathlib.Path(__file__).resolve().parents[1]
XML='''<node><interface name="org.freedesktop.portal.Settings"><method name="ReadOne"><arg type="s" direction="in"/><arg type="s" direction="in"/><arg type="v" direction="out"/></method><signal name="SettingChanged"><arg type="s"/><arg type="s"/><arg type="v"/></signal></interface></node>'''
PROBE=r'''
#include <stdio.h>
#include "motion-preference.h"
static GMainLoop *loop;
static void publish(const char *frame) {puts(frame);fflush(stdout);}
static gboolean done(GIOChannel *channel,GIOCondition condition,gpointer data) {
 (void)channel;(void)condition;(void)data;g_main_loop_quit(loop);return G_SOURCE_REMOVE;
}
int main(void) {
 loop=g_main_loop_new(NULL,FALSE);motion_preference_start(publish);
 GIOChannel *input=g_io_channel_unix_new(0);g_io_add_watch(input,G_IO_IN|G_IO_HUP,done,NULL);
 g_main_loop_run(loop);g_io_channel_unref(input);g_main_loop_unref(loop);return 0;
}
'''
checks={};frames=[];pending=b'';bus=probe=None;loop=GLib.MainLoop();thread=None;connection=None
def check(name,condition):
 checks[name]=bool(condition)
 assert condition,name
def wait(profile,source):
 global pending
 deadline=time.monotonic()+3
 while time.monotonic()<deadline:
  if frames and frames[-1]['profile']==profile and frames[-1]['source']==source:return frames[-1]
  assert probe.poll() is None,'observer unexpectedly exited'
  if select.select([probe.stdout],[],[],.05)[0]:
   chunk=os.read(probe.stdout.fileno(),4096);assert chunk;pending+=chunk
   while b'\n' in pending:
    line,pending=pending.split(b'\n',1);frames.append(json.loads(line))
 raise AssertionError(('native observer deadline',profile,source,frames))
try:
 with tempfile.TemporaryDirectory(prefix='warlock-motion-') as directory:
  work=pathlib.Path(directory);source=work/'probe.c';source.write_text(PROBE);binary=work/'probe'
  flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gtk+-3.0','gio-2.0'],text=True))
  subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-I'+str(ROOT/'native'),str(source),'-o',str(binary),*flags],check=True,capture_output=True)
  bus=subprocess.Popen(['dbus-daemon','--session','--nofork','--print-address'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  address=bus.stdout.readline().strip();assert address.startswith('unix:')
  connection=Gio.DBusConnection.new_for_address_sync(address,Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
  def bus_call(method,parameters):
   return connection.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus',method,parameters,None,Gio.DBusCallFlags.NO_AUTO_START,1000,None)
  current=GLib.Variant('u',1)
  def method(connection_,sender,path,interface,name,parameters,invocation):
   assert name=='ReadOne' and parameters.unpack()==('org.freedesktop.appearance','reduced-motion')
   invocation.return_value(GLib.Variant('(v)',(current,)))
  registration=connection.register_object('/org/freedesktop/portal/desktop',Gio.DBusNodeInfo.new_for_xml(XML).interfaces[0],method,None,None)
  assert bus_call('RequestName',GLib.Variant('(su)',('org.freedesktop.portal.Desktop',0))).unpack()==(1,)
  thread=threading.Thread(target=loop.run);thread.start()
  probe=subprocess.Popen([str(binary)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={**os.environ,'DBUS_SESSION_BUS_ADDRESS':address,'DISPLAY':'','WAYLAND_DISPLAY':''})
  wait('reduced','portal');check('actualReadOneOverridesFallback',True)
  def change(value,profile,source='portal'):
   global current
   current=value;before=frames[-1]['serial']
   connection.emit_signal(None,'/org/freedesktop/portal/desktop','org.freedesktop.portal.Settings','SettingChanged',GLib.Variant('(ssv)',('org.freedesktop.appearance','reduced-motion',value)))
   result=wait(profile,source);check('serial-'+str(len(checks)),int(result['serial'])>int(before))
  change(GLib.Variant('u',0),'full');check('actualSettingChangedUpdatesPreference',True)
  change(GLib.Variant('u',1),'reduced')
  change(GLib.Variant('u',9),'full');check('unknownPortalValueMeansNoPreference',True)
  change(GLib.Variant('u',1),'reduced')
  change(GLib.Variant('b',True),'full','gtk');check('malformedPortalValueFallsBack',True)
  change(GLib.Variant('u',1),'reduced')
  bus_call('ReleaseName',GLib.Variant('(s)',('org.freedesktop.portal.Desktop',)));wait('full','gtk');check('ownerLossRetiresPortalPreference',True)
  bus_call('RequestName',GLib.Variant('(su)',('org.freedesktop.portal.Desktop',0)));wait('reduced','portal');check('newOwnerIsReadAgain',True)
  probe.stdin.write(b'q\n');probe.stdin.flush();probe.wait(timeout=3);check('observerNormalExit',probe.returncode==0)
  connection.unregister_object(registration);loop.quit();thread.join(timeout=3);connection.close_sync(None);connection=None
  bus.terminate();bus.wait(timeout=3);bus=None
  check('strictTypedObservationFrames',all(set(row)=={'protocolVersion','kind','serial','profile','source'} and row['protocolVersion']==3 and row['kind']=='host-motion-preference' for row in frames))
  print(json.dumps({'passed':True,'checks':checks,'frames':frames,'scope':'Actual C preference observer/private portal ReadOne and signals; native GTK preference and window presentation remain separate.'}))
finally:
 if probe is not None and probe.poll() is None:probe.terminate();probe.wait(timeout=3)
 if thread is not None and thread.is_alive():loop.quit();thread.join(timeout=3)
 if connection is not None:connection.close_sync(None)
 if bus is not None and bus.poll() is None:bus.terminate();bus.wait(timeout=3)
