"""Actual GTK4 accessible application; emits real layout, never AX metadata."""
import gi,json,os,sys,time
from pathlib import Path
gi.require_version('Gtk','4.0')
from gi.repository import Gtk,GLib,Gio,Gdk
from private_runtime_guard import checked_runtime
runtime=checked_runtime()
tag,path=sys.argv[1],Path(sys.argv[2])
GLib.set_application_name('Pointer peer '+tag)
app=Gtk.Application(application_id='org.omarchy.PointerPeer'+tag,flags=Gio.ApplicationFlags.NON_UNIQUE)
windows=[];buttons=[];popover=None;popup_button=None;pointer_event=None
def track(widget):
    controller=Gtk.EventControllerMotion()
    controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
    def moved(controller,x,y):
        global pointer_event
        picked=widget.pick(x,y,Gtk.PickFlags.DEFAULT)
        while picked is not None and not isinstance(picked,Gtk.Button):picked=picked.get_parent()
        pointer_event=dict(time=time.monotonic(),widget_x=x,widget_y=y,
            actualPickedButton=picked.get_label() if picked else None,native=widget.__gtype__.name)
        snapshot()
    controller.connect('motion',moved);widget.add_controller(controller)
def window(title):
    w=Gtk.ApplicationWindow(application=app,title=title);w.set_decorated(tag=='B');w.set_default_size(360,240)
    if tag=='B':w.set_titlebar(Gtk.HeaderBar())
    box=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=0)
    for edge in ('top','bottom','start','end'):getattr(box,'set_margin_'+edge)(24)
    b=Gtk.Button(label='Pointer target '+tag)
    b.update_property([Gtk.AccessibleProperty.LABEL],['Pointer target '+tag])
    neighbor=Gtk.Button(label='Distinct adjacent '+tag)
    neighbor.update_property([Gtk.AccessibleProperty.LABEL],['Distinct adjacent '+tag])
    if tag=='B':
        for button in (b,neighbor):button.add_css_class('pointer-compact');button.set_size_request(160,20)
    box.append(b);box.append(neighbor);entry=Gtk.Entry();entry.set_placeholder_text('Focus peer '+tag);box.append(entry)
    w.set_child(box);windows.append(w);buttons.append(b);track(w);w.present();return w
def activate(application):
    css=Gtk.CssProvider();css.load_from_string('button.pointer-compact {padding:0;min-height:18px;min-width:80px;}')
    Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(),css,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    window('Pointer peer '+tag)
app.connect('activate',activate)
def snapshot():
    rows=[]
    for w,b in zip(windows,buttons):
        ok,bounds=b.compute_bounds(w)
        rows.append(dict(title=w.get_title(),width=w.get_width(),height=w.get_height(),
            decorated=w.get_decorated(),surfaceTransform=list(w.get_surface_transform()),
            button=dict(x=bounds.get_x(),y=bounds.get_y(),width=bounds.get_width(),height=bounds.get_height()) if ok else None))
    popup=None
    if popover and popover.get_mapped():
        ok,bounds=popup_button.compute_bounds(popover);surface=popover.get_surface()
        center_picked=popover.pick(bounds.get_x()+bounds.get_width()/2,bounds.get_y()+bounds.get_height()/2,Gtk.PickFlags.DEFAULT) if ok else None
        while center_picked is not None and not isinstance(center_picked,Gtk.Button):center_picked=center_picked.get_parent()
        if ok and surface:popup=dict(observedAt=time.monotonic(),nativeMapped=surface.get_mapped(),
            popoverAllocation=[popover.get_width(),popover.get_height()],buttonAllocation=[popup_button.get_width(),popup_button.get_height()],
            centerPickedButton=center_picked.get_label() if center_picked else None,
            position=[surface.get_position_x(),surface.get_position_y()],
            surfaceTransform=list(popover.get_surface_transform()),
            button=dict(x=bounds.get_x(),y=bounds.get_y(),width=bounds.get_width(),height=bounds.get_height()))
    path.write_text(json.dumps(dict(pid=os.getpid(),tag=tag,windows=rows,popup=popup,pointerEvent=pointer_event)));path.chmod(0o600);return True
def command(source,condition):
    global popover,popup_button
    line=sys.stdin.readline()
    if not line:app.quit();return False
    op=json.loads(line).get('operation')
    if op=='second':window('Pointer peer '+tag+' second')
    elif op=='close-second' and len(windows)>1:windows.pop().destroy();buttons.pop()
    elif op=='popover':
        popover=Gtk.Popover();popup_button=Gtk.Button(label='Actual popup target '+tag)
        popover.set_child(popup_button);popover.set_parent(buttons[0]);popover.set_position(Gtk.PositionType.TOP);track(popover);popover.popup()
    elif op=='close-popover' and popover:popover.popdown();popover.unparent();popover=None
    elif op=='exit':
        print(json.dumps(dict(pass_=True,operation=op)),flush=True)
        app.quit();return False
    snapshot();print(json.dumps(dict(pass_=True,operation=op)),flush=True);return True
GLib.io_add_watch(sys.stdin.fileno(),GLib.IO_IN,command)
GLib.timeout_add(100,snapshot)
app.run([sys.argv[0]])
