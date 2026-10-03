"""B-only actual layer episode data. A2 native-window token decoder is unchanged."""
import copy
import math
from decimal import Decimal
from popup_authority import exact,integer
def uint(v):return type(v)is int and 0<=v<=2**32-1
def episode(before,after,route,expected,*,allow_pending=False):
 if route not in('pointer','return') or type(before)is not list or type(after)is not list:raise ValueError('Exact B input route/lists required')
 bound=256 if route=='pointer' else 512
 if len(after)>bound or len(after)<len(before) or len(after)>len(before)+2 or not exact(before,after[:len(before)]):raise ValueError('Complete retained prefix and exact bounded suffix required')
 for row in after:
  if type(row)is not dict or type(row.get('sequence'))is not int or not 0<row['sequence']<=2**53-1 or not uint(row.get('timeMs')) or type(row.get('cancelledAtObservation'))is not bool:raise ValueError('Actual typed event prefix required')
  code,state=('button','buttonState')if route=='pointer'else('keycode','keyState')
  if not uint(row.get(code)) or type(row.get(state))is not int or row[state]not in(0,1):raise ValueError('Actual typed event code/state required')
 if any(b['sequence']!=a['sequence']+1 for a,b in zip(after,after[1:])):raise ValueError('Actual event sequence gap/eviction/replacement')
 fresh=after[len(before):]
 point=expected['point'];layer=expected['layer']
 if type(point)is not list or len(point)!=2 or any(type(n)is not int for n in point):raise ValueError('Exact admitted integer point required')
 for row,(code,state)in zip(fresh,[(272,1),(272,0)]if route=='pointer'else[(28,1),(28,0)],strict=False):
  cf,sf=('button','buttonState')if route=='pointer'else('keycode','keyState')
  if (row[cf],row[sf])!=(code,state) or row['cancelledAtObservation']is not False:raise ValueError('Actual B popup episode/cancellation differs')
  native=row.get('native')
  if type(native)is not dict:raise ValueError('Actual event-time native layer snapshot required')
  if route=='pointer':
   cursor=native.get('cursor')
   if native.get('pointerSurfacePresent')is not True or not exact(native.get('pointerLayerOwner'),layer) or type(cursor)is not list or len(cursor)!=2 or any(type(v)not in(int,float) or not math.isfinite(v) for v in cursor) or any(Decimal(str(v))!=Decimal(p)for v,p in zip(cursor,point)):raise ValueError('Same actual popup pointer layer/integer cursor required')
  else:
   if native.get('keyboardSurfacePresent')is not True or native.get('keyboardResourcePresent')is not True or not exact(native.get('keyboardLayerOwner'),layer):raise ValueError('Same actual popup Seat keyboard layer/resource required')
   if row.get('seatKeySymAvailableAtObservation')is not True or not uint(row.get('seatKeySymAtObservation')) or row['seatKeySymAtObservation']!=65293:raise ValueError('Actual pre-core Return symbol required')
 if len(fresh)!=2:
  if allow_pending:return None
  raise ValueError('Complete actual popup press/release episode required')
 return {'profile':'b-popup-layer-input-v1','route':route,'before':copy.deepcopy(before),'after':copy.deepcopy(after),'popupWitness':copy.deepcopy(expected['popupWitness']),
  'observedPressAndRelease':True,'nativeAcceptance':False,'scope':'pre-core event-time layer evidence; actual QML callback/native receipt required separately'}
