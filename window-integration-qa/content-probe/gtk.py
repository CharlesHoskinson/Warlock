#!/usr/bin/env python3
import gi,math,time
gi.require_version('Gtk','4.0')
from gi.repository import Gtk,Gio
app=Gtk.Application(application_id='org.omarchy.ContentQA',flags=Gio.ApplicationFlags.NON_UNIQUE)
def activate(app):
    window=Gtk.ApplicationWindow(application=app,title='Content repaint QA GTK')
    window.set_default_size(600,350)
    area=Gtk.DrawingArea()
    state={'phase':0}
    def paint(area,context,width,height):
        state['phase']+=1
        for i in range(16):
            hue=(i*22+state['phase']*3)%360
            context.set_source_rgb((math.sin(hue*.017)+1)/2,(math.sin((hue+120)*.017)+1)/2,(math.sin((hue+240)*.017)+1)/2)
            context.rectangle(i*width/16,0,width/16+1,height);context.fill()
        context.set_source_rgb(1,1,1);context.rectangle(20+(state['phase']*5)%max(1,width-50),40,25,100);context.fill()
    area.set_draw_func(paint)
    area.add_tick_callback(lambda *_:area.queue_draw() or True)
    window.set_child(area);window.present()
app.connect('activate',activate)
app.run(None)
