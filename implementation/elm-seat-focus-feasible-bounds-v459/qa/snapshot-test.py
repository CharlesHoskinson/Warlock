"""Execute actual nested snapshot helper with frozen196 native records; no GUI."""
import ast,copy,hashlib,importlib.util,json,resource,time,types
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
s=Path(__file__).resolve().parents[1];r=s.parents[1];source=s/'qa/native.py';original=r/'implementation/elm-geometry-xdg-origin-native-v196/qa/native-1791130292488706555';packet=json.loads((original/'report.json').read_text());selected=[p for p in packet['profiles'] if p['name']=='zero-scale1'][-1];log=original/'native-evidence/zero-scale1.jsonl'
spec=importlib.util.spec_from_file_location('actual194',r/'implementation/elm-geometry-client-journal-v194/journal.py');journal=importlib.util.module_from_spec(spec);spec.loader.exec_module(journal)
function=next(n for n in ast.walk(ast.parse(source.read_text())) if isinstance(n,ast.FunctionDef) and n.name=='snapshot')
raw=selected['native'];facts=selected['facts'];checks=[]
def check(name,value,**data):
 checks.append({'name':name,'passed':bool(value)});assert value,name
class Endpoint:
 def geometry_facts(self,request):return copy.deepcopy(facts)
 def snapshot(self,request):return {'windows':[{'incarnation':facts['facts']['windows'][0]['incarnation'],'label':raw['title']}]}
namespace={'wait':lambda predicate,deadline:predicate(),'rows':lambda:journal.parse(log.read_bytes(),raw['pid'],[0,0,0,0,1])['events'],'log':log,'send':lambda command,deadline:None,'journal':journal,'bounded_log':lambda:log.read_bytes(),'client':types.SimpleNamespace(pid=raw['pid']),'profile':[0,0,0,0,1],'name':'zero-scale1','check':check,'selected_colors':{},'endpoint':Endpoint(),'rid':lambda:'1','native':lambda:copy.deepcopy(raw),'time':time,'report':{},'physical':(800,600),'monitor_scale':1,'maximum':[0,0],'requested':{'expectedLogicalWorkarea':[0,0,800,600]},'session':types.SimpleNamespace(data=lambda key:[{'id':int(facts['facts']['windows'][0]['monitor']),'width':800,'height':600,'scale':1}])}
exec(compile(ast.Module(body=[function],type_ignores=[]),str(source),'exec'),namespace)
result=namespace['snapshot'](time.monotonic()+6);assert result[0]['incarnation']==facts['facts']['windows'][0]['incarnation'] and all(c['passed'] for c in checks)
for field,bad in [('width',799),('height',599),('scale',2)]:
 namespace['session']=types.SimpleNamespace(data=lambda key,field=field,bad=bad:[{'id':int(facts['facts']['windows'][0]['monitor']),'width':bad if field=='width' else 800,'height':bad if field=='height' else 600,'scale':bad if field=='scale' else 1}])
 try:namespace['snapshot'](time.monotonic()+6)
 except AssertionError as error:assert 'actualOutputScaleAndWorkareaBeforeIntent' in str(error)
 else:raise AssertionError('Actual output mismatch accepted:'+field)
class Clock:
 current=0
 def monotonic(self):return self.current
clock=Clock();namespace['time']=clock
def delayed_monitors(key):
 clock.current=7
 return [{'id':int(facts['facts']['windows'][0]['monitor']),'width':800,'height':600,'scale':1}]
namespace['session']=types.SimpleNamespace(data=delayed_monitors)
try:namespace['snapshot'](6)
except AssertionError as error:assert 'deadline after final monitor read' in str(error)
else:raise AssertionError('Accepted delayed final monitor read')
out=s/'qa'/('snapshot-test-'+str(time.time_ns()));out.mkdir();report={'passed':True,'checks':5,'scope':'Actual204 snapshot helper executed with frozen196 native journal/facts plus synthetic observation carrier; output dimension/scale mismatches rejected. No GUI or new native qualification','inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),source,original/'report.json',log,r/'implementation/elm-geometry-client-journal-v194/journal.py']}}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'report':str(out/'report.json')}))
