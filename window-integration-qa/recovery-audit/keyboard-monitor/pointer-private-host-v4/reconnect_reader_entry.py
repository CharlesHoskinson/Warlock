"""Private test launcher: actual Orca entry point with scoped reconnect import."""
import json, os, runpy, sys, time
from pathlib import Path
from gi.repository import GLib
from reader_reconnect import install

from private_runtime_guard import checked_runtime,reader_entry
runtime=checked_runtime()
events=Path(os.environ['KEYBOARD_RECONNECT_EVENTS'])
state=Path(os.environ['KEYBOARD_RECONNECT_STATE'])
def report(event, **fields):
    with events.open('a') as stream:
        stream.write(json.dumps(dict(time=time.monotonic(),event=event,**fields))+'\n')
adapter=install(report)
def observe():
    from orca import ax_device_manager,command_manager,learn_mode_presenter
    device=ax_device_manager.get_manager().get_device()
    commands=command_manager.get_manager().get_keyboard_commands()
    state.write_text(json.dumps(dict(time=time.monotonic(),epoch=adapter.epoch,
        appliedEpoch=adapter.applied_epoch,owner=adapter.owner,
        backend=device.__gtype__.name if device else None,
        watch=adapter.watch_requested,full=adapter.full_requested,paused=adapter.pause_requested,
        learn=learn_mode_presenter.get_presenter().is_active(),
        commands=sorted((c.get_name(),c.is_active(),c.is_enabled(),c.is_suspended()) for c in commands.values()))))
    state.chmod(0o600)
    return True
GLib.timeout_add(100,observe)
orca=reader_entry()
sys.argv[0]=str(orca)
runpy.run_path(str(orca),run_name='__main__')
