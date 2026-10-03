"""Decode actual probe rows; caller must bind real process/source/socket authority."""
import json,math
from case_authority import token,matches
PLANS={'titlebar':[(272,1),(272,0)],'super-p':[(125,1),(25,1),(25,0),(125,0)],'super-ctrl-t':[(125,1),(29,1),(20,1),(20,0),(29,0),(125,0)]}
def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
def uint(value):return type(value) is int and 0<=value<=2**32-1
def episode(before,after,route,captured,point=None):
 token(captured)
 if route not in PLANS or type(before) is not list or type(after) is not list:raise ValueError('fixed input route and actual probe lists required')
 bound=256 if route=='titlebar' else 512
 plan=PLANS[route]
 if len(after)>bound or len(before)+len(plan)!=len(after) or encoded(before)!=encoded(after[:len(before)]):raise ValueError('exact retained prefix and complete unique event suffix required')
 fresh=after[len(before):]
 for row in after:
  if type(row) is not dict or not uint(row.get('timeMs')) or type(row.get('cancelledAtObservation')) is not bool:raise ValueError('typed complete probe prefix required')
  cf,sf=('button','buttonState') if route=='titlebar' else ('keycode','keyState')
  if not uint(row.get(cf)) or type(row.get(sf)) is not int or row[sf] not in (0,1):raise ValueError('typed whole probe event prefix required')
 if route=='titlebar':
  if type(point) not in (list,tuple) or len(point)!=2 or any(type(n) is not int for n in point):raise ValueError('actual integer cursor witness required')
 else:
  all_rows=before+fresh
  for row in all_rows:
   if type(row) is not dict or type(row.get('sequence')) is not int or row['sequence']<1:raise ValueError('exact actual key sequence required')
  if any(b['sequence']!=a['sequence']+1 for a,b in zip(all_rows,all_rows[1:])):raise ValueError('key event sequence gap or replacement')
 for row,(code,state) in zip(fresh,plan,strict=True):
  if type(row) is not dict or not uint(row.get('timeMs')) or type(row.get('cancelledAtObservation')) is not bool:raise ValueError('typed actual event fields required')
  codefield,statefield=('button','buttonState') if route=='titlebar' else ('keycode','keyState')
  if type(row.get(codefield)) is not int or type(row.get(statefield)) is not int or (row[codefield],row[statefield])!=(code,state):raise ValueError('physical delivered episode differs from frozen route')
  if route=='titlebar':
   native=row.get('native');coords=native.get('cursor') if type(native) is dict else None
   if type(coords) is not list or len(coords)!=2 or any(type(x) not in (int,float) or not math.isfinite(x) for x in coords) or coords!=list(point) or not matches(native.get('hitOwner'),captured):raise ValueError('same actual captured pointer hit and cursor required')
  else:
   seat=row.get('seat')
   if type(seat) is not dict or not matches(seat.get('keyboardOwner'),captured) or not matches(seat.get('coreNativeFocus'),captured) or seat.get('keyboardSurfacePresent') is not True or seat.get('keyboardResourcePresent') is not True:raise ValueError('same actual captured Seat and core key owner required')
   if type(row.get('seatKeySymAvailableAtObservation')) is not bool or not uint(row.get('seatKeySymAtObservation')):raise ValueError('typed pre-core symbol observation required')
 return {'route':route,'observedPressAndRelease':True,'sameCapturedOwner':True,'eventCount':len(fresh),'events':fresh,'nativeAcceptance':False,'scope':'source-bound pre-core delivery episode data; actual native receipt and host lifetime required separately'}
