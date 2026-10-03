#!/usr/bin/env python3
"""Real official Orca factory or public AT-SPI client; private-bus ABI only."""
import gc,importlib.machinery,json,os,sys,time
from pathlib import Path
import gi
gi.require_version('Atspi','2.0')
from gi.repository import Atspi,GLib,Gio

ROOT=Path(os.environ['KEYBOARD_ABI_RUNTIME']);app_id=sys.argv[1];tag=sys.argv[2]
assert ROOT==Path(os.environ['XDG_RUNTIME_DIR']) and str(ROOT).startswith('/tmp/kbd-')
events=[]
if app_id=='org.gnome.Orca':
    path=Path.home()/'window-integration-qa/orca-reader/prefix/usr/lib/python3.14/site-packages/orca/ax_device_manager.py'
    official=importlib.machinery.SourceFileLoader('official_orca_ax_device_manager',str(path)).load_module()
    manager=official.AXDeviceManager();manager.activate();device=manager.get_device()
else:device=Atspi.Device.new_full(app_id)
report={'appID':app_id,'deviceType':device.__gtype__.name,'officialOrcaFactory':app_id=='org.gnome.Orca','events':events,'nativeInputClaim':False}
device.connect('key-pressed',lambda dev,*args:events.append({'pressed':True,'args':args}))
device.connect('key-released',lambda dev,*args:events.append({'pressed':False,'args':args}))
definition=Atspi.KeyDefinition();definition.keysym=ord('h');definition.keycode=0;definition.modifiers=0
report['grabID']=device.add_key_grab(definition,None)
report['mappedCapsModifier']=device.map_keysym_modifier(65509)
report['grabAllReturned']=device.grab_keyboard();device.ungrab_keyboard()
(ROOT/(tag+'-ready')).touch()
loop=GLib.MainLoop()
def tick():
    (ROOT/(tag+'-report.json')).write_text(json.dumps(report,indent=2))
    if (ROOT/'clients-exit').exists():loop.quit();return False
    return True
GLib.timeout_add(30,tick);loop.run();tick()
