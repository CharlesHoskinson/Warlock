"""Private native-protocol fixtures; no hardware, desktop buses or power effects."""
import json,os,pathlib,signal,sys

def audio_config(root,environment):
 root=pathlib.Path(root);root.mkdir(parents=True,exist_ok=True,mode=0o700);(root/'pulse').mkdir(exist_ok=True,mode=0o700)
 env={**environment,'PIPEWIRE_RUNTIME_DIR':str(root),'PIPEWIRE_REMOTE':'warlock-audio','PIPEWIRE_CORE':'warlock-audio','PULSE_SERVER':'unix:'+str(root/'pulse/native'),'PULSE_RUNTIME_PATH':str(root/'pulse'),'DISABLE_RTKIT':'1'}
 (root/'core.conf').write_text('''context.properties = { core.daemon = true core.name = warlock-audio }
context.spa-libs = { support.* = support/libspa-support audio.convert.* = audioconvert/libspa-audioconvert }
context.modules = [
 { name = libpipewire-module-protocol-native }
 { name = libpipewire-module-client-node }
 { name = libpipewire-module-adapter }
 { name = libpipewire-module-metadata }
 { name = libpipewire-module-access args = { access.force = unrestricted } }
]
context.objects = [
 { factory = metadata args = { metadata.name = default metadata.values = [ { key = default.audio.sink value = { name = warlock.null } } ] } }
 { factory = adapter args = { factory.name = support.null-audio-sink node.name = warlock.null node.description = "Warlock private audio" media.class = Audio/Sink audio.position = [ FL FR ] } }
]
''')
 (root/'pulse.conf').write_text('''context.properties = { core.name = warlock-pulse }
context.spa-libs = { support.* = support/libspa-support audio.convert.* = audioconvert/libspa-audioconvert }
context.modules = [
 { name = libpipewire-module-protocol-native }
 { name = libpipewire-module-client-node }
 { name = libpipewire-module-adapter }
 { name = libpipewire-module-metadata }
 { name = libpipewire-module-protocol-pulse }
]
pulse.properties = { server.address = [ "unix:'''+str(root/'pulse/native')+'''" ] }
''')
 return env

MANAGER_XML='''<node><interface name="org.freedesktop.login1.Manager">
<method name="CanSuspend"><arg type="s" direction="out"/></method><method name="CanReboot"><arg type="s" direction="out"/></method><method name="CanPowerOff"><arg type="s" direction="out"/></method>
<method name="GetSessionByPID"><arg type="u" direction="in"/><arg type="o" direction="out"/></method>
<method name="Suspend"><arg type="b" direction="in"/></method><method name="Reboot"><arg type="b" direction="in"/></method><method name="PowerOff"><arg type="b" direction="in"/></method><method name="TerminateSession"><arg type="s" direction="in"/></method>
</interface></node>'''
SESSION_XML='''<node><interface name="org.freedesktop.login1.Session"><method name="Lock"/>
<property name="Id" type="s" access="read"/><property name="Name" type="s" access="read"/><property name="State" type="s" access="read"/><property name="LockedHint" type="b" access="read"/><property name="User" type="(uo)" access="read"/>
</interface></node>'''
NETWORK_XML='''<node><interface name="org.freedesktop.NetworkManager"><method name="Enable"><arg type="b" direction="in"/></method><method name="GetPermissions"><arg type="a{ss}" direction="out"/></method><property name="NetworkingEnabled" type="b" access="read"/><property name="State" type="u" access="read"/></interface></node>'''
CONTROL_XML='''<node><interface name="org.warlock.SystemFixture"><method name="Read"><arg type="s" direction="out"/></method><method name="Mode"><arg type="s" direction="in"/></method><method name="Quit"/></interface></node>'''

