#!/usr/bin/env python3
"""Manager-only public ABI client: valid pure Wayland, no X fallback key calls."""
from pathlib import Path
import importlib.util,json,os,sys
QA=Path('/home/hoskinson/window-integration-qa');sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope,verify_runtime
from abi_guard import session_preflight
OFFICIAL=QA/'orca-reader/prefix/usr/lib/python3.14/site-packages/orca/ax_device_manager.py'

def main():
 require_qa_scope()
 root=verify_runtime(Path(os.environ['KEYBOARD_ABI_RUNTIME']))
 assert root==Path(os.environ['XDG_RUNTIME_DIR']) and not os.environ.get('DISPLAY') and not os.environ.get('ATSPI_USE_LEGACY_DEVICE')
 os.environ['ATSPI_USE_A11Y_MANAGER_DEVICE']='1'
 app_id,tag=sys.argv[1:3];assert tag in ('orca','generic')
 import gi
 from gi.repository import GLib,Gio
 guard,transport=session_preflight(root,os.environ,Gio,GLib)
 # Atspi is imported only after verified private transport/owner/protocol.
 gi.require_version('Atspi','2.0');from gi.repository import Atspi
 manager=None
 if app_id=='org.gnome.Orca':
  spec=importlib.util.spec_from_file_location('official_orca_ax_device_manager',OFFICIAL);official=importlib.util.module_from_spec(spec);spec.loader.exec_module(official)
  manager=official.AXDeviceManager();manager.activate();device=manager.get_device()
 else:device=Atspi.Device.new_full(app_id)
 guard.attach(device)
 events=[];report={'appID':app_id,'deviceType':device.__gtype__.name,'officialOrcaFactory':app_id=='org.gnome.Orca','events':events,'nativeInputClaim':False,'transport':transport,'result':'active'}
 device.connect('key-pressed',lambda dev,*args:events.append({'pressed':True,'args':args}))
 device.connect('key-released',lambda dev,*args:events.append({'pressed':False,'args':args}))
 definition=Atspi.KeyDefinition();definition.keysym=ord('h');definition.keycode=0;definition.modifiers=0
 report['grabID']=guard.invoke('add_key_grab',definition,None);assert report['grabID']
 report['mappedCapsModifier']=guard.invoke('map_keysym_modifier',65509);assert report['mappedCapsModifier']
 report['grabAllReturned']=guard.invoke('grab_keyboard');guard.invoke('ungrab_keyboard')
 (root/(tag+'-ready')).touch();loop=GLib.MainLoop();failed=[]
 def tick():
  try:guard.check()
  except Exception as error:failed.append(repr(error));report.update(result='fail',error=repr(error));loop.quit()
  (root/(tag+'-report.json')).write_text(json.dumps(report,indent=2))
  if failed or (root/'clients-exit').exists():loop.quit();return False
  return True
 GLib.timeout_add(30,tick);loop.run()
 if not failed:
  guard.invoke('remove_key_grab',report['grabID']);guard.invoke('unmap_keysym_modifier',65509);report['result']='stopped'
 (root/(tag+'-report.json')).write_text(json.dumps(report,indent=2))
 if manager:manager.deactivate()
 return bool(failed)

if __name__=='__main__':
 try:raise SystemExit(main())
 except Exception as error:print(json.dumps({'result':'refused','error':str(error),'nativeInputClaim':False}),file=sys.stderr);raise SystemExit(2)
