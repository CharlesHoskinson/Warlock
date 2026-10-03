"""Independent strict oracle for retained raw native/public observation samples."""
import re
IDENTITY=('address','stableId','pid')
def valid_identity(a):
 return (isinstance(a,dict) and isinstance(a.get('address'),str) and re.fullmatch(r'0x[0-9a-f]{1,16}',a['address']) is not None
  and isinstance(a.get('stableId'),str) and re.fullmatch(r'[0-9a-f]{1,16}',a['stableId']) is not None
  and type(a.get('pid')) is int and 1<=a['pid']<(1<<31))
def exact(a,b):return valid_identity(a) and valid_identity(b) and all(a[k]==b[k] for k in IDENTITY)
def group_snapshot(state):
 groups=[]
 for g in state['groups']:
  project=lambda w:tuple(w[k] for k in IDENTITY)
  groups.append((project(g['head']),project(g['current']),tuple(project(w) for w in g['members']),g['locked'],g['denied']))
 return sorted(groups)
def captured(state,target,mode,button):
 if not exact(state['coreDragTarget'],target):raise ValueError('Core gesture exact native lifetime mismatch')
 if state['coreDragMode']!=mode:raise ValueError('Core gesture actual native mode mismatch')
 if state['signalDownButtonIds']!=[button]:raise ValueError('Actual one owned button signal must remain down')
 if any(state[k] for k in ('sessionLocked','exclusiveLayers','constrained','seatGrab','captured','dnd')):raise ValueError('Private competing input authority refuses gesture')
 return True
def retired(before,after,independent=None):
 if after['coreDragTarget'] is not None:raise ValueError('Exact native core controller not retired')
 if group_snapshot(before)!=group_snapshot(after):raise ValueError('Nonrelease interruption mutated actual group')
 if independent is not None and not exact(after['nativeFocus'],independent):raise ValueError('Nonrelease interruption stole independent native focus')
 if after['signalDownButtonIds']!=before['signalDownButtonIds']:raise ValueError('Retirement fabricated genuine button release')
 return True
def released(state):
 if state['coreDragTarget'] is not None or state['heldButtons'] or state['signalDownButtonIds']:raise ValueError('Actual genuine release did not quiesce button/controller')
 if any(state[k] for k in ('sessionLocked','exclusiveLayers','constrained','seatGrab','captured','dnd')):raise ValueError('Competing input state remains after release')
 return True
def positive_group_drop(state,source,peer):
 for g in state['groups']:
  if len(g['members'])==2 and exact(g['head'],peer) and any(exact(w,source) for w in g['members']) and any(exact(w,peer) for w in g['members']) and any(exact(g['current'],w) for w in (source,peer)):return True
 raise ValueError('Actual genuine release did not insert source into exact peer group')
