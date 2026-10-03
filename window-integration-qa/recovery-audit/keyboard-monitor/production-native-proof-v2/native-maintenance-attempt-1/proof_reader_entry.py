"""Owned fixture entry; only acceptance seam is actual Control(approved=False)."""
import json,os,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
PAYLOAD=HERE/'payload'
sys.path.insert(0,str(PAYLOAD))
from private_runtime_guard import checked_runtime
runtime=checked_runtime()
for key in ('HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME'):
    if not Path(os.environ[key]).resolve().is_relative_to(runtime):raise RuntimeError('reader profile escaped owned runtime')
import control,reader_bootstrap
actual=control.Control
def private_factory(*args,**kwargs):
    if 'approved' in kwargs:raise RuntimeError('fixture approval injection duplicated')
    return actual(*args,approved=False,**kwargs)
reader_bootstrap.Control=private_factory
# Public state observer runs only after actual Orca's GLib main loop begins.
# No event/command/device is invented or replaced by the observation.
if os.environ['PROOF_READER_MODE']=='enabled':
    from gi.repository import GLib
    def observe():
        from orca import ax_device_manager,command_manager,learn_mode_presenter,mouse_review
        device=ax_device_manager.get_manager().get_device();commands=command_manager.get_manager().get_keyboard_commands()
        reviewer=mouse_review.get_reviewer();item=reviewer.get_current_item()
        try:target=dict(name=item.get_name(),app_bus=item.app.bus_name,object_path=item.path) if item else None
        except Exception as error:target=dict(error=repr(error))
        value=dict(time=time.monotonic(),fixtureControlApprovedFalse=True,backend=device.__gtype__.name if device else None,
            learn=learn_mode_presenter.get_presenter().is_active(),mouseEnabled=reviewer.get_is_enabled(),currentItem=target,
            commands=sorted((c.get_name(),c.is_active(),c.is_enabled(),c.is_suspended()) for c in commands.values()))
        Path(os.environ['PROOF_READER_STATE']).write_text(json.dumps(value));return True
    GLib.timeout_add(40,observe)
try:reader_bootstrap.main()
except control.Refused as error:
    result=dict(refused=True,error=str(error),orcaImported=any(name=='orca' or name.startswith('orca.') for name in sys.modules),fixtureControlApprovedFalse=True)
    Path(os.environ['PROOF_READER_RESULT']).write_text(json.dumps(result));raise SystemExit(3)
