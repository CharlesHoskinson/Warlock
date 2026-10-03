"""Actual public Orca AX factory/libatspi device, controlled native held probe.

This is a library/control-plane proof; it is separate from the later real
Omarchy Orca compat reader and pointer navigation trial.
"""
import gi,json,os,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(HERE/'mouse-review-v2/orca-compat'))
from capability_adapter import install_private
gi.require_version('Atspi','2.0')
from gi.repository import Gio,GLib,Atspi
from orca import ax_device_manager
adapter=install_private()
manager=ax_device_manager.get_manager();manager.activate();device=manager.get_device()
connection=device.get_property('session-bus');name=device.get_app_id()+'.KeyboardMonitor'
def owner():
    return connection.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus',
        'GetNameOwner',GLib.Variant('(s)',(name,)),None,Gio.DBusCallFlags.NONE,500,None).unpack()[0]
print(json.dumps(dict(ready=True,backend=device.__gtype__.name,ownUnique=connection.get_unique_name(),owner=owner())),flush=True)
for line in sys.stdin:
    request=json.loads(line)
    if request['operation']=='exit':break
    if request['operation']=='pump-official-callback':
        context=GLib.MainContext.default();end=time.monotonic()+.7
        while time.monotonic()<end:
            while context.pending():context.iteration(False)
            time.sleep(.005)
        value=connection.call_sync('org.freedesktop.a11y.Manager','/org/freedesktop/a11y/Manager',
            'org.omarchy.KeyboardMonitorProbe','State',None,None,Gio.DBusCallFlags.NONE,500,None)
        print(json.dumps(dict(pass_=True,state=json.loads(value.unpack()[0]),
            gobjectObserverInstalled=False,sameActualDevice=manager.get_device() is device)),flush=True)
        continue
    before=owner()
    try:
        value=device.set_capabilities(device.get_capabilities() | Atspi.DeviceCapability.POINTER_MONITOR)
        result=dict(pass_=True,value=int(value))
    except Exception as error:result=dict(pass_=False,error=str(error))
    print(json.dumps(dict(before=before,after=owner(),sameActualDevice=manager.get_device() is device,**result)),flush=True)
connection.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus','org.freedesktop.DBus',
    'ReleaseName',GLib.Variant('(s)',(name,)),None,Gio.DBusCallFlags.NONE,500,None)
adapter.close()
