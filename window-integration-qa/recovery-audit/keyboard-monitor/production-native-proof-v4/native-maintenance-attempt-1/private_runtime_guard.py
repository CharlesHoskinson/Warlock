"""Fresh fixture-only guard; explicit owned private bus/display and QA scope."""
import importlib.util,os
from pathlib import Path
ROOT=Path('/home/hoskinson/window-integration-qa')
spec=importlib.util.spec_from_file_location('_pointer_private_qa_launch',ROOT/'qa_launch.py')
qa=importlib.util.module_from_spec(spec);spec.loader.exec_module(qa)
def checked_runtime():
    qa.require_qa_scope()
    runtime=qa.verify_runtime(os.environ['XDG_RUNTIME_DIR'])
    if os.environ.get('DBUS_SESSION_BUS_ADDRESS')!='unix:path='+str(runtime/'bus') or os.environ.get('DISPLAY') or os.environ.get('HYPR_A11Y_BRIDGE_PRIVATE')!='1':
        raise RuntimeError('fixture needs its exact private native bus/runtime/flag')
    peer=qa.verify_parent(os.environ)
    pid=int(os.environ['POINTER_QA_COMPOSITOR_PID']);start=os.environ['POINTER_QA_COMPOSITOR_START']
    actual=Path('/proc/'+str(pid)+'/stat').read_text().rsplit(')',1)[1].split()[19]
    if peer['pid']!=pid or actual!=start:raise RuntimeError('fixture Wayland server identity changed')
    return runtime
def reader_entry():
    root=Path(os.environ['ORCA_QA_READER_ROOT'])
    if root!=ROOT/'orca-reader':raise RuntimeError('unexpected actual signed Orca prefix')
    entry=root/'prefix/usr/bin/orca'
    if not entry.is_file():raise RuntimeError('actual Orca entry unavailable')
    return entry
