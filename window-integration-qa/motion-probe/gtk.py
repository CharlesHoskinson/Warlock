import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio
app = Gtk.Application(application_id='org.omarchy.MotionQA', flags=Gio.ApplicationFlags.NON_UNIQUE)
def activate(app):
    window = Gtk.ApplicationWindow(application=app, title='Motion QA GTK')
    window.set_default_size(600, 350)
    window.set_child(Gtk.Label(label='Disposable motion measurement window'))
    window.present()
app.connect('activate', activate)
app.run(None)
