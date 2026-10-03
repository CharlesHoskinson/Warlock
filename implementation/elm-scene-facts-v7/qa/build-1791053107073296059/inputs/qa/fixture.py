"""Owned real Wayland remap fixture; control path supplied only by private QA."""
import gi,json,signal,sys
from pathlib import Path
gi.require_version('Gtk','4.0')
from gi.repository import Gtk,GLib
control=Path(sys.argv[1]);window=Gtk.Window(title='ELM-AUTHORITY-FIXTURE');window.set_default_size(280,180)
loop=GLib.MainLoop();window.present()
def quit_():
 window.destroy();loop.quit();return False
def poll():
 if control.exists():
  request=json.loads(control.read_text());control.unlink()
  if request['op']=='hide':window.hide()
  elif request['op']=='show':window.present()
  elif request['op']=='quit':return quit_()
 return True
GLib.timeout_add(40,poll);GLib.unix_signal_add(GLib.PRIORITY_DEFAULT,signal.SIGTERM,quit_);loop.run()
