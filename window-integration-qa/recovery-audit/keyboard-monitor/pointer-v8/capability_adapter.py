"""Explicit process-only public API adapter for fresh pointer capability probes.

Passive until install(). The injected verifier must prove exact compositor
quiescence AND zero caller interception policies before releasing a name.
Production must inject exact-instance Lua verification; private native proof
may use the isolated bridge's read-only probe. No maintenance method is called.
"""
from __future__ import annotations

class CapabilityAdapter:
    def __init__(self, atspi, ax, transport, verify_pre_replay, report=None):
        self.atspi,self.ax,self.transport=atspi,ax,transport
        self.verify_pre_replay=verify_pre_replay
        self.report=report or (lambda event,**fields:None)
        self.fresh={}
        self.original_activate=ax.activate
        self.original_capabilities=atspi.Device.set_capabilities
        self.installed=False

    def install(self):
        if self.installed: raise RuntimeError('capability adapter already installed')
        self.ax.activate=self.activate
        def public_capabilities(device,caps):
            return self.set_capabilities(device,caps)
        self.atspi.Device.set_capabilities=public_capabilities
        self.installed=True
        return self

    def activate(self,*args,**kwargs):
        prior=self.ax.get_device()
        if prior is None:self.fresh.clear()
        result=self.original_activate(*args,**kwargs)
        current=self.ax.get_device()
        if prior is None and current is not None and current.__gtype__.name=='AtspiDeviceA11yManager':
            self.fresh[id(current)]=(current,self.transport.manager_owner())
        return result

    def set_capabilities(self,device,caps):
        pointer=self.atspi.DeviceCapability.POINTER_MONITOR
        if (not caps & pointer or device.__gtype__.name!='AtspiDeviceA11yManager'
                or device.get_capabilities() & pointer):
            return self.original_capabilities(device,caps)
        marker=self.fresh.get(id(device))
        if not marker or marker[0] is not device or self.ax.get_device() is not device:
            raise RuntimeError('pointer probe requires the current fresh pre-replay device')
        owner=marker[1]
        if not owner or self.transport.manager_owner()!=owner:
            self.fresh.pop(id(device),None)
            raise RuntimeError('manager epoch changed before pointer probe')
        connection=device.get_property('session-bus')
        app_id=device.get_app_id()
        name=(app_id+'.KeyboardMonitor') if app_id else 'org.a11y.atspi.KeyboardMonitor'
        unique=connection.get_unique_name()
        if not unique or self.transport.name_owner(connection,name)!=unique:
            raise RuntimeError('actual device connection does not own its registration')
        if not self.verify_pre_replay(connection,owner):
            raise RuntimeError('held, dirty, unknown or already replayed pointer probe refused')
        if self.transport.manager_owner()!=owner:
            self.fresh.pop(id(device),None)
            raise RuntimeError('manager epoch changed at pointer probe gate')
        # Consume the fresh marker before entering potentially reentrant GI.
        self.fresh.pop(id(device),None)
        if self.transport.release(connection,name)!=1:
            raise RuntimeError('own registration release failed')
        result=None
        failure=None
        try:
            result=self.original_capabilities(device,caps)
        except BaseException as error:
            failure=error
        finally:
            # Reclaim only the verified own registration. Never replace/queue.
            reclaimed=self.transport.request(connection,name,4)
            if reclaimed not in (1,4) or self.transport.name_owner(connection,name)!=unique:
                raise RuntimeError('pointer probe could not reclaim its own registration') from failure
        if self.transport.manager_owner()!=owner:
            raise RuntimeError('manager epoch changed during pointer probe; no policy replay') from failure
        if failure is not None:
            raise failure
        self.transport.watch(connection)
        if not result & pointer:
            self.report("pointer-capability-unsupported",owner=owner,name=name,unique=unique,capable=False)
            raise RuntimeError("actual device did not enable POINTER_MONITOR; pointer recovery refused")
        # The unregistered availability test did not arm a pointer query.
        # Bootstrap via a truthful public call; subsequent motion signals use
        # the unchanged official libatspi query/emit/rearm callback.
        self.transport.arm(connection)
        if self.transport.manager_owner()!=owner:
            raise RuntimeError('manager epoch changed after pointer bootstrap; no policy replay')
        self.report('pointer-capability-probed',owner=owner,name=name,
                    unique=unique,capable=bool(result & pointer))
        return result

    def close(self):
        if self.installed:
            self.ax.activate=self.original_activate
            self.atspi.Device.set_capabilities=self.original_capabilities
            self.installed=False
        self.fresh.clear()

class PublicTransport:
    def __init__(self,session,glib,gio):
        self.session,self.glib,self.gio=session,glib,gio
    def _daemon(self,connection,method,signature,args):
        return connection.call_sync('org.freedesktop.DBus','/org/freedesktop/DBus',
            'org.freedesktop.DBus',method,self.glib.Variant(signature,args),None,
            self.gio.DBusCallFlags.NONE,500,None).unpack()[0]
    def manager_owner(self):
        try:return self.name_owner(self.session,'org.freedesktop.a11y.Manager')
        except self.glib.Error:return ''
    def name_owner(self,connection,name):return self._daemon(connection,'GetNameOwner','(s)',(name,))
    def release(self,connection,name):return self._daemon(connection,'ReleaseName','(s)',(name,))
    def request(self,connection,name,flags):return self._daemon(connection,'RequestName','(su)',(name,flags))
    def watch(self,connection):
        connection.call_sync('org.freedesktop.a11y.Manager','/org/freedesktop/a11y/Manager',
            'org.freedesktop.a11y.KeyboardMonitor','WatchKeyboard',None,None,
            self.gio.DBusCallFlags.NONE,500,None)
    def arm(self,connection):
        try:
            connection.call_sync('org.freedesktop.a11y.Manager','/org/freedesktop/a11y/Manager',
                'org.freedesktop.a11y.PointerLocator','QueryPointer',None,None,
                self.gio.DBusCallFlags.NONE,2000,None)
        except self.glib.Error as error:
            if self.gio.DBusError.get_remote_error(error)!='org.freedesktop.a11y.UnknownToplevel':
                raise

def install_private(report=None):
    """Explicit isolated-test bootstrap. Does not import MouseReviewer."""
    import os,json
    from pathlib import Path
    runtime=Path(os.environ['XDG_RUNTIME_DIR'])
    if (not str(runtime).startswith('/tmp/kbn-') or runtime.stat().st_mode & 0o777 != 0o700
            or os.environ.get('DBUS_SESSION_BUS_ADDRESS')!='unix:path='+str(runtime/'bus')
            or os.environ.get('DISPLAY')):
        raise RuntimeError('private pointer adapter requires isolated runtime/bus and native Wayland')
    import gi
    gi.require_version('Atspi','2.0')
    from gi.repository import Atspi,Gio,GLib
    from orca import ax_device_manager
    session=Gio.bus_get_sync(Gio.BusType.SESSION,None)
    transport=PublicTransport(session,GLib,Gio)
    def quiet(connection,owner):
        # This interface is private proof instrumentation, absent in production.
        value=connection.call_sync('org.freedesktop.a11y.Manager','/org/freedesktop/a11y/Manager',
            'org.omarchy.KeyboardMonitorProbe','State',None,None,Gio.DBusCallFlags.NONE,500,None)
        state=json.loads(value.unpack()[0])
        return (state.get('quiescent') is True and state.get('unloadQuiescent') is True
                and state.get('retiring') is False and state.get('callerPreReplay') is True
                and transport.manager_owner()==owner)
    return CapabilityAdapter(Atspi,ax_device_manager.get_manager(),transport,quiet,report).install()
