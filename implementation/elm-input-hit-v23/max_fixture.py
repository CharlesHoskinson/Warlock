"""Owned colored GTK windows, including a modal and unrelated same-process peer."""
import gi
import cairo
import json
import signal
import sys
from pathlib import Path

gi.require_version('Gtk', '4.0')
gi.require_foreign('cairo')
from gi.repository import Gdk, GLib, Gtk

control = Path(sys.argv[1])
loop = GLib.MainLoop()
windows = {}
groups = {}
popovers = {}
events = control.with_suffix('.events.jsonl')

def log(name, kind, **values):
    with events.open('a') as stream:
        stream.write(json.dumps({'window':name,'kind':kind,**values})+'\n')
provider = Gtk.CssProvider()
provider.load_from_string('window.red {background:#ff0000;} window.green {background:#00ff00;} window.blue {background:#0000ff;}')
Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

def create(name, color, parent=None):
    window = Gtk.Window(title=name)
    # Independent document roots need independent GTK grab groups. Otherwise
    # Gtk's default application-wide modal grab can redirect client-side keys
    # after the compositor has correctly focused an unrelated same-process peer.
    if parent:
        parent.get_group().add_window(window)
    else:
        group = Gtk.WindowGroup()
        group.add_window(window)
        groups[name] = group
    window.set_default_size(320, 240)
    window.add_css_class(color)
    content = Gtk.Fixed()
    entry = Gtk.Entry()
    entry.set_size_request(100,24)
    content.put(entry,8,8)
    if name=='SCENE-PEER':
        menu=Gtk.MenuButton(label='Menu')
        menu.set_size_request(64,24)
        popup=Gtk.Popover()
        popup.set_child(Gtk.Label(label='Owned popup'))
        menu.set_popover(popup)
        content.put(menu,8,90)
        popovers[name]=popup
    window.set_child(content)
    gesture = Gtk.GestureClick()
    gesture.set_button(0)
    gesture.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
    gesture.connect('pressed',lambda controller,n,x,y:log(name,'pressed',button=controller.get_current_button(),x=x,y=y))
    gesture.connect('released',lambda controller,n,x,y:log(name,'released',button=controller.get_current_button(),x=x,y=y))
    window.add_controller(gesture)
    keyboard = Gtk.EventControllerKey()
    keyboard.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
    def key_(controller,keyval,keycode,state):
        log(name,'key',keyval=keyval,keycode=keycode)
        return False
    keyboard.connect('key-pressed',key_)
    window.add_controller(keyboard)
    if parent:
        window.set_transient_for(parent)
        window.set_modal(True)
    windows[name] = window
    window.present()
    entry.grab_focus()
    return window

def quit_():
    for window in reversed(list(windows.values())):
        window.destroy()
    windows.clear()
    loop.quit()
    return False

def peer_input_region(request):
    """Change native pointer eligibility while leaving opaque paint untouched."""
    window = windows['SCENE-PEER']
    surface = window.get_surface()
    if surface is None:
        raise RuntimeError('Peer has no native surface')
    width, height = surface.get_width(), surface.get_height()
    if width <= 0 or height <= 0:
        raise RuntimeError('Peer native surface has invalid dimensions')
    if request['op'] == 'input-full-peer':
        # None restores GDK's whole-surface input region.
        surface.set_input_region(None)
        log('SCENE-PEER', 'input-region', op=request['op'], width=width,
            height=height, hole=None, rectangles=[[0, 0, width, height]])
        return
    hole_width, hole_height = max(1, width // 4), max(1, height // 4)
    hole = request.get('hole', [(width-hole_width)//2, (height-hole_height)//2,
                                hole_width, hole_height])
    if (not isinstance(hole, list) or len(hole) != 4
            or any(type(v) is not int for v in hole)):
        raise ValueError('Input hole must be four integer surface coordinates')
    x, y, w, h = hole
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x+w > width or y+h > height:
        raise ValueError('Input hole must fit inside the native surface')
    region = cairo.Region(cairo.RectangleInt(0, 0, width, height))
    region.subtract(cairo.RectangleInt(x, y, w, h))
    surface.set_input_region(region)
    rectangles = []
    for index in range(region.num_rectangles()):
        rect = region.get_rectangle(index)
        rectangles.append([rect.x, rect.y, rect.width, rect.height])
    # This is an application-side request receipt. Native QA must independently
    # observe the committed input region and actual recipient after a click.
    log('SCENE-PEER', 'input-region', op=request['op'], width=width,
        height=height, hole=hole, rectangles=rectangles)

def poll():
    if control.exists():
        request = json.loads(control.read_text())
        control.unlink()
        if request['op'] == 'family':
            windows.pop('SCENE-MAX').destroy()
            owner = create('SCENE-OWNER', 'red')
            create('SCENE-MODAL', 'blue', owner)
        elif request['op'] == 'hide-peer':
            windows['SCENE-PEER'].hide()
        elif request['op'] == 'show-peer':
            windows['SCENE-PEER'].present()
        elif request['op'] == 'quit':
            return quit_()
        elif request['op'] == 'late-child':
            create('SCENE-LATE','blue',windows['SCENE-OWNER'])
        elif request['op'] == 'close-popup':
            popovers['SCENE-PEER'].popdown()
        elif request['op'] == 'retire-late':
            windows.pop('SCENE-LATE').destroy()
        elif request['op'] == 'retire-modal':
            windows.pop('SCENE-MODAL').destroy()
        elif request['op'] in ('input-hole-peer', 'input-full-peer'):
            peer_input_region(request)
    return True

create('SCENE-MAX', 'red')
create('SCENE-PEER', 'green')
GLib.timeout_add(40, poll)
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, quit_)
loop.run()
