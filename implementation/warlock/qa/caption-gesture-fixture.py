"""Owned colored GTK windows, including a modal and unrelated same-process peer."""
import gi
import cairo
gi.require_foreign("cairo")
import json
import signal
import sys
from pathlib import Path

gi.require_version('Gtk', '4.0')
from gi.repository import Gdk, GLib, Gtk

control = Path(sys.argv[1])
loop = GLib.MainLoop()
windows = {}
entries = {}
captured = {}
gesture_mode = "deferred"
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
    window.set_decorated(False)
    window.set_default_size(320, 240)
    window.add_css_class(color)
    content = Gtk.Fixed()
    entry = Gtk.Entry()
    entries[name] = entry
    entry.set_text("Warlock caption draft Ω")
    entry.set_size_request(100,24)
    content.put(entry,8,8)
    if name=='ELM-ACTIVATION-PEER':
        menu=Gtk.MenuButton(label='Menu')
        menu.set_size_request(64,24)
        popup=Gtk.Popover()
        popup.set_child(Gtk.Label(label='Owned popup'))
        menu.set_popover(popup)
        content.put(menu,8,90)
        popovers[name]=popup
    if name=='ELM-AUTHORITY-FIXTURE':
        caption=Gtk.Label(label='Caption drag')
        caption.set_size_request(180,32)
        content.put(caption,120,8)
        edge=Gtk.Label(label='Resize')
        edge.set_size_request(40,32)
        content.put(edge,280,200)
    window.set_child(content)
    gesture = Gtk.GestureClick()
    gesture.set_button(0)
    gesture.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
    def pressed(controller,n,x,y):
        captured[name]={'device':controller.get_current_event_device(),'button':controller.get_current_button(),'x':x,'y':y,'time':controller.get_current_event_time()}
        log(name,'pressed',button=controller.get_current_button(),x=x,y=y,time=controller.get_current_event_time())
        if name=='ELM-AUTHORITY-FIXTURE' and gesture_mode in ['move','resize']:
            begin(name,gesture_mode)
    gesture.connect('pressed',pressed)
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

def begin(name,mode,source=None):
    press=captured[source or name]
    surface=windows[name].get_surface()
    if mode=='move':
        surface.begin_move(press['device'],press['button'],press['x'],press['y'],press['time'])
    else:
        surface.begin_resize(Gdk.SurfaceEdge.SOUTH_EAST,press['device'],press['button'],press['x'],press['y'],press['time'])
    Gdk.Display.get_default().sync()
    log(name,'native-request',mode=mode,source=source or name,time=press['time'])

def quit_():
    for window in reversed(list(windows.values())):
        window.destroy()
    windows.clear()
    loop.quit()
    return False

def poll():
    global gesture_mode
    if control.exists():
        request = json.loads(control.read_text())
        control.unlink()
        if request['op'].startswith('gesture-mode-'):
            gesture_mode=request['op'].removeprefix('gesture-mode-')
            assert gesture_mode in ['move','resize','deferred']
            log('ELM-AUTHORITY-FIXTURE','gesture-mode',mode=gesture_mode)
        elif request['op'] in ['gesture-request-move','gesture-request-resize']:
            begin('ELM-AUTHORITY-FIXTURE',request['op'].removeprefix('gesture-request-'))
        elif request['op']=='gesture-request-other-surface':
            begin('ELM-AUTHORITY-FIXTURE','move','ELM-ACTIVATION-PEER')
        elif request['op']=='query-caption-draft':
            log('ELM-AUTHORITY-FIXTURE','draft',text=entries['ELM-AUTHORITY-FIXTURE'].get_text())
        elif request['op'] == 'family':
            windows.pop('ELM-AUTHORITY-FIXTURE').destroy()
            owner = create('SCENE-OWNER', 'red')
            create('SCENE-MODAL', 'blue', owner)
        elif request['op'] == 'input-hole':
            surface=windows['ELM-ACTIVATION-PEER'].get_surface()
            assert surface.get_display().supports_input_shapes()
            region=cairo.Region()
            for rectangle in [(0,0,320,60),(0,60,70,60),(130,60,190,60),(0,120,320,120)]:
                region.union(cairo.RectangleInt(*rectangle))
            surface.set_input_region(region)
            windows['ELM-ACTIVATION-PEER'].queue_draw()
            log('ELM-ACTIVATION-PEER','mask',rectangles=[(0,0,320,60),(0,60,70,60),(130,60,190,60),(0,120,320,120)])
        elif request['op'] == 'input-full':
            windows['ELM-ACTIVATION-PEER'].get_surface().set_input_region(None)
            windows['ELM-ACTIVATION-PEER'].queue_draw()
            log('ELM-ACTIVATION-PEER','mask',full=True)
        elif request['op'] == 'many-documents':
            for i in range(8):create('LONG-DOC-'+str(i)+' '+('W'*220),'green')
        elif request['op'] == 'add-modal':
            create('SCENE-MODAL','blue',windows['ELM-AUTHORITY-FIXTURE'])
        elif request['op'] == 'retire-peer':
            windows.pop('ELM-ACTIVATION-PEER').destroy()
        elif request['op'] == 'hide-peer':
            windows['ELM-ACTIVATION-PEER'].hide()
        elif request['op'] == 'show-peer':
            windows['ELM-ACTIVATION-PEER'].present()
        elif request['op'] == 'quit':
            return quit_()
        elif request['op'] == 'late-child':
            create('SCENE-LATE','blue',windows['SCENE-OWNER'])
        elif request['op'] == 'close-popup':
            popovers['ELM-ACTIVATION-PEER'].popdown()
        elif request['op'] == 'retire-late':
            windows.pop('SCENE-LATE').destroy()
        elif request['op'] == 'renew-modal':
            create('SCENE-MODAL','blue',windows['SCENE-OWNER'])
        elif request['op'] == 'retire-modal':
            windows.pop('SCENE-MODAL').destroy()
    return True

create('ELM-AUTHORITY-FIXTURE', 'red')
create('ELM-ACTIVATION-PEER', 'green')
GLib.timeout_add(40, poll)
GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, quit_)
loop.run()
