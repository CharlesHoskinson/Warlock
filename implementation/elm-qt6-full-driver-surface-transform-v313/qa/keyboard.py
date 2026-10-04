"""Owning Qt6 keyboard event conversion; actual keymap and compiled Qt objects."""
import re
class Refused(ValueError):pass

def shift_pair(trace,baseline,*,surface_id,xkb_shift_mask,qt_shift_mask,mapping,seat_registry_id):
 if type(baseline) is not int or not 0<=baseline<=len(trace.calls):raise Refused('keyboard trace baseline')
 if type(surface_id) is not int or not 1<=surface_id<2**32:raise Refused('current Qt surface resource')
 if type(xkb_shift_mask) is not int or xkb_shift_mask<=0 or type(qt_shift_mask) is not int or qt_shift_mask<=0:raise Refused('actual XKB and compiled Qt modifier masks')
 if type(mapping) is not dict or set(mapping)!={'0',str(xkb_shift_mask)}:raise Refused('actual owning-keymap Qt conversion table')
 if type(seat_registry_id) is not int or not 0<seat_registry_id<2**32:raise Refused('owning keymap registry seat')
 for raw,entry in mapping.items():
  if type(entry) is not dict or set(entry)!={'nativeScanCode','nativeVirtualKey','qtKey','qtModifiers','nativeModifiers'} or any(type(v) is not int or not 0<=v<2**32 for v in entry.values()):raise Refused('closed canonical compiled Qt conversion fields')
  if entry['nativeModifiers']!=int(raw) or entry['qtModifiers'] not in (0,qt_shift_mask):raise Refused('bound compiled Qt modifier conversion')
 focus={};mods={};selected=[];seats={};keyboards={} 
 def values(raw,count):
  if not re.fullmatch(r'[0-9]+(?:, [0-9]+){'+str(count-1)+'}',raw):raise Refused('canonical keyboard wire values')
  result=[int(v) for v in raw.split(', ')]
  if any(v>=2**32 for v in result):raise Refused('bounded keyboard values')
  return result
 for index,row in enumerate(trace.calls):
  if row['direction']=='request' and row['iface']=='wl_registry' and row['method']=='bind':
   m=re.fullmatch(r'([1-9][0-9]*), "wl_seat", ([1-9][0-9]*), new id wl_seat[@#]([1-9][0-9]*)',row['args'])
   if m:
    obj=int(m[3])
    if obj in seats:raise Refused('live seat object reused')
    seats[obj]=int(m[1])
  elif row['direction']=='event' and row['iface']=='wl_registry' and row['method']=='global_remove':
   if not re.fullmatch(r'[1-9][0-9]*',row['args']):raise Refused('registry global removal')
   removed=int(row['args']);seats={k:v for k,v in seats.items() if v!=removed};keyboards={k:v for k,v in keyboards.items() if v!=removed}
  elif row['direction']=='request' and row['iface']=='wl_seat' and row['method']=='get_keyboard':
   m=re.fullmatch(r'new id wl_keyboard[@#]([1-9][0-9]*)',row['args'])
   if not m or row['id'] not in seats:raise Refused('owning keyboard creation seat')
   obj=int(m[1])
   if obj in keyboards:raise Refused('live keyboard object reused')
   keyboards[obj]=seats[row['id']];focus.pop(obj,None);mods.pop(obj,None)
  elif row['direction']=='request' and row['iface']=='wl_keyboard' and row['method']=='release':
   keyboards.pop(row['id'],None);focus.pop(row['id'],None);mods.pop(row['id'],None)
  elif row['direction']=='request' and row['iface']=='wl_seat' and row['method']=='release':
   global_id=seats.pop(row['id'],None);keyboards={k:v for k,v in keyboards.items() if v!=global_id}
  if row['iface']!='wl_keyboard' or row['direction']!='event':continue
  oid=row['id'];method=row['method']
  if method=='enter':
   match=re.match(r'([0-9]+), wl_surface[@#]([1-9][0-9]*), ',row['args'])
   if not match:raise Refused('actual keyboard enter resource')
   focus[oid]=int(match.group(2))
  elif method=='leave':focus.pop(oid,None)
  elif method=='modifiers':
   serial,depressed,latched,locked,group=values(row['args'],5);raw=depressed|latched|locked
   if group!=0 or raw&~xkb_shift_mask:raise Refused('declared nontext keymap modifier scope')
   mods[oid]=raw
  elif method=='key' and index>=baseline:
   serial,stamp,key,state=values(row['args'],4)
   if keyboards.get(oid)!=seat_registry_id or focus.get(oid)!=surface_id or key!=42 or state not in (0,1) or oid not in mods:raise Refused('entire keyboard interval current Shift_L recipient')
   expected=mapping[str(mods[oid])]
   if expected.get('nativeModifiers')!=mods[oid] or expected.get('qtModifiers') not in (0,qt_shift_mask):raise Refused('actual compiled Qt conversion domain')
   selected.append(dict(expected,keyboardResource=oid,key=key,state=state,time=stamp,wireIndex=index,serial=serial))
 if len(selected)!=2 or [r['state'] for r in selected]!=[1,0] or selected[0]['keyboardResource']!=selected[1]['keyboardResource']:raise Refused('one complete nonrepeat Qt key pair')
 return selected
