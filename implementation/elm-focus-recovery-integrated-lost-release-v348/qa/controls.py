import ast,hashlib,json,os,pathlib,resource,shlex,subprocess,sys,time
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'fixture-adapter'));sys.path.insert(0,str(ROOT/'qa'))
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
from fault_backend import OneShotReleaseFault
from delivery_ledger import DeliveryLedger
from retirement_ledger import ObservationJoin
from grant_endpoint import RetirementProof,NativeBinding
from durable_ledger import encoded
OUT=ROOT/'qa'/('controls-'+str(time.time_ns()));OUT.mkdir();checks=[]
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
def denied(name,fn):
 try:fn()
 except (ValueError,OSError):check(name,True)
 else:check(name,False)
class OutputFailure(Exception):pass
try:
 for file in (ROOT/'qa').glob('*.py'):ast.parse(file.read_text())
 baseline=ast.parse((ROOT.parents[1]/'implementation/elm-reconciliation-native-journey-v627/qa/regression.py').read_text());runner=ast.parse((ROOT/'qa/runner.py').read_text())
 for name in ['wait','click']:
  old=next(n for n in ast.walk(baseline) if isinstance(n,ast.FunctionDef) and n.name==name);new=next(n for n in ast.walk(runner) if isinstance(n,ast.FunctionDef) and n.name==name)
  check('original627 '+name+' AST and deadlines retained',ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False))
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','json-glib-1.0'],text=True));p=subprocess.run(['cc','-std=gnu11','-O2',str(ROOT/'fixture-native/admission-test.c'),'-o',str(OUT/'admission-test'),*flags],capture_output=True,text=True)
 (OUT/'compile.stderr').write_text(p.stderr);check('unchanged actual624 C producer compiles',p.returncode==0)
 runtime=OUT/'runtime';runtime.mkdir(mode=0o700);config=runtime/'config.json';config.write_bytes(encoded({'runtime':str(runtime),'instance':'Test'}));config.chmod(0o600)
 old={'lifetime':'19','session':'1','frontend':'1'};current={'lifetime':'19','session':'2','frontend':'1'}
 record={'schema':2,'effectProtocol':1,'binding':old,'intent':{'request':'12','generation':'12','incarnation':'2','operation':'minimize','context':{'lifetime':'19','epoch':'1','output':'7','revision':'21'}},'status':'Unknown'}
 request={'protocolVersion':3,'kind':'window-effect','effectProtocol':1,'binding':old,'intent':record['intent']};p=subprocess.run([str(OUT/'admission-test'),str(config),json.dumps([request]),json.dumps(old)],capture_output=True,text=True);check('actual C durable Pending admission',p.returncode==0)
 ledger=DeliveryLedger(str(runtime),'Test','19');proof=RetirementProof(NativeBinding.parse(current),NativeBinding.parse(old),'3','19','retire','Retired');join=ObservationJoin(record,proof)
 for domain,request_id,revision in [('action','91','22'),('geometry','37','29')]:join.expect(domain,request_id);join.accept(domain,request_id,current,{'lifetime':'19','epoch':'1','output':'7','revision':revision})
 original=ledger.release(join);cert=ledger.attest(join);frame={'protocolVersion':3,'kind':'host-reservation-released','binding':current,'record':record,'release':{k:cert[k] for k in ['id','proof','observation']}}
 daemon=OUT/'synthetic-daemon.py';daemon.write_text('# CPU fixture target only; never imported as native daemon\n');forwarded=[]
 def fault_config(name):
  marker=OUT/name;marker.mkdir(mode=0o700)
  return {'schema':1,'campaignId':'a'*32,'daemonPath':str(daemon),'daemonSHA256':hashlib.sha256(daemon.read_bytes()).hexdigest(),'markerDirectory':str(marker),'runtime':str(runtime),'instance':'Test'}
 c=fault_config('single');fault=OneShotReleaseFault(c);fault.intercept({'kind':'geometry-facts'},forwarded.append,OutputFailure)
 check('observation frames pass through unchanged',forwarded==[{'kind':'geometry-facts'}])
 before=(ledger.path/'ledger-v6.json').read_bytes();before_sidecar=(ledger.path/'release-deliveries-v1.json').read_bytes()
 try:fault.intercept(frame,forwarded.append,OutputFailure)
 except OutputFailure:check('first real-shaped release suppressed after durable certificate',len(forwarded)==1)
 else:check('first real-shaped release suppressed after durable certificate',False)
 marker=pathlib.Path(c['markerDirectory'])/'lost-release.json';m=json.loads(marker.read_text());check('single-use marker private singlelink and exact anchor',marker.stat().st_mode&0o777==0o600 and marker.stat().st_nlink==1 and m['certificate']==cert and m['originalRelease']==original)
 marker_before=marker.read_bytes();restarted=OneShotReleaseFault(c);restarted.intercept(frame,forwarded.append,OutputFailure)
 check('fresh wrapper startup never rearms consumed marker',forwarded[-1]==frame and marker.read_bytes()==marker_before)
 check('wrapper does not alter original archive or sidecar',(ledger.path/'ledger-v6.json').read_bytes()==before and (ledger.path/'release-deliveries-v1.json').read_bytes()==before_sidecar)
 for case in ['absent-certificate','wrong-current','wrong-anchor','symlink-marker','public-marker','wrong-campaign','marker-write-zero','marker-fsync']:
  c=fault_config(case);f=OneShotReleaseFault(c);mutant=json.loads(json.dumps(frame));sent=[]
  if case=='absent-certificate':mutant['release']['id']='0'*64
  if case=='wrong-current':mutant['binding']['frontend']='2'
  if case=='wrong-anchor':mutant['record']['intent']['request']='13'
  if case in ['symlink-marker','public-marker','wrong-campaign']:
   p=pathlib.Path(c['markerDirectory'])/'lost-release.json'
   if case=='symlink-marker':p.symlink_to(marker)
   else:
    value=json.loads(marker_before);value['campaignId']=c['campaignId'] if case=='public-marker' else 'b'*32;p.write_bytes(encoded(value));p.chmod(0o644 if case=='public-marker' else 0o600)
  saved_write=os.write;saved_fsync=os.fsync
  def write(fd,data):return 0 if case=='marker-write-zero' else saved_write(fd,data)
  def fsync(fd):
   if case=='marker-fsync':raise OSError('marker fsync EIO')
   return saved_fsync(fd)
  with patch.multiple(os,write=write,fsync=fsync):denied('fault control rejects '+case,lambda:f.intercept(mutant,sent.append,OutputFailure))
  check('fault refusal never forwards or rearms '+case,not sent and f.poisoned)
 ledger.close()
 report={'passed':True,'assertions':len(checks),'checks':checks,'nativeAcceptance':False,'nativeLaunched':False,'targetGUIReviewed':False,'claim':'Actual copied624 C/filesystem archive+certificate, synthetic typedproof/read fixture for QA wrapper; runner AST/sixseconddeadline controls only','sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'qa').glob('*.py')}}
except BaseException as error:report={'passed':False,'checks':checks,'error':repr(error)};raise
finally:(OUT/'report.json').write_text(json.dumps(report,indent=2));print(OUT/'report.json',flush=True)
