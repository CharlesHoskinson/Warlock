#!/usr/bin/env python3
"""Disposable GTK surface recording only synthetic QA input."""
import json
from pathlib import Path
import sys
import gi
gi.require_version('Gtk','4.0')
from gi.repository import Gtk,Gio
title,log=sys.argv[1:]
def record(event):
    with Path(log).open('a') as output:output.write(json.dumps(event)+'\n')
app=Gtk.Application(application_id='org.omarchy.WheelProbe',flags=Gio.ApplicationFlags.NON_UNIQUE)
def activate(app):
    window=Gtk.ApplicationWindow(application=app,title=title)
    window.set_default_size(400,300)
    entry=Gtk.Entry(placeholder_text='Disposable native input QA')
    window.set_child(entry)
    scroll=Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.BOTH_AXES)
    scroll.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
    def on_scroll(controller,x,y):record(dict(event='wheel',x=x,y=y));return True
    scroll.connect('scroll',on_scroll);window.add_controller(scroll)
    keys=Gtk.EventControllerKey.new()
    keys.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
    def on_key(controller,keyval,keycode,state):record(dict(event='key',keyval=keyval));return False
    keys.connect('key-pressed',on_key);window.add_controller(keys)
    window.present();entry.grab_focus()
app.connect('activate',activate);app.run(None)
