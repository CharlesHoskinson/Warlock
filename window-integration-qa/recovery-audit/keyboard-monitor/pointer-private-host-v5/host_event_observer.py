#!/usr/bin/env python3
"""Private registered watch-only protocol client; records real directed packets."""
import json,os,time
from pathlib import Path
from gi.repository import Gio,GLib
from private_runtime_guard import checked_runtime
runtime=checked_runtime()
bus=Gio.bus_get_sync(Gio.BusType.SESSION,None)
name='org.omarchy.NativeKeyboardQA.KeyboardMonitor'
result=bus.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','RequestName',GLib.Variant('(su)',(name,4)),None,Gio.DBusCallFlags.NONE,3000,None).unpack()[0]
assert result==1
output=Path(os.environ['KEYBOARD_QA_PACKETS']);output.write_text('');output.chmod(0o600)
def packet(connection,sender,path,interface,member,parameters,user_data):
    released,mask,sym,unicode,keycode=parameters.unpack()
    with output.open('a') as stream:stream.write(json.dumps(dict(time=time.monotonic(),released=released,mask=mask,keysym=sym,unicode=unicode,keycode=keycode))+'\n')
bus.signal_subscribe('org.freedesktop.a11y.Manager','org.freedesktop.a11y.KeyboardMonitor','KeyEvent','/org/freedesktop/a11y/Manager',None,Gio.DBusSignalFlags.NONE,packet,None)
bus.call_sync('org.freedesktop.a11y.Manager','/org/freedesktop/a11y/Manager','org.freedesktop.a11y.KeyboardMonitor','WatchKeyboard',GLib.Variant('()',()),None,Gio.DBusCallFlags.NONE,3000,None)
(runtime/'observer-ready').touch()
GLib.MainLoop().run()
