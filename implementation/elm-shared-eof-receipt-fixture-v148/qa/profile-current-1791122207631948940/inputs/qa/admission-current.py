"""Actual current C schema5 admission + store; historical real receipt replay.

No fabricated native receipt, native operation, observer request or compositor
launch. Recorded V100 receipt is historical provenance, not current acceptance.
"""
import copy,hashlib,json,os,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
OUT=ROOT/'qa'/('admission-current-'+str(time.time_ns()));OUT.mkdir()
sys.path.insert(0,str(ROOT/'qa'))
import backend,wrapper
current=backend.load_backend()
from recovery_store import RecoveryStore
from endpoint import Refused
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[];report={'passed':False,'scope':'Actual current144 C/schema5 broker admission with no native dispatch, and exact historical V100 Committed receipt replay only','nativeAcceptance':False,'full09Accepted':False,'checks':checks}
def check(n,v):checks.append({'name':n,'passed':bool(v)});assert v,n
def refuses(fn):
 try:fn();return False
 except (Refused,wrapper.HoldFailure):return True
try:
 pin=json.loads((ROOT/'backend-pin.json').read_text());build=Path(pin['buildReport']).parent
 for p in [*sorted((ROOT/'qa').glob('*.py')),ROOT/'backend-pin.json',ROOT/'fixture-source-pin.json']:
  target=OUT/'inputs'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 native=OUT/'inputs/native';native.mkdir()
 for name in ['admission-test.c','surface.h','host-journal.h']:shutil.copy2(build/'inputs/native'/name,native/name)
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','json-glib-1.0'],text=True))
 command=['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-unused-function','-MD','-MF',str(OUT/'admission.d'),str(native/'admission-test.c'),'-o',str(OUT/'admission'),*flags]
 result=subprocess.run(command,capture_output=True,text=True,timeout=60);(OUT/'compile.stdout').write_text(result.stdout);(OUT/'compile.stderr').write_text(result.stderr)
 report['compileCommand']=command;check('exact current C durable schema5 admission compiles',result.returncode==0)
 history=REPO/'implementation/elm-geometry-family-menu-receipt-cleanup-native-v100/qa/native-1791110259133139744'
 evidence=history/'native-evidence/receipt-actor-2/held.json';original=json.loads((history/'report.json').read_text())
 check('historical real native receipt hash matches failed campaign frozen artifacts',sha(evidence)==original['artifacts'][str(evidence.relative_to(history))])
 shutil.copy2(evidence,OUT/'historical-v100-held.json');record=json.loads(evidence.read_text());receipt=record['receipt']
 check('historical original actual status is Committed',receipt['status']=='Committed' and receipt['intent']==record['intent'] and receipt['binding']==record['binding'])
 bound=receipt['binding'];intent=receipt['intent']
 runtime=OUT/'runtime';runtime.mkdir(mode=0o700);config=OUT/'authority.json';config.write_text(json.dumps({'runtime':str(runtime),'instance':'qa_current_148'}));config.chmod(0o600)
 request={'protocolVersion':3,'kind':'window-effect','effectProtocol':2,'binding':bound,'intent':intent}
 with RecoveryStore(runtime,'qa_current_148',bound['lifetime']) as store:
  check('without actual host admission broker cannot authorize effect',refuses(lambda:store.begin(bound,intent,2)))
  result=subprocess.run([str(OUT/'admission'),str(config),json.dumps([request]),json.dumps(bound)],capture_output=True,text=True,timeout=3)
  report['admission']={'exitCode':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
  check('actual current C admission stores original full protocol2 key',result.returncode==0)
  check('actual store admits that exact key once',store.begin(bound,intent,2) is True)
  check('duplicate key does not authorize native resubmission',store.begin(bound,intent,2) is False)
  check('foreign frontend cannot consume original host admission',refuses(lambda:store.begin(dict(bound,frontend=str(int(bound['frontend'])+1)),intent,2)))
 # No native effect/settlement call occurs. Current store must remain uncertain.
 fresh=dict(bound,session=str(int(bound['session'])+1),frontend=str(int(bound['frontend'])+1))
 with RecoveryStore(runtime,'qa_current_148',bound['lifetime']) as store:
  frames=store.recovery_frames(fresh)
  uncertain=next(f for f in frames if f['kind']=='host-uncertain')
  check('renewed current binding preserves original full unknown intent',uncertain['binding']==fresh and uncertain['intent']==intent and uncertain['effectProtocol']==2)
  check('native execution is never inferred from historical receipt fixture',store.read()['status']=='Pending' and store.read()['binding']==bound)
  check('old compositor lifetime is rejected',refuses(lambda:store.recovery_frames(dict(fresh,lifetime='2'))))
 control=OUT/'receipt-control';control.mkdir(mode=0o700);(control/'gate.json').write_text('{"action":"hold"}');(control/'gate.json').chmod(0o600)
 sent=[];holder=wrapper.ReceiptHold(control,intent['incarnation'],sent.append,operation=intent['operation'])
 check('original five-second holder deadline retained',holder.timeout==5)
 holder.intercept(copy.deepcopy(receipt))
 check('exact recorded native receipt held without forwarding',holder.seen and not holder.released and sent==[] and holder.receipt==receipt)
 holder.intercept({'protocolVersion':3,'kind':'host-refresh'})
 check('actual notification frame passes during recorded hold',sent==[{'protocolVersion':3,'kind':'host-refresh'}])
 wrong={'action':'release','wrapper':{'pid':holder.pid,'start':holder.start},'effectProtocol':2,'binding':fresh,'intent':intent}
 check('wrong renewed binding cannot release original receipt',refuses(lambda:holder.release(wrong)) and not holder.released)
 wrapper.write_release(control);holder.poll_gate()
 check('private gate releases exact original recorded receipt once',holder.released and sent[-1]==receipt)
 check('duplicate selected recorded receipt is rejected',refuses(lambda:holder.intercept(receipt)))
 holder.close()
 # Valid current native transport still owns kernel credentials/identity checks.
 import inspect
 check('current broker uses actual inherited kernel SO_PEERCRED transport', 'SO_PEERCRED' in inspect.getsource(current.Endpoint.request) and 'verify_process' in inspect.getsource(current.Endpoint.request))
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and not p.is_symlink()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'checks':len(checks),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
