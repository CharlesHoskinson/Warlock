"""Shared AT-SPI reader; tests enable and restore assistive status explicitly."""
from contextlib import contextmanager
import time
import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi, Gio, GLib

@contextmanager
def assistive_session():
    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    def call(method, args):
        return bus.call_sync('org.a11y.Bus', '/org/a11y/bus',
            'org.freedesktop.DBus.Properties', method, args, None,
            Gio.DBusCallFlags.NONE, 5000, None)
    previous = call('GetAll', GLib.Variant('(s)', ('org.a11y.Status',))).unpack()[0]
    def set_status(key, value):
        call('Set', GLib.Variant('(ssv)', ('org.a11y.Status', key, GLib.Variant('b', value))))
    try:
        for key in ('IsEnabled', 'ScreenReaderEnabled'):
            set_status(key, True)
        yield
    finally:
        for key in ('IsEnabled', 'ScreenReaderEnabled'):
            set_status(key, previous[key])

def nodes():
    result = []
    def walk(node, depth):
        if depth > 16:
            return
        try:
            node.clear_cache()
            if node.get_state_set().contains(Atspi.StateType.SHOWING):
                result.append(node)
            for i in range(node.get_child_count()):
                walk(node.get_child_at_index(i), depth + 1)
        except Exception:
            pass
    desktop = Atspi.get_desktop(0)
    for i in range(desktop.get_child_count()):
        app = desktop.get_child_at_index(i)
        if app.get_name() in ('qs', 'quickshell'):
            walk(app, 0)
    return result

def find(name=None, accessible_id=None, role=None):
    for node in nodes():
        if name is not None and node.get_name() != name:
            continue
        if accessible_id is not None and node.get_accessible_id() != accessible_id:
            continue
        if role is not None and node.get_role_name() != role:
            continue
        return node

def invoke(node, action='press', allow_defunct=False):
    try:
        iface = node.get_action_iface()
        assert iface is not None
        names = [iface.get_action_name(i) for i in range(iface.get_n_actions())]
        index = next(i for i, name in enumerate(names) if name.lower() == action.lower())
        accepted = iface.do_action(index)
        if not allow_defunct:
            assert accepted, names
    except Exception:
        if not allow_defunct:
            raise
    time.sleep(.45)
