#!/usr/bin/env python3
"""Public GTK4 same-process modal/peer fixture. Import does not initialize GTK.
Only startup, dialog open/close, snapshot and normal quit commands are allowed;
all tested pointer/keyboard/focus/window-manager actions come from native input.
"""
from pathlib import Path
import argparse,json,os,re,sys,time
QA=Path('/home/hoskinson/window-integration-qa')

def validate_tag(tag):
 if not re.fullmatch(r'[A-Za-z][A-Za-z0-9]{0,31}',tag):raise ValueError('Invalid fixture tag')
 return tag

def main():
 sys.path.insert(0,str(QA))
 from qa_launch import require_qa_scope,verify_runtime
 require_qa_scope();verify_runtime(Path(os.environ['XDG_RUNTIME_DIR']))
 p=argparse.ArgumentParser();p.add_argument('--state',type=Path,required=True);p.add_argument('--tag',required=True);p.add_argument('--backend',choices=('wayland','x11'),required=True);a=p.parse_args();validate_tag(a.tag)
 if a.state.exists() or a.state.parent.stat().st_uid!=os.getuid() or a.state.parent.stat().st_mode&0o777!=0o700:raise RuntimeError('Fresh owned0700 output required')
 if os.environ.get('GDK_BACKEND')!=a.backend:raise RuntimeError('Explicit selected GDK backend required')
 import gi
 gi.require_version('Gtk','4.0');gi.require_version('Gdk','4.0')
 from gi.repository import Gtk,Gdk,GLib,Gio
 Gtk.init();display=Gdk.Display.get_default();actual=display.__gtype__.name if display else ''
 if ('Wayland' if a.backend=='wayland' else 'X11') not in actual:raise RuntimeError('Actual GTK display backend mismatch')
 app=Gtk.Application(application_id='org.omarchy.Interruption'+a.tag,flags=Gio.ApplicationFlags.NON_UNIQUE)
 windows={};buttons={};epochs={r:0 for r in ('owner','child','nested','peer')};counts={r:0 for r in epochs};events=[]
 def event(kind,role,**fields):
  events.append(dict(kind=kind,role=role,epoch=epochs[role],time=time.monotonic(),**fields));del events[:-512]
 def snapshot():
  rows={}
  for role,w in list(windows.items()):
   b=buttons[role];ok,bounds=b.compute_bounds(w);surface=w.get_surface();parent=w.get_transient_for()
   rows[role]=dict(title=w.get_title(),epoch=epochs[role],mapped=w.get_mapped(),active=w.is_active(),modal=w.get_modal(),
    transientTitle=parent.get_title() if parent else None,client=[w.get_width(),w.get_height()],surfaceTransform=list(w.get_surface_transform()),
    surfaceType=surface.__gtype__.name if surface else None,
    buttonClient=[bounds.get_x(),bounds.get_y(),bounds.get_width(),bounds.get_height()] if ok else None,callbacks=counts[role])
  value=json.dumps(dict(pid=os.getpid(),backend=actual,windows=rows,events=events),sort_keys=True)
  temp=a.state.with_suffix('.new');fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'w') as f:f.write(value)
  os.replace(temp,a.state);return True
 def make(role,parent=None):
  if role in windows:raise RuntimeError('Window already exists')
  epochs[role]+=1;w=Gtk.ApplicationWindow(application=app,title='Toolkit '+a.tag+' '+role)
  w.set_decorated(False);w.set_resizable(True);w.set_default_size(*{'owner':(460,300),'peer':(460,300),'child':(320,180),'nested':(240,140)}[role])
  if parent:w.set_transient_for(windows[parent]);w.set_modal(True);w.set_destroy_with_parent(True)
  b=Gtk.Button(label='Public callback '+role);b.set_hexpand(False);b.set_vexpand(False);b.set_halign(Gtk.Align.CENTER);b.set_valign(Gtk.Align.CENTER)
  def clicked(button):counts[role]+=1;event('clicked',role);snapshot()
  b.connect('clicked',clicked);w.set_child(b);windows[role]=w;buttons[role]=b
  w.connect('notify::is-active',lambda widget,prop:event('active',role,active=widget.is_active()))
  w.connect('map',lambda widget:event('map',role));w.connect('unmap',lambda widget:event('unmap',role))
  w.present();event('created',role)
 def close(role):
  descendants={'owner':['nested','child','owner'],'child':['nested','child'],'nested':['nested'],'peer':['peer']}[role]
  for r in descendants:
   if r in windows:window=windows.pop(r);buttons.pop(r);event('destroy-request',r);window.destroy()
 def activate(application):make('owner');make('peer')
 def command(source,condition):
  line=sys.stdin.readline()
  if not line:app.quit();return False
  try:
   op=json.loads(line).get('operation')
   if op=='open':make('child','owner')
   elif op=='nested':make('nested','child')
   elif op=='closeNested':close('nested')
   elif op=='closeChild':close('child')
   elif op=='destroyOwner':close('owner')
   elif op=='snapshot':pass
   elif op=='quit':
    print(json.dumps(dict(ack=True,operation=op)),flush=True);app.quit();return False
   else:raise ValueError('Unknown public fixture command')
   snapshot();print(json.dumps(dict(ack=True,operation=op)),flush=True)
  except Exception as e:print(json.dumps(dict(ack=False,error=type(e).__name__+': '+str(e))),flush=True)
  return True
 app.connect('activate',activate)
 GLib.io_add_watch(sys.stdin.fileno(),GLib.IO_IN|GLib.IO_HUP,command)
 GLib.timeout_add(100,snapshot)
 result=app.run([sys.argv[0]])
 for role,w in list(windows.items()):w.destroy()
 return result
if __name__=='__main__':raise SystemExit(main())
