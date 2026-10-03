"""Owned colored GTK windows, including a modal and unrelated same-process peer."""
import gi
import json
import signal
import sys
from pathlib import Path

gi.require_version('Gtk', '4.0')
from gi.repository import Gdk, GLib, Gtk

control = Path(sys.argv[1])
loop = GLib.MainLoop()
windows = {}
provider = Gtk.CssProvider()
provider.load_from_string('window.red {background:#ff0000;} window.green {background:#00ff00;} window.blue {background:#0000ff;}')
Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

def create(name, color, parent=None):
    window = Gtk.Window(title=name)
    window.set_default_size(320, 240)
    window.add_css_class(color)
    if parent:
        window.set_transient_for(parent)
        window.set_modal(True)
    windows[name] = window
    window.present()
    return window

def quit_():
    for window in reversed(list(windows.values())):
        window.destroy()
    windows.clear()
    loop.quit()
    return False

def poll():
    if control.exists():
        request = json.loads(control.read_text())
        control.unlink()
        if request['op'] == 'family':
            windows.pop('SCENE-MAX').destroy()
            owner = create('SCENE-OWNER', 'red')
            create('SCENE-MODAL', 'blue', owner)
        elif request['op'] == 'quit':
            return quit_()
    return True

create('SCENE-MAX', 'red')
create('SCENE-PEER', 'green')
GLib.timeout_add(40, poll)
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, quit_)
loop.run()