def serve(state_path):
 import gi
 gi.require_version('Gio','2.0');from gi.repository import Gio,GLib
 address=os.environ['DBUS_SESSION_BUS_ADDRESS'];connection=Gio.DBusConnection.new_for_address_sync(address,Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None);connection.set_exit_on_close(False)
 loop=GLib.MainLoop();session='/org/freedesktop/login1/session/warlock';data={'locked':False,'state':'active','calls':[],'mode':'normal','owner':connection.get_unique_name(),'networkEnabled':True}
 def save():pathlib.Path(state_path).write_text(json.dumps(data))
 def method(conn,sender,path,interface,name,args,invocation):
  values=args.unpack()
  if name in ['CanSuspend','CanReboot','CanPowerOff']:invocation.return_value(GLib.Variant('(s)',('yes' if name!='CanPowerOff' else 'no',)));return
  if name=='GetSessionByPID':invocation.return_value(GLib.Variant('(o)',(session,)));return
  if name=='Read':invocation.return_value(GLib.Variant('(s)',(json.dumps(data),)));return
  if name=='GetPermissions':invocation.return_value(GLib.Variant('(a{ss})',({'org.freedesktop.NetworkManager.enable-disable-network':'yes'},)));return
  if name=='Mode':
   data['mode']=values[0]
   if values[0]=='network':
    handles.append(connection.register_object('/org/freedesktop/NetworkManager',Gio.DBusNodeInfo.new_for_xml(NETWORK_XML).interfaces[0],method,prop,None))
    result=connection.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','RequestName',GLib.Variant('(su)',('org.freedesktop.NetworkManager',4)),GLib.VariantType.new('(u)'),0,1000,None).unpack()[0];assert result==1
   save();invocation.return_value(None);return
  if name=='Quit':invocation.return_value(None);GLib.idle_add(lambda:loop.quit() or False);return
  data['calls'].append({'operation':name,'values':list(values),'sender':sender});save()
  if data['mode']=='refused':invocation.return_dbus_error('org.freedesktop.DBus.Error.AccessDenied','Private fixture refusal');return
  if data['mode']=='unknown':invocation.return_dbus_error('org.freedesktop.DBus.Error.NoReply','Private fixture lost response');return
  if name=='Enable':data['networkEnabled']=values[0]
  if name=='Lock':data['locked']=True
  if name=='TerminateSession':data['state']='closing'
  save();invocation.return_value(None)
 def prop(conn,sender,path,interface,name):
  if interface=='org.freedesktop.NetworkManager':return {'NetworkingEnabled':GLib.Variant('b',data['networkEnabled']),'State':GLib.Variant('u',70 if data['networkEnabled'] else 10)}[name]
  return {'Id':GLib.Variant('s','warlock'),'Name':GLib.Variant('s','Warlock private session'),'State':GLib.Variant('s',data['state']),'LockedHint':GLib.Variant('b',data['locked']),'User':GLib.Variant('(uo)',(os.getuid(),'/org/freedesktop/login1/user/_'+str(os.getuid())))}[name]
 handles=[]
 for path,xml in [('/org/freedesktop/login1',MANAGER_XML),(session,SESSION_XML),('/org/warlock/SystemFixture',CONTROL_XML)]:
  handles.append(connection.register_object(path,Gio.DBusNodeInfo.new_for_xml(xml).interfaces[0],method,prop if path==session else None,None))
 for name in ['org.freedesktop.login1','org.warlock.SystemFixture']:
  reply=connection.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','RequestName',GLib.Variant('(su)',(name,4)),GLib.VariantType.new('(u)'),0,1000,None).unpack()[0];assert reply==1
 save();print('ready',flush=True)
 for sig in [signal.SIGTERM,signal.SIGINT]:GLib.unix_signal_add(GLib.PRIORITY_DEFAULT,sig,lambda:loop.quit() or False)
 try:loop.run()
 finally:
  for handle in handles:connection.unregister_object(handle)
  connection.close_sync(None)
if __name__=='__main__':serve(sys.argv[1])
