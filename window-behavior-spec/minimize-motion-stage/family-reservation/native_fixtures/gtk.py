#!/usr/bin/env python3
import gi
gi.require_version('Gtk','4.0')
from gi.repository import Gtk,Gio
app=Gtk.Application(application_id='org.omarchy.MotionParityQAGtk',flags=Gio.ApplicationFlags.NON_UNIQUE)
def activate(app):
 window=Gtk.ApplicationWindow(application=app,title='Motion parity QA GTK')
 window.set_decorated(False);window.set_default_size(620,380)
 area=Gtk.DrawingArea()
 def paint(area,context,width,height):
  context.set_source_rgb(.1,.65,.3);context.paint()
  context.set_source_rgb(1,1,1);context.set_font_size(24);context.move_to(40,100);context.show_text('GTK motion fixture')
 area.set_draw_func(paint);window.set_child(area);window.present()
app.connect('activate',activate);app.run(None)
