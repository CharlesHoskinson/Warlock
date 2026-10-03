"""Exercise actual native endpoint admission and bracketing join; no native claim."""
import copy,hashlib,json,resource,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('projection-'+str(time.time_ns()));INPUT=OUT/'inputs';INPUT.mkdir(parents=True)
paths=[*sorted((ROOT/'adapter').glob('*.py')),Path(__file__)]
inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
for p in paths:
 dest=INPUT/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
sys.path.insert(0,str(INPUT/'adapter'))
from effect_endpoint import Endpoint,Refused
from taskbar_projection import coherent_scene
binding={'lifetime':'9007199254740993','session':'8','frontend':'1'}
row={'incarnation':'7','owner':None,'application':'owned.app','stackPosition':0,'workspace':'1','monitor':'0','geometry':[0,0,500,400],'fullscreenMode':0,
     **{key:True for key in ['workspaceVisible','acceptsInput','shouldRenderAny','shouldRenderOwnMonitor']},
     **{key:False for key in ['hidden','pinned','allowedOverFullscreen','renderOverFullscreen','minimized']}}
facts={'protocolVersion':3,'kind':'scene-facts','binding':binding,'requestId':'1','sequence':'1','revision':'4','outputGeneration':'3','facts':{'focused':'7','windows':[row]}}
snapshot={'windows':[{'incarnation':'7','application':'owned.app','label':'Owned','minimized':False}]}
client=Endpoint.__new__(Endpoint);client.bound=binding;client.pid=42;client.instance='private'
checks=[]
def admit(value):
 client.request=lambda request:value
 return client.scene_facts('1')
def check(name,test):
 assert test,name
 checks.append(name)
report={'passed':False,'inputs':inputs,'scope':'Actual endpoint decoder and join under controlled responses; real native campaign pending'}
try:
 check('valid native metadata',admit(facts)==facts)
 scene=coherent_scene(facts,snapshot,facts)
 check('native focus retained',scene['focused']=='7')
 check('owner and visibility retained',scene['windows'][0]['owner'] is None and scene['windows'][0]['available'])
 for key in ['revision','outputGeneration']:
  altered=copy.deepcopy(facts);altered[key]='5'
  check('reject raced '+key,coherent_scene(facts,snapshot,altered) is None)
 for key,value in [('application','different.app'),('minimized',True),('incarnation','8')]:
  altered=copy.deepcopy(snapshot);altered['windows'][0][key]=value
  check('reject snapshot/facts mismatch '+key,coherent_scene(facts,altered,facts) is None)
 for key,value in [('workspace','-1'),('workspace',None),('workspaceVisible',False),('hidden',True)]:
  altered=copy.deepcopy(facts);altered['facts']['windows'][0][key]=value
  check('unavailable '+str((key,value)),not coherent_scene(altered,snapshot,altered)['windows'][0]['available'])
 for key,value in [('workspace','01'),('workspace','-0'),('workspace',True),('workspace','9223372036854775808'),('monitor','01'),('geometry',[0,0,float('nan'),4]),('geometry',[0,0,float('inf'),4]),('application','bad\napp'),('application','a'*257),('owner','8')]:
  altered=copy.deepcopy(facts);altered['facts']['windows'][0][key]=value
  try:admit(altered)
  except Refused:checks.append('refuse malformed '+key+' '+repr(value))
  else:raise AssertionError('admitted malformed '+key)
 hello={'protocolVersion':3,'kind':'attached','binding':{**binding,'frontend':'2'},'compositor':{'pid':42,'instance':'private','coreHash':'frozen'},'capabilities':{'observe':True,'effects':True,'minimizedState':True,'effectProtocol':1,'operations':['minimize','restore','activate'],'canonicalScene':False,'taskbarProjectionProtocol':1}}
 for key,value in [('effectProtocol',True),('taskbarProjectionProtocol',True),('observe',1),('canonicalScene',0)]:
  altered=copy.deepcopy(hello);altered['capabilities'][key]=value;client.request=lambda request:altered
  try:client.hello()
  except Refused:checks.append('refuse capability bool/int alias '+key)
  else:raise AssertionError('admitted capability '+key)
 assert len(checks)==26
 assert all(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest for rel,digest in inputs.items())
 report.update(passed=True,checks=len(checks),cases=checks)
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])
