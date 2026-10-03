#!/usr/bin/env python3
import sys,gi
gi.require_version('Gtk','4.0')
from gi.repository import Gtk,Gio
role=sys.argv[1]
app=Gtk.Application(application_id='org.omarchy.WholeSnapshotQA'+role,flags=Gio.ApplicationFlags.NON_UNIQUE)
def activate(app):
 window=Gtk.ApplicationWindow(application=app,title='Whole snapshot '+role)
 window.set_decorated(False);window.set_default_size(380,240)
 area=Gtk.DrawingArea()
 def paint(area,context,width,height):
  context.set_source_rgb(*((.9,.05,.05) if role=='target' else (.05,.1,.95)))
  context.paint()
 area.set_draw_func(paint);window.set_child(area);window.present()
app.connect('activate',activate);app.run(None)
