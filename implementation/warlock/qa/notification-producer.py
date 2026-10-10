"""Two private native D-Bus producers for the protected GUI recording."""
import json, os, pathlib, sys
import gi
gi.require_version('Gio','2.0');from gi.repository import Gio,GLib
control=pathlib.Path(sys.argv[1]);log=control.with_suffix('.events.jsonl');last=0
connections=[];loop=GLib.MainLoop()
def emit(value):
 with log.open('a') as stream:stream.write(json.dumps(value)+'\n')
for index in range(2):
 connection=Gio.DBusConnection.new_for_address_sync(os.environ['DBUS_SESSION_BUS_ADDRESS'],Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
 connection.set_exit_on_close(False)
 connection.signal_subscribe(None,'org.freedesktop.Notifications',None,'/org/freedesktop/Notifications',None,0,
  lambda *args,index=index:emit({'kind':'signal','producer':index,'signal':args[4],'values':args[5].unpack()}))
 connections.append(connection)
emit({'kind':'ready','producers':[connection.get_unique_name() for connection in connections]})
def tick():
 global last
 if not control.exists():return True
 request=json.loads(control.read_text())
 if request['serial']==last:return True
 last=request['serial']
 if request['op']=='quit':loop.quit();return False
 if request['op']=='notify':
  identifier=connections[request['producer']].call_sync('org.freedesktop.Notifications','/org/freedesktop/Notifications','org.freedesktop.Notifications','Notify',
   GLib.Variant('(susssasa{sv}i)',('Warlock fixture',request.get('replaces',0),'',request['summary'],'A real native notification',['open',request['label']],{'urgency':GLib.Variant('y',request.get('urgency',1))},request.get('timeout',0))),GLib.VariantType.new('(u)'),0,2000,None).unpack()[0]
  emit({'kind':'notified','serial':last,'id':identifier,'producer':request['producer']})
 return True
GLib.timeout_add(20,tick)
try:loop.run()
finally:
 for connection in connections:connection.close_sync(None)
