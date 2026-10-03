"""Capture import-only GTK4 introspection loader closure; never initialize GTK."""
from pathlib import Path
import hashlib,json,os,sys
B=Path(__file__).resolve().parent

def main():
 import gi
 gi.require_version('Gtk','4.0');gi.require_version('Gdk','4.0')
 from gi.repository import Gtk,Gdk,GLib,Gio
 inputs={};links={}
 def add(path):
  path=Path(path)
  if path.is_symlink():links[str(path)]=os.readlink(path);add(path.resolve());return
  if path.is_file():inputs[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
 for module in list(sys.modules.values()):
  path=getattr(module,'__file__',None)
  if path and Path(path).exists():add(path)
 for row in Path('/proc/self/maps').read_text().splitlines():
  fields=row.split(maxsplit=5)
  if len(fields)==6 and fields[5].startswith('/'):add(fields[5])
 for root in (Path(gi.__file__).parent,Path('/usr/lib/girepository-1.0')):
  for path in root.rglob('*'):
   if '__pycache__' not in path.parts and (path.is_file() or path.is_symlink()):add(path)
 for path in Path('/usr/lib').glob('libgtk-4.so*'):add(path)
 for path in Path('/usr/lib').glob('libgirepository-*.so*'):add(path)
 path=B/'gtk-loader-inputs.json'
 with path.open('x') as stream:json.dump(dict(inputs=inputs,symlinks=links,gtkInitialized=False,displayConnected=False,nativeLaunch=False),stream,indent=2);stream.write('\n')
 path.chmod(0o600);print(json.dumps(dict(inputs=len(inputs),links=len(links),nativeLaunch=False)))
if __name__=='__main__':main()
