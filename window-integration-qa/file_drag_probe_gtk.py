#!/usr/bin/env python3
"""Disposable file-offer drag source/drop receiver. It never moves or deletes files."""
import gi,json,sys
from pathlib import Path
gi.require_version('Gtk','4.0')
from gi.repository import Gtk,Gdk,Gio,GLib,GObject
app_id,title,mode,path,log=sys.argv[1:]
uri=Path(path).resolve().as_uri()
def record(**event):
    with Path(log).open('a') as out:out.write(json.dumps(event)+'\n')
app=Gtk.Application(application_id=app_id,flags=Gio.ApplicationFlags.NON_UNIQUE)
def activate(app):
    window=Gtk.ApplicationWindow(application=app,title=title)
    window.set_default_size(400,260)
    area=Gtk.Label(label='Drag the disposable file' if mode=='source' else 'Drop the disposable file here')
    area.set_hexpand(True);area.set_vexpand(True);window.set_child(area)
    if mode=='source':
        source=Gtk.DragSource.new();source.set_actions(Gdk.DragAction.COPY)
        def prepare(*args):
            return Gdk.ContentProvider.new_union([
                Gdk.ContentProvider.new_for_bytes('text/uri-list',GLib.Bytes.new((uri+'\r\n').encode())),
                Gdk.ContentProvider.new_for_value(uri)])
        source.connect('prepare',prepare)
        source.connect('drag-begin',lambda *args:record(event='begin'))
        source.connect('drag-end',lambda controller,drag,delete:record(event='end',delete=delete))
        source.connect('drag-cancel',lambda *args:record(event='cancel'))
        area.add_controller(source)
    else:
        drop=Gtk.DropTarget.new(GObject.TYPE_STRING,Gdk.DragAction.COPY)
        def receive(controller,value,x,y):record(event='drop',value=value);return value==uri
        drop.connect('drop',receive);area.add_controller(drop)
    window.present()
app.connect('activate',activate);app.run(None)
