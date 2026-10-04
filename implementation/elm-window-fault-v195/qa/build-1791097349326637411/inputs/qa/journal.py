"""Real abrupt-writer death and filesystem/correlation adversarial recovery checks."""
import hashlib,json,os,resource,signal,subprocess,sys,tempfile,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from recovery_journal import Journal
from endpoint import Refused
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('journal-'+str(time.time_ns()));OUT.mkdir()
bound={'lifetime':'9007199254740993','session':'8','frontend':'1'}
intent={'request':'41','generation':'43','incarnation':'7','operation':'minimize','context':{'lifetime':bound['lifetime'],'epoch':'1','output':'3','revision':'4'}}
report={'passed':False,'checks':[],'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'adapter/recovery_journal.py',ROOT/'adapter/endpoint.py']}}
def check(name,value):report['checks'].append({'name':name,'passed':bool(value)});assert value,name
def refuse(fn):
 try:fn()
 except (OSError,ValueError,Refused):return True
 return False
try:
 with tempfile.TemporaryDirectory(prefix='elm-recovery-') as directory:
  runtime=Path(directory);runtime.chmod(0o700)
  with Journal(runtime) as journal:
   check('emptyJournalHasNoRecovery',journal.uncertain(bound) is None)
   check('concurrentWriterRefused',refuse(lambda:Journal(runtime)))
   journal.begin(bound,intent);check('pendingDurablyRoundTrips',journal.read()['status']=='Pending')
   check('freshBindingRecoversOnlyUncertainIntent',journal.uncertain(dict(bound,session='9'))['intent']==intent)
   check('foreignCompositorRefused',refuse(lambda:journal.uncertain(dict(bound,lifetime='9'))))
   bad={'binding':bound,'intent':dict(intent,request='42'),'status':'Committed'}
   check('mismatchedReceiptRefused',refuse(lambda:journal.settle(bad)))
   check('mismatchDoesNotClearPending',journal.read()['status']=='Pending')
   journal.settle({'binding':bound,'intent':intent,'status':'Committed'})
   check('durableCommitIsNotUnknown',journal.uncertain(bound) is None)
   check('duplicateTerminalReceiptRefused',refuse(lambda:journal.settle({'binding':bound,'intent':intent,'status':'Committed'})))
  code="import sys;sys.path.insert(0,sys.argv[1]);from recovery_journal import Journal;import json,time; j=Journal(sys.argv[2]);j.begin(json.loads(sys.argv[3]),json.loads(sys.argv[4]));print('durable',flush=True);time.sleep(30)"
  writer=subprocess.Popen(['/usr/bin/python3','-B','-c',code,str(ROOT/'adapter'),str(runtime),json.dumps(bound),json.dumps(intent)],stdout=subprocess.PIPE,text=True)
  try:
   import selectors
   with selectors.DefaultSelector() as selector:
    selector.register(writer.stdout,selectors.EVENT_READ);assert selector.select(3)
    check('writerConfirmsDurableSubmission',writer.stdout.readline().strip()=='durable')
   writer.kill();writer.wait(timeout=3);check('abruptWriterExitIsRecorded',writer.returncode==-signal.SIGKILL)
  finally:
   if writer.poll() is None:writer.kill();writer.wait(timeout=3)
  with Journal(runtime) as journal:
   check('freshWriterReadsUnknownAfterActualDeath',journal.uncertain(dict(bound,session='9'))['intent']==intent)
   target=runtime/'elm-window-recovery/intent.json';saved=target.read_bytes()
   target.write_text('{"schema":1,"schema":1}');check('duplicateJSONRefused',refuse(journal.read));target.write_bytes(saved)
   target.chmod(0o644);check('publicRecordRefused',refuse(journal.read));target.chmod(0o600)
   target.write_bytes(b'x'*4097);check('oversizeRecordRefused',refuse(journal.read));target.write_bytes(saved)
   target.unlink();target.symlink_to(runtime/'outside');check('symlinkRecordRefused',refuse(journal.read));target.unlink();target.write_bytes(saved);target.chmod(0o600)
   before=target.read_bytes();check('unsupportedOperationRefusedBeforeWrite',refuse(lambda:journal.begin(bound,dict(intent,operation='close'))));check('rejectedWritePreservesRecord',target.read_bytes()==before)
  (runtime/'elm-window-recovery').chmod(0o755);check('publicRecoveryDirectoryRefused',refuse(lambda:Journal(runtime)))
 report['passed']=True
except Exception as error:report.update(error=repr(error),traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
