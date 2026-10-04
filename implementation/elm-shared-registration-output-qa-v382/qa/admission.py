"""Actual C host admission, correlated broker settlement and hostile paths."""
import hashlib,json,os,resource,shlex,subprocess,sys,tempfile,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from recovery_journal import Journal
from endpoint import Refused
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('admission-'+str(time.time_ns()));OUT.mkdir()
bound={'lifetime':'9007199254740993','session':'8','frontend':'1'}
intent={'request':'41','generation':'43','incarnation':'7','operation':'minimize','context':{'lifetime':bound['lifetime'],'epoch':'1','output':'3','revision':'4'}}
request={'protocolVersion':3,'kind':'window-effect','effectProtocol':1,'binding':bound,'intent':intent}
report={'passed':False,'checks':[],'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'native/admission-test.c',ROOT/'native/host-journal.h',ROOT/'native/surface.h',ROOT/'adapter/recovery_journal.py',ROOT/'adapter/endpoint.py']}}
def check(name,value):report['checks'].append({'name':name,'passed':bool(value)});assert value,name
def refused(fn):
 try:fn()
 except (OSError,ValueError,Refused):return True
 return False
try:
 flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','json-glib-1.0'],text=True))
 result=subprocess.run(['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wno-unused-function',str(ROOT/'native/admission-test.c'),'-o',str(OUT/'admission'),*flags],capture_output=True,text=True,timeout=90)
 (OUT/'compile.stdout').write_text(result.stdout);(OUT/'compile.stderr').write_text(result.stderr);assert result.returncode==0,result.stderr
 report['binarySHA256']=hashlib.sha256((OUT/'admission').read_bytes()).hexdigest()
 with tempfile.TemporaryDirectory(prefix='elm-host-admission-') as directory:
  runtime=Path(directory);runtime.chmod(0o700);config=runtime/'authority.json';config.write_text(json.dumps({'runtime':str(runtime),'instance':'qa_fixture_1'}));config.chmod(0o600)
  def admit(rows,expected=bound,path=config):
   result=subprocess.run([str(OUT/'admission'),str(path),json.dumps(rows),json.dumps(expected)],capture_output=True,text=True,timeout=3)
   report.setdefault('runs',[]).append({'exitCode':result.returncode,'stdout':result.stdout,'stderr':result.stderr});return result.returncode
  check('actualCAdmissionWritesBeforeBrokerExists',admit([request])==0)
  target=Journal.namespace_path(runtime,'qa_fixture_1',bound['lifetime'])/'host-intent.json';record=json.loads(target.read_text());check('hostRecordHasExactIntentAndPendingState',record=={'schema':1,'binding':bound,'intent':intent,'status':'Pending'})
  with Journal(runtime,'qa_fixture_1',bound['lifetime']) as journal:
   check('unreadBrokerRecoversHostUncertainty',journal.read() is None and journal.uncertain(dict(bound,session='9'))['intent']==intent)
   old=dict(intent,request='40',generation='42');journal.begin(bound,old);journal.settle({'binding':bound,'intent':old,'status':'Committed'})
   check('olderBrokerCommitDoesNotResolveNewAdmission',journal.uncertain(bound)['intent']==intent)
   journal.begin(bound,intent);journal.settle({'binding':bound,'intent':intent,'status':'Committed'});check('exactDurableCommitResolvesHostAdmission',journal.uncertain(bound) is None)
   newer=dict(intent,request='42',generation='44');check('newHostActionCanBeAdmittedWhileBrokerLockHeld',admit([dict(request,intent=newer)])==0)
   check('priorSettlementCannotResolveLaterHostIntent',journal.uncertain(bound)['intent']==newer)
   journal.begin(bound,newer);journal.settle({'binding':bound,'intent':newer,'status':'Refused'});check('correlatedDurableRefusalIsKnown',journal.uncertain(bound) is None)
   saved=target.read_bytes();check('missingBackendBindingRefused',admit([request],None)==1);check('retiredBackendBindingRefused',admit([request],dict(bound,frontend='2'))==1)
   check('twoEffectBatchRefusedBeforePersistence',admit([request,request])==1);check('refusedBatchesPreserveLastAdmission',target.read_bytes()==saved)
   check('unsupportedOperationRefused',admit([dict(request,intent=dict(intent,operation='close'))])==1)
   check('mismatchedNativeEpochRefused',admit([dict(request,intent=dict(intent,context=dict(intent['context'],epoch='2')))])==1)
   check('zeroRequestRefused',admit([dict(request,intent=dict(intent,request='0'))])==1)
   check('protocolBooleanRefused',admit([dict(request,effectProtocol=True)])==1)
   target.chmod(0o644);check('publicAdmissionTargetRefused',admit([request])==1);target.chmod(0o600)
   target.unlink();outside=runtime/'outside';outside.write_text('untouched');target.symlink_to(outside);check('symlinkAdmissionTargetRefused',admit([request])==1 and outside.read_text()=='untouched');target.unlink();target.write_bytes(saved);target.chmod(0o600)
   lock=os.open(Journal.namespace_path(runtime,'qa_fixture_1',bound['lifetime'])/'host-writer.lock',os.O_RDWR)
   import fcntl
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);check('competingHostWriterRefused',admit([request])==1);os.close(lock)
   target.write_text(json.dumps(dict(record,status='Committed')));check('forgedHostSettlementRefused',refused(lambda:journal.uncertain(bound)));target.write_bytes(saved)
  config.chmod(0o644);check('publicAuthorityConfigRefused',admit([request])==2);config.chmod(0o600)
  alias=runtime/'alias';alias.symlink_to(runtime,target_is_directory=True);check('symlinkConfigAncestryRefused',admit([request],path=alias/'authority.json')==2)
 report['passed']=True
except Exception as error:report.update(error=repr(error),traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
