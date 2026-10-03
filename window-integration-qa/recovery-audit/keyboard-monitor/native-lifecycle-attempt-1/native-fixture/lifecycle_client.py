#!/usr/bin/env python3
"""Registered public monitor control client; native packets come from Wayland."""
import json,os,sys,time
from pathlib import Path
from gi.repository import Gio,GLib
runtime=Path(os.environ['XDG_RUNTIME_DIR'])
assert str(runtime).startswith('/tmp/kbn-')
assert os.environ['DBUS_SESSION_BUS_ADDRESS']=='unix:path='+str(runtime/'bus')
assert len(sys.argv) in (3,4)
name=sys.argv[3] if len(sys.argv)==4 else 'org.omarchy.NativePolicy'+sys.argv[1]+'.KeyboardMonitor'
output=Path(sys.argv[2]);output.write_text('');output.chmod(0o600)
bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
owner=bus.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','RequestName',GLib.Variant('(su)',(name,4)),None,Gio.DBusCallFlags.NONE,3000,None).unpack()[0]
assert owner in (1,3)  # second live caller may wait without owning the name
def packet(connection,sender,path,interface,member,parameters,user_data):
    released,mask,sym,unicode,keycode=parameters.unpack()
    with output.open('a') as stream:stream.write(json.dumps(dict(time=time.monotonic(),released=released,mask=mask,keysym=sym,unicode=unicode,keycode=keycode))+'\n')
bus.signal_subscribe('org.freedesktop.a11y.Manager','org.freedesktop.a11y.KeyboardMonitor','KeyEvent','/org/freedesktop/a11y/Manager',None,Gio.DBusSignalFlags.NONE,packet,None)
loop=GLib.MainLoop()
def request(fd,condition):
    if condition&GLib.IOCondition.HUP:loop.quit();return False
    line=sys.stdin.readline()
    if not line:loop.quit();return False
    try:
        command=json.loads(line);operation=command['operation']
        if operation in ('claim','release'):
            bus.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus',
                'RequestName' if operation=='claim' else 'ReleaseName',
                GLib.Variant('(su)',(name,4)) if operation=='claim' else GLib.Variant('(s)',(name,)),
                None,Gio.DBusCallFlags.NONE,3000,None)
            print(json.dumps({'id':command.get('id'),'pass':True}),flush=True);return True
        if operation=='grabs':method='SetKeyGrabs';args=GLib.Variant('(aua(uu))',(command.get('modifiers',[]),command.get('strokes',[])))
        elif operation in ('watch','unwatch','grab','ungrab'):
            method={'watch':'WatchKeyboard','unwatch':'UnwatchKeyboard','grab':'GrabKeyboard','ungrab':'UngrabKeyboard'}[operation];args=GLib.Variant('()',())
        elif operation=='sync':print(json.dumps({'id':command.get('id'),'pass':True}),flush=True);return True
        else:raise ValueError('unknown public monitor operation')
        result=bus.call_sync('org.freedesktop.a11y.Manager','/org/freedesktop/a11y/Manager','org.freedesktop.a11y.KeyboardMonitor',method,args,None,Gio.DBusCallFlags.NONE,3000,None)
        print(json.dumps({'id':command.get('id'),'pass':True,'result':result.unpack()}),flush=True)
    except Exception as error:print(json.dumps({'id':command.get('id') if 'command' in locals() else None,'pass':False,'error':repr(error)}),flush=True)
    return True
GLib.io_add_watch(sys.stdin,GLib.IOCondition.IN|GLib.IOCondition.HUP,request)
print(json.dumps({'ready':True,'name':name,'uniqueName':bus.get_unique_name()}),flush=True)
loop.run()
