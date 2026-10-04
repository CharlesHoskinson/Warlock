"""Strict Qt6 fixture journal decoder; raw QWindow and QWidget propagation differ."""
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
def parse(raw,*,pid,started,previous=None,profile="window-modal"):
 if type(raw) is not bytes or len(raw)>2*1024*1024:raise Refused('journal bytes')
 if type(started) is not str or not re.fullmatch(r'[1-9][0-9]{0,19}',started):raise Refused('process start identity')
 integer(pid,2,2**31-1);start=integer(int(started),1,2**63-1)
 complete=raw[:raw.rfind(b'\n')+1]
 try:
  rows=[json.loads(line,object_pairs_hook=pairs,parse_constant=constant) for line in complete.decode('utf-8',errors='strict').split('\n')[:-1]]
 except (UnicodeError,ValueError,RecursionError) as error:raise Refused('strict journal JSON/UTF8') from error
 if len(rows)>16384:raise Refused('journal row bound')
 if previous is not None and rows[:len(previous)]!=previous:raise Refused('changed observed prefix')
 last=0;monotonic=0;request=0
 for row in rows:
  if type(row) is not dict or row.get('schema')!=1 or type(row.get('schema')) is not int:raise Refused('journal schema')
  if integer(row.get('pid'),2,2**31-1)!=pid or integer(row.get('processStarted'),1,2**63-1)!=start:raise Refused('journal actor ownership')
  seq=integer(row.get('sequence'),1,2**63-1);clock=integer(row.get('monotonicUs'),1,2**63-1);req=integer(row.get('requestSequence'),0,2**63-1)
  if seq!=last+1 or clock<monotonic or req<request:raise Refused('journal ordering')
  last=seq;monotonic=clock;request=req
  if row.get('profile')!=profile or profile not in ('independent-groups','default-group'):raise Refused('exact toolkit group profile')
  for value in row.values():
   if type(value) not in (str,int,float,bool):raise Refused('flat primitive journal fields')
   if type(value) is float and not math.isfinite(value):raise Refused('nonfinite journal field')
   if type(value) is int and not -(2**63)<=value<=2**63-1:raise Refused('journal integer bound')
   if type(value) is str:
    try:encoded=value.encode('utf-8',errors='strict')
    except UnicodeError as error:raise Refused('invalid Unicode journal field') from error
    if len(encoded)>4096:raise Refused('journal text bound')
  if type(row.get('event')) is not str or not 1<=len(row['event'])<=64:raise Refused('event name')
  if row.get('event') in ('refusal','failed-exit'):raise Refused('actual fixture refusal')
  if 'role' in row:
   if row['role'] not in ('A','B','C','D','P'):raise Refused('role domain')
   integer(row.get('instance'),1,2**63-1);integer(row.get('mapGeneration'),0,2**63-1);integer(row.get('surfaceId'),0,2**32-1)
  for key in ['localX','localY','globalQtX','globalQtY','windowPositionX','windowPositionY','landmarkWindowX','landmarkWindowY']:
   if key in row:
    n=row[key]
    if type(n) not in (int,float) or abs(n)>2**23 or (type(n) is float and not math.isfinite(n)):raise Refused('finite coordinate')
 return rows

def interval(rows,baseline,kinds):
 integer(baseline,0,2**63-1)
 if baseline and not any(row['sequence']==baseline for row in rows):raise Refused('observed interval baseline')
 return [row for row in rows if row['sequence']>baseline and row['event'] in kinds]

def recipient(row,event,role,instance,map_generation,surface_id,event_types):
 if role not in ('A','B','C','D','P'):raise Refused('expected Qt role')
 for value,maximum in [(instance,2**63-1),(map_generation,2**63-1),(surface_id,2**32-1)]:integer(value,1,maximum)
 expected=event_types.get(event)
 integer(expected,0,2**31-1)
 if row['event']!=event or row.get('role')!=role or row.get('trackedRecipient') is not True:raise Refused('complete current raw QWindow recipient')
 for field,value in [('instance',instance),('mapGeneration',map_generation),('surfaceId',surface_id),('sourceSurfaceId',surface_id),('rawEventType',expected)]:
  if type(row.get(field)) is not int or row[field]!=value:raise Refused('exact Qt resource/event identity')
 integer(row.get('qtTimestamp'),0,2**63-1)

def coordinates(row,prefix,expected):
 if type(expected) not in (list,tuple) or len(expected)!=2:raise Refused('explicit measured coordinate pair')
 actual=[row.get(prefix+'X'),row.get(prefix+'Y')]
 for value in list(expected)+actual:
  if type(value) not in (int,float) or not math.isfinite(value) or abs(value)>2**23:raise Refused('finite bounded Qt coordinate')
 if actual!=list(expected):raise Refused('exact declared Qt coordinate')

def raw_pointer_interval(rows,baseline,*,role,instance,map_generation,surface_id,event_types,qt_button,modifiers,expected_local,expected_global):
 integer(qt_button,1,2**31-1);integer(modifiers,0,2**32-1)
 if qt_button&(qt_button-1):raise Refused('one explicit Qt button bit')
 selected=interval(rows,baseline,('window-button-press','window-button-release','window-button-double-click'))
 if len(selected)!=2:raise Refused('entire raw QWindow pointer interval exact pair')
 for row,event,buttons in zip(selected,('window-button-press','window-button-release'),(qt_button,0)):
  recipient(row,event,role,instance,map_generation,surface_id,event_types)
  for field,expected in [('qtButton',qt_button),('qtButtons',buttons),('qtModifiers',modifiers)]:
   if type(row.get(field)) is not int or row[field]!=expected:raise Refused('explicit Qt mouse domain/state')
  coordinates(row,'local',expected_local);coordinates(row,'globalQt',expected_global)
 return selected

def raw_key_interval(rows,baseline,*,role,instance,map_generation,surface_id,event_types,qt_key,native_scan,native_virtual,qt_modifiers,native_modifiers):
 for value in (qt_key,native_scan,native_virtual):integer(value,0,2**32-1)
 for states in (qt_modifiers,native_modifiers):
  if type(states) not in (list,tuple) or len(states)!=2:raise Refused('explicit press/release modifier states')
  for value in states:integer(value,0,2**32-1)
 selected=interval(rows,baseline,('window-key-press','window-key-release'))
 if len(selected)!=2:raise Refused('entire raw QWindow keyboard interval exact pair')
 for index,(row,event) in enumerate(zip(selected,('window-key-press','window-key-release'))):
  recipient(row,event,role,instance,map_generation,surface_id,event_types)
  if row.get('autoRepeat') is not False:raise Refused('nonrepeat Qt key interval')
  for field,expected in [('qtKey',qt_key),('nativeScanCode',native_scan),('nativeVirtualKey',native_virtual),('qtModifiers',qt_modifiers[index]),('nativeModifiers',native_modifiers[index])]:
   if type(row.get(field)) is not int or row[field]!=expected:raise Refused('explicit Qt key domain/state')
 return selected

def blocked_raw_pointer_interval(rows,baseline):
 if interval(rows,baseline,('window-button-press','window-button-release','window-button-double-click')):raise Refused('raw blocked native pointer leaked')
 return []

def widget_input_observations(rows,baseline):
 return interval(rows,baseline,('widget-button-press','widget-button-release','widget-button-double-click','widget-key-press','widget-key-release'))
