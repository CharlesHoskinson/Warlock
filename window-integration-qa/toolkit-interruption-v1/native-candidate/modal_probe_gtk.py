#!/usr/bin/env python3
"""Disposable native transient/modal family; peer runs in a separate process."""
import gi, json, sys
from pathlib import Path
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib

mode, control, log = sys.argv[1:]
control, log = Path(control), Path(log)
app = Gtk.Application(application_id='org.omarchy.ModalFamilyQA' if mode == 'family' else 'org.omarchy.ModalPeerQA', flags=Gio.ApplicationFlags.NON_UNIQUE)
windows = {}
last_command = ''

def record(**event):
    with log.open('a') as out:
        out.write(json.dumps(event) + '\n')

def create(name, width, height):
    window = Gtk.ApplicationWindow(application=app, title='Modal QA ' + name)
    window.set_default_size(width, height)
    button = Gtk.Button(label=name + ': click to record interaction')
    button.connect('clicked', lambda *args: record(event='click', window=name))
    motion = Gtk.EventControllerMotion.new()
    motion.connect('enter', lambda *args: record(event='pointer-enter', window=name))
    motion.connect('leave', lambda *args: record(event='pointer-leave', window=name))
    button.add_controller(motion)
    window.set_child(button)
    window.connect('notify::is-active', lambda win, *args: record(event='active', window=name, active=win.is_active()))
    windows[name] = window
    return window

def open_modal(name='child', parent='owner'):
    child = create(name, 320 if name=='child' else 240, 180 if name=='child' else 140)
    child.set_transient_for(windows[parent])
    child.set_modal(True)
    child.set_destroy_with_parent(True)
    child.present()
    record(event='modal', window=name, parent=parent, modal=child.get_modal(), transient=child.get_transient_for() is windows[parent])

def poll():
    global last_command
    command = control.read_text().strip() if control.exists() else ''
    if command and command != last_command:
        last_command = command
        if command == 'open': open_modal()
        elif command == 'close': windows['child'].destroy(); windows.pop('child')
        elif command == 'nested': open_modal('nested','child')
        elif command == 'close_nested': windows['nested'].destroy(); windows.pop('nested')
    return True

def activate(app):
    if mode == 'family':
        create('owner', 580, 380).present()
        GLib.timeout_add(100, poll)
    else:
        create('peer', 380, 300).present()

app.connect('activate', activate)
app.run(None)
