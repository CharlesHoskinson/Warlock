"""Read-only actual AT-SPI tree/events and actual Orca observation getter.

The org.a11y.Bus/Status fixture only advertises the owned AT bus and reader
presence. The real registry, GTK/WebKit accessibility bridge and reader run
unchanged; no synthetic Accessible nodes or focus events are supplied.
"""
import json
import os
import signal
from pathlib import Path
import sys
import time
import gi
gi.require_version('Atspi', '2.0')
from gi.repository import Atspi, Gio, GLib

runtime = Path(os.environ['XDG_RUNTIME_DIR']).resolve()
assert os.environ['DBUS_SESSION_BUS_ADDRESS'] == 'unix:path=' + str(runtime / 'bus')
address = 'unix:path=' + str(runtime / 'a11y-bus')
assert os.environ['AT_SPI_BUS_ADDRESS'] == address
assert not Path(os.environ['DBUS_SYSTEM_BUS_ADDRESS'].removeprefix('unix:path=')).exists()
request, reply, ready, event_path = map(Path, sys.argv[1:])
session = Gio.bus_get_sync(Gio.BusType.SESSION, None)
interface = Gio.DBusNodeInfo.new_for_xml('''<node>
<interface name="org.a11y.Bus"><method name="GetAddress"><arg direction="out" type="s"/></method></interface>
<interface name="org.a11y.Status"><property name="IsEnabled" type="b" access="read"/>
<property name="ScreenReaderEnabled" type="b" access="read"/></interface></node>''')


def method(connection, sender, path, interface, name, parameters, invocation):
    invocation.return_value(GLib.Variant('(s)', (address,)))


def prop(*args):
    return GLib.Variant('b', True)


for item in interface.interfaces:
    session.register_object('/org/a11y/bus', item, method, prop, None)
owner = Gio.bus_own_name_on_connection(session, 'org.a11y.Bus', Gio.BusNameOwnerFlags.DO_NOT_QUEUE, None, None)
Atspi.set_timeout(500, 500)
Atspi.init()
events = []


def describe(obj):
    if obj is None:
        return None
    try:
        return dict(name=obj.get_name() or '', role=obj.get_role_name(), identity=obj.get_accessible_id() or '',
                    states=[state.value_nick for state in obj.get_state_set().get_states()],
                    attributes=obj.get_attributes(), app=(obj.get_application().get_name() if obj.get_application() else ''),
                    pid=(obj.get_application().get_process_id() if obj.get_application() else 0))
    except Exception as error:
        return dict(error=repr(error))


def event(value):
    row = dict(type=value.type, detail1=value.detail1, detail2=value.detail2,
               source=describe(value.source), time=time.monotonic())
    events.append(row)
    with event_path.open('a') as stream:
        stream.write(json.dumps(row) + '\n')


listener = Atspi.EventListener.new(event)
for kind in ['object:state-changed:focused', 'object:state-changed:selected', 'object:state-changed:pressed',
             'object:property-change:accessible-name', 'object:selection-changed']:
    listener.register(kind)
seen = None


def snapshot():
    nodes, errors = [], []

    def walk(obj, ancestors, depth):
        if depth > 32 or len(nodes) >= 2048:
            raise RuntimeError('Native tree exceeds bounded fixture inspection')
        row = describe(obj)
        if not row or 'error' in row:
            errors.append(row)
            return
        row['ancestors'] = ancestors
        nodes.append(row)
        try:
            for i in range(obj.get_child_count()):
                walk(obj.get_child_at_index(i), ancestors + [dict(name=row['name'], role=row['role'])], depth + 1)
        except Exception as error:
            errors.append(repr(error))

    desktop = Atspi.get_desktop(0)
    if desktop:
        walk(desktop, [], 0)
    return nodes, errors


def tick():
    global seen
    if not request.exists():
        return True
    packet = json.loads(request.read_text())
    if packet['sequence'] == seen:
        return True
    seen = packet['sequence']
    nodes, errors = snapshot()
    reader = None
    reader_error = None
    try:
        value = session.call_sync('org.gnome.Orca.Service', '/org/gnome/Orca/Service/QAObservation',
                                  'org.gnome.Orca.Module', 'ExecuteRuntimeGetter',
                                  GLib.Variant('(s)', ('State',)), None,
                                  Gio.DBusCallFlags.NO_AUTO_START, 500, None)
        reader = json.loads(value.unpack()[0])
    except Exception as error:
        reader_error = repr(error)
    temp = reply.with_suffix('.tmp')
    temp.write_text(json.dumps(dict(sequence=seen, nodes=nodes, errors=errors, events=events,
                                   reader=reader, readerError=reader_error, time=time.monotonic())))
    temp.replace(reply)
    return True


ready.write_text(json.dumps(dict(pid=os.getpid(), session=os.environ['DBUS_SESSION_BUS_ADDRESS'],
                                accessibility=address, syntheticAccessibleNodes=False)))
GLib.timeout_add(25, tick)
loop=GLib.MainLoop()
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, lambda: (loop.quit(), False)[1])
loop.run()
