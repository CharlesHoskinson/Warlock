"""Strict GTK role journal consumer; toolkit facts remain distinct from native proof."""
import json,math,re
class Refused(ValueError):pass

def integer(v,minimum,maximum):
 if type(v) is not int or not minimum<=v<=maximum:raise Refused('canonical journal integer')
 return v
def pairs(rows):
 result={}
 for key,value in rows:
  if key in result:raise Refused('duplicate journal key')
  result[key]=value
 return result
def constant(value):raise Refused('nonfinite JSON')
def parse(raw,*,pid,started,previous=None):
 if type(raw) is not bytes or len(raw)>2*1024*1024:raise Refused('journal bytes')
 if type(started) is not str or not re.fullmatch(r'[1-9][0-9]{0,19}',started):raise Refused('process start identity')
 integer(pid,2,2**31-1);start=integer(int(started),1,2**63-1)
 complete=raw[:raw.rfind(b'\n')+1]
 rows=[json.loads(line,object_pairs_hook=pairs,parse_constant=constant) for line in complete.decode('utf-8',errors='strict').splitlines()]
 if len(rows)>16384:raise Refused('journal row bound')
 if previous is not None and rows[:len(previous)]!=previous:raise Refused('changed observed prefix')
 last=0;monotonic=0;request=0
 for row in rows:
  if type(row) is not dict or row.get('schema')!=1 or type(row.get('schema')) is not int:raise Refused('journal schema')
  if integer(row.get('pid'),2,2**31-1)!=pid or integer(row.get('processStarted'),1,2**63-1)!=start:raise Refused('journal actor ownership')
  seq=integer(row.get('sequence'),1,2**63-1);clock=integer(row.get('monotonicUs'),1,2**63-1);req=integer(row.get('requestSequence'),0,2**63-1)
  if seq<=last or clock<monotonic or req<request:raise Refused('journal ordering')
  last=seq;monotonic=clock;request=req
  if type(row.get('event')) is not str or not 1<=len(row['event'])<=64:raise Refused('event name')
  if row.get('event') in ('refusal','failed-exit'):raise Refused('actual fixture refusal')
  if 'role' in row:
   if row['role'] not in ('A','B','C','D','P'):raise Refused('role domain')
   integer(row.get('instance'),1,2**63-1);integer(row.get('mapGeneration'),0,2**63-1);integer(row.get('surfaceId'),0,2**32-1)
  for key in ['surfaceX','surfaceY','widgetX','widgetY','nativeTransformX','nativeTransformY']:
   if key in row:
    n=row[key]
    if type(n) not in (int,float) or abs(n)>2**23 or (type(n) is float and not math.isfinite(n)):raise Refused('finite coordinate')
 return rows

def full_pointer_interval(rows,baseline,*,role,instance,surface_id,expected_surface,button=1):
 # Keep every role/button. Negative delivery is not inferred from a selected pair.
 selected=[r for r in rows if r['sequence']>baseline and r['event'] in ('button-press','button-release')]
 if len(selected)!=2:raise Refused('entire interval exact pair')
 for row,name in zip(selected,('button-press','button-release')):
  if row.get('event')!=name or row.get('role')!=role or row.get('instance')!=instance or row.get('sourceSurfaceId')!=surface_id or row.get('surfaceId')!=surface_id:raise Refused('actual role/resource recipient')
  if type(row.get('button')) is not int or row['button']!=button or type(row.get('rawButton')) is not int or row['rawButton']!=button:raise Refused('explicit GDK button domain')
  if row.get('hasSurfacePosition') is not True or type(row.get('hasSurfacePosition')) is not bool:raise Refused('actual GdkEvent position')
  actual=[row.get('surfaceX'),row.get('surfaceY')]
  if any(type(n) not in (int,float) or abs(n)>2**23 or (type(n) is float and not math.isfinite(n)) for n in actual):raise Refused('coordinate bound')
  if actual!=expected_surface:raise Refused('surface coordinate mismatch')
 return selected

def blocked_interval(rows,baseline):
 selected=[r for r in rows if r['sequence']>baseline and r['event'] in ('button-press','button-release')]
 if selected:raise Refused('blocked press/release leaked to application')
 return []

def full_key_interval(rows,baseline,*,role,instance,surface_id,keyval,keycode,modifiers=0):
 selected=[r for r in rows if r['sequence']>baseline and r['event'] in ('key-press','key-release')]
 if len(selected)!=2:raise Refused('entire keyboard interval exact pair')
 for row,name in zip(selected,('key-press','key-release')):
  if row.get('event')!=name or row.get('role')!=role or row.get('instance')!=instance or row.get('sourceSurfaceId')!=surface_id or row.get('surfaceId')!=surface_id:raise Refused('actual keyboard role/resource recipient')
  if row.get('rawEventAvailable') is not True:raise Refused('actual raw GDK keyboard event required')
  for field,expected in [('keyval',keyval),('rawKeyval',keyval),('keycode',keycode),('rawKeycode',keycode),('modifiers',modifiers),('rawModifiers',modifiers)]:
   if integer(row.get(field),0,2**32-1)!=integer(expected,0,2**32-1):raise Refused('explicit GDK keyboard domain mismatch')
 return selected

def stable_drafts(rows,baseline,expected):
 # Require actual post-interval inspections of every selected live role.
 for role,draft in expected.items():
  selected=[r for r in rows if r['sequence']>baseline and r['event']=='inspect' and r.get('role')==role]
  if not selected:raise Refused('draft evidence absent')
  row=selected[-1]
  if type(draft) is not str or row.get('draftUTF8')!=draft or integer(row.get('draftBytes'),0,1024)!=len(draft.encode('utf-8')):raise Refused('actual draft changed')
 return True
