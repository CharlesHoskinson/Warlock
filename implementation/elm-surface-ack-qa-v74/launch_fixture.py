"""Owned real GTK application; control file provides normal shutdown."""
import gi,sys
from pathlib import Path
gi.require_version('Gtk','4.0');from gi.repository import Gtk,GLib
control=Path(sys.argv[1]);loop=GLib.MainLoop()
window=Gtk.Window(title='ELM-CATALOG-LAUNCHED');window.set_default_size(320,220);window.set_child(Gtk.Label(label='Owned catalog launch fixture'))
window.connect('close-request',lambda *_:(loop.quit(),False)[1])
def poll():
 if control.exists():window.destroy();loop.quit();return False
 return True
GLib.timeout_add(40,poll);window.present();loop.run()
