"""Private Omarchy Orca compat entry, with public fresh-device adapters."""
import json,os,runpy,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
COMPAT=HERE/'mouse-review-v2/orca-compat'
sys.path.insert(0,str(COMPAT))
runtime=Path(os.environ['XDG_RUNTIME_DIR'])
assert str(runtime).startswith('/tmp/kbn-') and runtime.stat().st_mode&0o777==0o700
assert os.environ['DBUS_SESSION_BUS_ADDRESS']=='unix:path='+str(runtime/'bus')
assert not os.environ.get('DISPLAY')
from gi.repository import GLib
from capability_adapter import install_private
events=Path(os.environ['POINTER_READER_EVENTS']);state=Path(os.environ['POINTER_READER_STATE'])
def report(event,**fields):
    with events.open('a') as stream:stream.write(json.dumps(dict(time=time.monotonic(),event=event,**fields))+'\n')
caps=install_private(report)
from reader_reconnect_v7 import install
adapter=install(report)
seen_device=None;pointer_handler=None
def pointer(device,obj,x,y):
    report('actual-public-pointer-moved',accessible=describe(obj),x=x,y=y)
def describe(obj):
    if obj is None:return None
    try:return dict(name=obj.get_name(),role=obj.get_role_name(),app_bus=obj.app.bus_name,object_path=obj.path)
    except Exception as error:return dict(error=str(error))
def observe():
    global seen_device,pointer_handler
    from orca import ax_device_manager,command_manager,mouse_review,object_navigator
    assert Path(mouse_review.__file__).resolve()==(COMPAT/'orca/mouse_review.py').resolve()
    device=ax_device_manager.get_manager().get_device()
    if device is not seen_device:
        if seen_device is not None and pointer_handler is not None:seen_device.disconnect(pointer_handler)
        seen_device=device;pointer_handler=device.connect('pointer-moved',pointer) if device else None
    commands=command_manager.get_manager().get_keyboard_commands();reviewer=mouse_review.get_reviewer()
    current=describe(reviewer.get_current_item())
    value=dict(time=time.monotonic(),identity='Omarchy Orca compat',mouseSource=str(mouse_review.__file__),
        epoch=adapter.epoch,appliedEpoch=adapter.applied_epoch,owner=adapter.owner,
        backend=device.__gtype__.name if device else None,watch=adapter.watch_requested,
        full=adapter.full_requested,paused=adapter.pause_requested,mouseEnabled=reviewer.get_is_enabled(),
        currentItem=current,commands=sorted((c.get_name(),c.is_active(),c.is_enabled(),c.is_suspended()) for c in commands.values()))
    state.write_text(json.dumps(value));state.chmod(0o600)
    if current:report('actual-public-current-item',accessible=current)
    return True
GLib.timeout_add(15,observe)
orca=Path.home()/'window-integration-qa/orca-reader/prefix/usr/bin/orca'
sys.argv[0]=str(orca);runpy.run_path(str(orca),run_name='__main__')
