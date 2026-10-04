from gi.repository import Gio,GLib
import os,signal
loop=GLib.MainLoop();ignore=os.environ.get('CPU_IGNORE_TERM')=='1'
signal.signal(signal.SIGTERM,signal.SIG_IGN if ignore else lambda *_:loop.quit())
bus=Gio.DBusConnection.new_for_address_sync(os.environ['DBUS_SESSION_BUS_ADDRESS'],Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
bus.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','RequestName',GLib.Variant('(su)',('org.elm.LateActivation',0)),None,Gio.DBusCallFlags.NONE,1000,None)
if not ignore:GLib.timeout_add(150,lambda:(loop.quit(),False)[1])
loop.run();bus.close_sync(None)
