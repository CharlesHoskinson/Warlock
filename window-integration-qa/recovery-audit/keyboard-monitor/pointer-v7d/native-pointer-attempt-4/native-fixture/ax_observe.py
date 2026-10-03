"""Reads actual public AX references; never supplies metadata to the bridge."""
import gi,json,os,sys
from pathlib import Path
gi.require_version('Atspi','2.0')
from gi.repository import Atspi
runtime=Path(os.environ['XDG_RUNTIME_DIR'])
assert str(runtime).startswith('/tmp/kbn-') and runtime.stat().st_mode&0o777==0o700
assert os.environ['DBUS_SESSION_BUS_ADDRESS']=='unix:path='+str(runtime/'bus')
Atspi.init()
root=Atspi.get_desktop(0)
def describe(obj,depth=0):
    row=dict(name=obj.get_name(),role=obj.get_role_name(),pid=obj.get_process_id(),
             app_bus=obj.app.bus_name,object_path=obj.path)
    if depth<2:row['children']=[describe(obj.get_child_at_index(i),depth+1) for i in range(min(obj.get_child_count(),32))]
    return row
rows=[]
for i in range(min(root.get_child_count(),64)):
    try:rows.append(describe(root.get_child_at_index(i)))
    except Exception as error:rows.append(dict(error=str(error)))
print(json.dumps(rows));Atspi.exit()
