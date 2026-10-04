"""Join owning GTK Wayland keyboard ordering; no keymap or recipient is invented."""
import re
class Refused(ValueError):pass

def shift_pair(trace,baseline,*,surface_id,xkb_shift_mask,gdk_shift_mask):
 if type(baseline) is not int or not 0<=baseline<=len(trace.calls):raise Refused('owning keyboard trace baseline')
 if type(surface_id) is not int or not 1<=surface_id<2**32:raise Refused('current surface resource')
 if type(xkb_shift_mask) is not int or xkb_shift_mask<=0 or type(gdk_shift_mask) is not int or gdk_shift_mask<=0:raise Refused('actual owning keymap modifier masks')
 focus={};mods={};selected=[]
 def values(raw,count):
  if not re.fullmatch(r'[0-9]+(?:, [0-9]+){'+str(count-1)+'}',raw):raise Refused('canonical keyboard wire values')
  result=[int(v) for v in raw.split(', ')];
  if any(v>=2**32 for v in result):raise Refused('bounded keyboard wire values')
  return result
 for index,row in enumerate(trace.calls):
  if row['iface']!='wl_keyboard' or row['direction']!='event':continue
  oid=row['id'];method=row['method']
  if method=='enter':
   match=re.match(r'([0-9]+), wl_surface[@#]([1-9][0-9]*), ',row['args'])
   if not match:raise Refused('actual keyboard enter resource')
   focus[oid]=int(match.group(2))
  elif method=='leave':focus.pop(oid,None)
  elif method=='modifiers':
   serial,depressed,latched,locked,group=values(row['args'],5)
   if group!=0 or (depressed|latched|locked)&~xkb_shift_mask:raise Refused('declared synthetic keymap modifier scope')
   mods[oid]=gdk_shift_mask if (depressed|latched|locked)&xkb_shift_mask else 0
  elif method=='key' and index>=baseline:
   serial,stamp,key,state=values(row['args'],4)
   if focus.get(oid)!=surface_id or key!=42 or state not in (0,1) or oid not in mods:raise Refused('entire keyboard interval exact current Shift_L pair')
   selected.append({'keyboardResource':oid,'key':key,'state':state,'time':stamp,'gdkModifiers':mods[oid],'wireIndex':index,'serial':serial})
 if len(selected)!=2 or [r['state'] for r in selected]!=[1,0] or selected[0]['keyboardResource']!=selected[1]['keyboardResource']:raise Refused('one ordered actual Shift_L pair')
 return selected
