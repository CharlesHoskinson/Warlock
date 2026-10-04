from gi.repository import Gio,GLib
import os,signal
loop=GLib.MainLoop()
signal.signal(signal.SIGTERM,signal.SIG_IGN if os.environ.get('CPU_IGNORE_TERM')=='1' else lambda *_:loop.quit())
bus=Gio.DBusConnection.new_for_address_sync(os.environ['DBUS_SESSION_BUS_ADDRESS'],Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT|Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,None,None)
bus.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus','RequestName',GLib.Variant('(su)',('org.elm.CPUActivation',0)),None,Gio.DBusCallFlags.NONE,1000,None)
loop.run()
bus.close_sync(None)
