"""Invoke one real AT-SPI action on the exact current private-host taskbar control.

No synthetic accessible nodes, DOM events or native window effects. The actual
WebKit control uses its normal frontend policy and native admission path.
"""
import json,os,pathlib,sys
import gi
gi.require_version('Atspi','2.0')
from gi.repository import Atspi

runtime=pathlib.Path(os.environ['XDG_RUNTIME_DIR']).resolve()
assert os.environ['DBUS_SESSION_BUS_ADDRESS']=='unix:path='+str(runtime/'bus')
assert os.environ['AT_SPI_BUS_ADDRESS']=='unix:path='+str(runtime/'a11y-bus')
assert not pathlib.Path(os.environ['DBUS_SYSTEM_BUS_ADDRESS'].removeprefix('unix:path=')).exists()
assert pathlib.Path(os.environ['HOME']).resolve().is_relative_to(runtime)
pid,identity,name,receipt=sys.argv[1:];pid=int(pid);receipt=pathlib.Path(receipt)
assert pid>0 and not receipt.exists() and receipt.parent.stat().st_uid==os.getuid()
Atspi.set_timeout(500,500);Atspi.init()
matches=[];visited=0
def walk(obj,in_taskbar=False,depth=0):
 global visited
 visited+=1;assert visited<=2048 and depth<=32
 role=obj.get_role_name();label=obj.get_name() or ''
 in_taskbar=in_taskbar or (role=='tool bar' and label=='Warlock taskbar')
 app=obj.get_application();owner=app.get_process_id() if app else 0
 if in_taskbar and owner==pid and role in ['button','push button','toggle button'] and label==name and (not identity or obj.get_accessible_id()==identity):matches.append(obj)
 for index in range(obj.get_child_count()):walk(obj.get_child_at_index(index),in_taskbar,depth+1)
walk(Atspi.get_desktop(0));assert len(matches)==1,('Ambiguous actual taskbar target',len(matches))
obj=matches[0];states=[x.value_nick for x in obj.get_state_set().get_states()]
assert {'enabled','sensitive','showing','visible','focused'}<=set(states),states
action=obj.get_action_iface();actions=[action.get_action_name(i) for i in range(action.get_n_actions())]
indices=[i for i,n in enumerate(actions) if n.lower() in ['click','press','activate']];assert len(indices)==1,actions
before={'pid':pid,'identity':obj.get_accessible_id() or '', 'name':obj.get_name(),'role':obj.get_role_name(),'states':states}
passed=bool(action.do_action(indices[0]));assert passed,'Actual AT-SPI action refused'
packet={'passed':passed,'source':'actual-at-spi-action','before':before,'action':actions[indices[0]],'actionIndex':indices[0],'syntheticNodes':False,'injectedDomEvents':False}
with receipt.open('x') as stream:json.dump(packet,stream,indent=2);stream.write('\n')
print(json.dumps(packet));Atspi.exit()
