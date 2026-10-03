"""Typed real-provider observations; this decoder cannot create a witness."""
import copy,json,re
NAMES=('menu','row','popup','attached','content','window','nativeRoot')
ENGINE=('engineGeneration','engineEpoch','providerGeneration')
def exact(a,b):return json.dumps(a,sort_keys=True,allow_nan=False,separators=(',',':'))==json.dumps(b,sort_keys=True,allow_nan=False,separators=(',',':'))
def integer(v,low=1,high=2**53-1):
 if type(v)is not int or not low<=v<=high:raise ValueError('Exact bounded provider integer required')
 return v
def process(value):
 integer(value.get('processId'),high=2147483647)
 if type(value.get('processStart'))is not str or not re.fullmatch(r'[1-9][0-9]*',value['processStart']):raise ValueError('Exact provider process start required')
 if type(value.get('configSHA256'))is not str or not re.fullmatch(r'[0-9a-f]{64}',value['configSHA256']):raise ValueError('Exact provider config hash required')
 for k in ENGINE:integer(value.get(k))
 return dict(pid=value['processId'],start=value['processStart'],configSHA256=value['configSHA256'],**{k:value[k]for k in ENGINE})
def metadata(value):
 if type(value)is not dict or set(value)!={'schema','kind','processId','processStart','configSHA256',*ENGINE} or value.get('schema')!='qml-engine-metadata-v1' or value.get('kind')!='metadata-only; no widget/input authority':raise ValueError('Actual complete engine metadata required')
 return process(value)
def engine_pair(menu):
 if type(menu)is not dict:raise ValueError('Actual QML diagnostic object required')
 a=metadata(menu.get('engineBefore'));b=metadata(menu.get('engineAfter'))
 if not exact(a,b):raise ValueError('Actual metadata changed across QML diagnostic')
 return a
def popup(value):
 fields={'schema','relationship','processId','processStart','configSHA256',*ENGINE,'allocations','contexts','nativeWindowBound','diagnostics'}
 if type(value)is not dict or set(value)!=fields or value.get('schema')!='qml-popup-lifetime-v1' or value.get('relationship')!='lexical-pin-popup-existing-attached-native-content' or value.get('nativeWindowBound')is not True:raise ValueError('Actual complete non-null native popup witness required')
 process(value)
 objects=value['allocations'];contexts=value['contexts']
 if type(objects)is not dict or set(objects)!=set(NAMES) or type(contexts)is not dict or set(contexts)!=set(NAMES) or type(value['diagnostics'])is not dict:raise ValueError('Whole seven-allocation/context tuple required')
 for name in NAMES:
  integer(objects[name]);c=contexts[name]
  if type(c)is not dict or set(c)!={'generation','present','enginePresent'} or type(c['present'])is not bool or type(c['enginePresent'])is not bool:raise ValueError('Exact context presence/engine representation required')
  integer(c['generation'],low=0)
  if c['present']is not(c['generation']>0) or c['enginePresent']is not c['present'] or (name in NAMES[:3] and not c['present']):raise ValueError('Actual lexical/native context relation differs')
 if len({objects[n]for n in NAMES[:3]})!=3 or any(objects['window']==objects[n]for n in NAMES if n!='window') or objects['content']==objects['row']:raise ValueError('Actual lexical/window allocation type relationship differs')
 # content and nativeRoot may be the same actual QQuickItem. Preserve both slots.
 return copy.deepcopy(value)
def popup_pair(menu,scope):
 if not exact(engine_pair(menu),scope):raise ValueError('Current external/QML engine metadata differs')
 a=popup(menu.get('popupBefore'));b=popup(menu.get('popupAfter'))
 if not exact(a,b) or not exact(process(a),scope):raise ValueError('Actual popup tuple changed across geometry/current engine')
 return a
