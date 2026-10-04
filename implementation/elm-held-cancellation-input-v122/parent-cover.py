"""One real GTK3 recipient. Run only inside the parent's protected private GUI."""
import json
import os
from pathlib import Path
import signal
import sys
import time

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk, GLib, Gtk

TITLE = 'ELM-PARENT-FOCUS-COVER'
RECIPIENT = 'parent-input-recipient'
control = Path(sys.argv[1])
events = Path(sys.argv[2]) if len(sys.argv) > 2 else control.with_suffix('.events.jsonl')
loop = GLib.MainLoop()
counts = {'enter': 0, 'motion': 0, 'button-press': 0, 'button-release': 0}
sequence = 0
quitting = False
window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
window.set_title(TITLE)
window.set_role('elm-parent-focus-cover')
window.fullscreen()
window.set_decorated(False)
window.set_default_size(240, 160)
window.set_resizable(True)
recipient = Gtk.EventBox()
recipient.set_name(RECIPIENT)
recipient.set_visible_window(True)
recipient.set_above_child(True)
recipient.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK |
                     Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK |
                     Gdk.EventMask.BUTTON_RELEASE_MASK)
label = Gtk.Label(label='Parent pointer recipient\nNative widget receipts only')
recipient.add(label)
window.add(recipient)


def geometry():
    allocation = recipient.get_allocation()
    top = window.get_allocation()
    gdk = recipient.get_window()
    return {'recipientAllocation': {'x': allocation.x, 'y': allocation.y,
                                   'width': allocation.width, 'height': allocation.height},
            'windowAllocation': {'width': top.width, 'height': top.height},
            'scaleFactor': recipient.get_scale_factor(), 'mapped': recipient.get_mapped(),
            'realized': recipient.get_realized(),
            'gdkWindowReference': str(hash(gdk)) if gdk is not None else None,
            'displayType': type(Gdk.Display.get_default()).__name__}


def log(kind, **values):
    global sequence
    sequence += 1
    record = {'schema': 1, 'sequence': sequence, 'monotonicNs': time.monotonic_ns(),
              'pid': os.getpid(), 'title': window.get_title(), 'fixtureWindowId': 'ordinary-1',
              'eventRecipient': RECIPIENT, 'kind': kind, 'counts': dict(counts),
              'geometry': geometry(), **values}
    payload = (json.dumps(record, ensure_ascii=True, allow_nan=False) + '\n').encode()
    fd = os.open(events, os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_CLOEXEC, 0o600)
    try:
        offset = 0
        while offset < len(payload):
            offset += os.write(fd, payload[offset:])
    finally:
        os.close(fd)


def delivered(widget, event, kind):
    counts[kind] += 1
    actual_widget = Gtk.get_event_widget(event)
    event_window = event.get_window()
    event_owner = event_window.get_user_data() if event_window is not None else None
    drawing_window = recipient.get_window()
    live_window = event_window is not None and not event_window.is_destroyed()
    owned_window = live_window and (event_window == drawing_window or
        (event_window.get_parent() == drawing_window and event_window in drawing_window.get_children()))
    log(kind, x=float(event.x), y=float(event.y),
        eventType=int(event.type), eventTypeNick=event.type.value_nick,
        eventTime=int(event.time), sendEvent=bool(event.send_event),
        button=int(event.button) if kind.startswith('button-') else None,
        signalRecipient=widget.get_name(),
        gdkEventWidget=actual_widget.get_name() if actual_widget else None,
        eventWidgetIsRecipient=actual_widget == recipient,
        signalWidgetIsRecipient=widget == recipient,
        eventWindowIsOwned=bool(owned_window),
        eventWindowOwnerReference=str(event_owner) if isinstance(event_owner, int) else None,
        recipientNativeReference=str(hash(recipient)),
        eventWindowOwnerIsRecipient=(event_owner == hash(recipient)),
        eventWindowReference=str(hash(event_window)) if event_window is not None else None)
    return False


for signal_name, kind in (('enter-notify-event', 'enter'), ('motion-notify-event', 'motion'),
                          ('button-press-event', 'button-press'), ('button-release-event', 'button-release')):
    recipient.connect(signal_name, lambda widget, event, kind=kind: delivered(widget, event, kind))
recipient.connect('size-allocate', lambda widget, allocation: log('allocation'))
recipient.connect('map-event', lambda widget, event: log('mapped') or False)
window.connect('configure-event', lambda widget, event: log('configure',
               configuredWidth=int(event.width), configuredHeight=int(event.height)) or False)


def quit_(cause='signal'):
    global quitting
    if quitting:
        return False
    quitting = True
    log('normal-exit', cause=cause)
    window.destroy()
    loop.quit()
    return False


def poll():
    if not control.exists():
        return True
    try:
        stat = control.lstat()
        if not control.is_file() or control.is_symlink() or stat.st_uid != os.getuid():
            raise ValueError('Control must be an owned regular file')
        request = json.loads(control.read_text())
        control.unlink()
        if not isinstance(request, dict) or set(request) - {'op', 'requestId', 'width', 'height'}:
            raise ValueError('Invalid control fields')
        identity = request.get('requestId')
        if identity is not None and (not isinstance(identity, str) or len(identity) > 128):
            raise ValueError('Invalid requestId')
        op = request.get('op')
        if op == 'quit':
            log('control-ack', op=op, requestId=identity)
            return quit_('control')
        if op == 'inspect':
            log('inspection', requestId=identity)
        elif op == 'resize':
            width, height = request.get('width'), request.get('height')
            if any(type(value) is not int or not 1 <= value <= 4096 for value in (width, height)):
                raise ValueError('Invalid resize bounds')
            window.resize(width, height)
            log('resize-requested', requestId=identity, requestedWidth=width, requestedHeight=height)
        else:
            raise ValueError('Unknown operation')
    except Exception as error:
        log('control-error', error=str(error))
    return True


window.connect('delete-event', lambda widget, event: quit_('delete') or True)
window.show_all()
GLib.idle_add(lambda: log('ready') or False)
GLib.timeout_add(25, poll)
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, quit_)
loop.run()
