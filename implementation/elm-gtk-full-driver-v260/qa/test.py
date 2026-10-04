"""Actual refactored full-key controls and preserved original source; no GUI."""
import ast,copy,hashlib,importlib.util,json,pathlib,resource,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
spec=importlib.util.spec_from_file_location('owned_shell',ROOT/'qa/shell.py');shell=importlib.util.module_from_spec(spec);spec.loader.exec_module(shell)
out=ROOT/'qa'/('source-test-'+str(time.time_ns()));out.mkdir()
report={'passed':False,'nativeAcceptance':False,'fullCampaignPassed':False,'checks':[]}
req={'protocolVersion':3,'kind':'window-effect','effectProtocol':1,'binding':{'lifetime':'1','session':'2','frontend':'3'},'intent':{'request':'4','generation':'5','incarnation':'6','operation':'minimize','context':{'lifetime':'1','epoch':'7','output':'8','revision':'9'}}}
receipt=dict(copy.deepcopy(req),kind='effect-outcome',status='Committed',reason='',revision='10',outputGeneration='8')
def check(name,fn,reject=False):
 try:fn();assert not reject,name
 except shell.Refused:assert reject,name
 report['checks'].append({'name':name,'passed':True})
try:
 check('original-full-key',lambda:shell.full_key(req,receipt))
 for path,value in [(('binding','lifetime'),'10'),(('binding','session'),'10'),(('binding','frontend'),'10'),(('intent','request'),'10'),(('intent','generation'),'10'),(('intent','incarnation'),'10'),(('intent','context','revision'),'10'),(('effectProtocol',),True),(('effectProtocol',),2),(('status',),'Unknown'),(('status',),'Refused'),(('protocolVersion',),True),(('kind',),'other')]:
  altered=copy.deepcopy(receipt);cursor=altered
  for component in path[:-1]:cursor=cursor[component]
  cursor[path[-1]]=value;check('reject-'+'.'.join(path)+'-'+str(value),lambda a=altered:shell.full_key(req,a),True)
 for value in [True,1,1.0,'0','01','-1','1e0',str(2**64)]:
  altered=copy.deepcopy(req);altered['intent']['request']=value;bad=copy.deepcopy(receipt);bad['intent']['request']=value;check('canonical-request-'+str(value),lambda a=altered,b=bad:shell.full_key(a,b),True)
 geometry=copy.deepcopy(req);geometry['effectProtocol']=2;geometry['intent']['operation']='maximize';geometry_out=dict(copy.deepcopy(geometry),kind='effect-outcome',status='Committed');check('geometry-exact-full-key',lambda:shell.full_key(geometry,geometry_out))
 tree=ast.parse((ROOT/'qa/driver.py').read_text());driver=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Driver');names={n.name for n in driver.body if isinstance(n,ast.FunctionDef)};assert {'GTK%02d'%i for i in range(1,9)}<=names
 origin=json.loads((ROOT/'origin.json').read_text())
 for section in ['original525','fault432']:
  for name,digest in origin[section].items():assert hashlib.sha256((ROOT/'qa/original'/name).read_bytes()).hexdigest()==digest
 for name in ['driver.py','shell.py']:ast.parse((ROOT/'qa'/name).read_text())
 report.update(passed=True,inputs={str(ROOT/'qa'/name):hashlib.sha256((ROOT/'qa'/name).read_bytes()).hexdigest() for name in ['driver.py','shell.py','test.py']},allEightPhasesMaterialized=True,sourceMutable=True)
except BaseException as error:report['error']=repr(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed'],'checks':len(report['checks']),'error':report.get('error')}));raise SystemExit(0 if report['passed'] else 1)
