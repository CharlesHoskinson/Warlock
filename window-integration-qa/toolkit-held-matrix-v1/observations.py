"""Independent strict oracle for retained raw native/public observation samples."""
IDENTITY=('address','stableId','pid')
def exact(a,b):return isinstance(a,dict) and isinstance(b,dict) and all(a.get(k)==b.get(k) and a.get(k) is not None for k in IDENTITY)
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
  if any(exact(w,source) for w in g['members']) and any(exact(w,peer) for w in g['members']):return True
 raise ValueError('Actual genuine release did not insert source into exact peer group')
