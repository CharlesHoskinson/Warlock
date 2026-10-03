#!/usr/bin/env python3
"""Native GTK file copy drag. Receiver checks actual bytes; no move/delete action."""
import hashlib,json,sys,time
from pathlib import Path
import gi
gi.require_version('Gtk','4.0')
from gi.repository import Gtk,Gdk,Gio,GLib

def main():
    app_id,title,mode,path,log,destination=sys.argv[1:]
    payload=Path(path).resolve();uri=payload.as_uri()
    dest=Path(destination).resolve()
    def record(**event):
        with Path(log).open('a') as output:
            output.write(json.dumps(dict(event,time=time.monotonic()))+'\n')
    app=Gtk.Application(application_id=app_id,flags=Gio.ApplicationFlags.NON_UNIQUE)
    def activate(app):
        window=Gtk.ApplicationWindow(application=app,title=title)
        window.set_default_size(400,260)
        area=Gtk.Label(label='Drag the disposable file' if mode=='source' else 'Drop: copy and verify disposable file')
        area.set_hexpand(True);area.set_vexpand(True);window.set_child(area)
        if mode=='source':
            source=Gtk.DragSource.new();source.set_actions(Gdk.DragAction.COPY)
            def prepare(*_args):
                files=Gdk.FileList.new_from_list([Gio.File.new_for_path(str(payload))])
                return Gdk.ContentProvider.new_union([
                    Gdk.ContentProvider.new_for_value(files),
                    Gdk.ContentProvider.new_for_bytes('text/uri-list',GLib.Bytes.new((uri+'\r\n').encode()))])
            source.connect('prepare',prepare)
            source.connect('drag-begin',lambda *_args:record(event='begin'))
            source.connect('drag-end',lambda controller,drag,delete:record(event='end',delete=bool(delete)))
            source.connect('drag-cancel',lambda controller,drag,reason:record(event='cancel',reason=str(reason)))
            area.add_controller(source)
        elif mode=='target':
            drop=Gtk.DropTarget.new(Gdk.FileList.__gtype__,Gdk.DragAction.COPY)
            drop.connect('enter',lambda controller,x,y:record(event='enter',x=x,y=y) or Gdk.DragAction.COPY)
            drop.connect('leave',lambda *_args:record(event='leave'))
            def receive(controller,value,x,y):
                try:
                    files=value.get_files();uris=[file.get_uri() for file in files]
                    if uris != [uri]:
                        record(event='rejected',uris=uris);return False
                    contents=Path(files[0].get_path()).read_bytes()
                    dest.mkdir(parents=True,exist_ok=True)
                    copy=dest/('received-'+str(time.monotonic_ns())+'.bin')
                    with copy.open('xb') as output:output.write(contents)
                    copied=copy.read_bytes()
                    record(event='drop',nativeType='Gdk.FileList',uris=uris,bytes=len(copied),sha256=hashlib.sha256(copied).hexdigest(),copy=str(copy),x=x,y=y)
                    return True
                except Exception as error:
                    record(event='error',error=repr(error));return False
            drop.connect('drop',receive);area.add_controller(drop)
        else:raise ValueError(mode)
        window.present()
    app.connect('activate',activate);app.run(None)

if __name__=='__main__':main()
