import hashlib,importlib.util,json,os,resource,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;OUT=ROOT/('profile-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
path=ROOT/'relay/qa/relay.py';spec=importlib.util.spec_from_file_location('current_relay',path);r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
report={'passed':False,'scope':'Actual profile parser/fixed child argv/current captured schema5 import; no native acceptance','inputs':{str(path):sha(path)},'checks':[]}
def check(name,v):report['checks'].append({'name':name,'passed':bool(v)});assert v,name
def private(p,value):p.write_text(json.dumps(value));p.chmod(0o600);return p
runtime=OUT/'runtime';runtime.mkdir(mode=0o700);control=OUT/'control';control.mkdir(mode=0o700);receipt=OUT/'receipt';receipt.mkdir(mode=0o700)
authority=private(OUT/'authority.json',{'runtime':str(runtime),'instance':'owned_instance','pid':os.getpid(),'expected_start':r.start(os.getpid()),'binary_sha256':'0'*64})
rc=private(OUT/'receipt.json',{'authorityConfig':str(authority),'controlDirectory':str(receipt),'incarnation':'16','effectOperation':'maximize','selectorOrdinal':1})
repo=next(p for p in ROOT.parents if (p/'AGENTS.md').is_file())
try:
 configs=[]
 for profile,field,target in [('broker','authorityConfig',authority),('receipt','receiptConfig',rc)]:
  cfg={'profile':profile,field:str(target),'controlDirectory':str(control),'runtime':str(runtime),'instance':'owned_instance'};configs.append(cfg)
  command=r.command_for(cfg,repo)
  expected=repo/'implementation/elm-shared-geometry-carrier-v422/qa/build-1791127807406303648/inputs/adapter/daemon.py' if profile=='broker' else ROOT/'receipt/qa/broker-entrypoint.py'
  check(profile+' exact fixed interpreter/source/private config',command==['/usr/bin/python3','-B',str(expected),str(target)])
 for name,change in [('wrong instance',{'instance':'forged'}),('nonstring runtime',{'runtime':True}),('missing instance',None),('extra command field',{'command':'untrusted'}),('closed profile',{'profile':'arbitrary'}),('wrong authority path',{'authorityConfig':'/not/a/file'})]:
  cfg=dict(configs[0])
  if change is None:cfg.pop('instance')
  else:cfg.update(change)
  try:r.command_for(cfg,repo);refused=False
  except (r.RelayFailure,KeyError,TypeError,OSError,ValueError):refused=True
  check(name+' refused',refused)
 sys.path.insert(0,str(ROOT/'receipt/qa'));import wrapper
 backend=wrapper.load_backend();check('verified current schema5 daemon imports',callable(backend.main) and hasattr(backend,'OutputWriter'))
 for rel in ['receipt/qa/wrapper.py','receipt/qa/broker-entrypoint.py','receipt/qa/held-source-manifest.json']:report['inputs'][str(ROOT/rel)]=sha(ROOT/rel)
 report['passed']=True
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
