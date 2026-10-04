"""Actual filesystem refusal classification; ENOSPC/EDQUOT use explicit fault injection."""
import errno,hashlib,json,os,resource,sys,tempfile,time,traceback
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from recovery_journal import Journal,RecoveryFailure,guarded
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('storage-'+str(time.time_ns()));OUT.mkdir()
report={'passed':False,'checks':[],'inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'adapter/recovery_journal.py',ROOT/'adapter/daemon.py']},'scope':'CPU actual filesystem refusals plus explicitly injected errno failures; native GUI proof separate'}
def check(name,value):report['checks'].append({'name':name,'passed':bool(value)});assert value,name
def reason(fn):
 try:fn()
 except RecoveryFailure as error:return error.reason
 raise AssertionError('Expected classified failure')
bound={'lifetime':'71','session':'2','frontend':'3'};intent={'request':'1','generation':'1','incarnation':'4','operation':'minimize','context':{'lifetime':'71','epoch':'3','output':'5','revision':'6'}}
try:
 with tempfile.TemporaryDirectory(prefix='elm-storage-') as temp:
  runtime=Path(temp);runtime.chmod(0o700)
  with Journal(runtime,'alpha','71') as journal:
   journal.begin(bound,intent);path=journal.path/'intent.json';saved=path.read_bytes()
   check('actualHeldWriterClassifiedBusy',reason(lambda:guarded(lambda:Journal(runtime,'alpha','71')))=='busy')
   path.write_text('{');check('actualMalformedRecordClassifiedUnverified',reason(lambda:guarded(journal.read))=='unverified');path.write_bytes(saved)
   path.chmod(0o644);check('actualPublicRecordClassifiedUnverified',reason(lambda:guarded(journal.read))=='unverified');path.chmod(0o600)
   for code in [errno.ENOSPC,errno.EDQUOT,errno.EROFS,errno.EACCES,errno.EIO]:
    with patch('recovery_journal.os.fsync',side_effect=OSError(code,'injected filesystem failure')):
     check('injectedDurabilityErrnoClassified:'+str(code),reason(lambda:guarded(lambda:journal.begin(bound,dict(intent,request='2'))))==('full' if code in [errno.ENOSPC,errno.EDQUOT] else 'unavailable'))
    check('injectedFailedWritePreservesOldIntent:'+str(code),path.read_bytes()==saved)
    check('injectedFailedWriteLeavesNoTemporaryFiles:'+str(code),not list(journal.path.glob('pending-*')))
   journal.settle({'binding':bound,'intent':intent,'status':'Committed'});check('correctionAllowsExplicitSettlement',journal.uncertain(bound) is None)
  base=runtime/'elm-window-recovery';legacy=base/'host-intent.json';legacy.write_text(json.dumps({'schema':1,'binding':bound,'intent':intent,'status':'Pending'}));legacy.chmod(0o600)
  check('actualAmbiguousLegacyClassifiedOwnerFailure',reason(lambda:guarded(lambda:Journal(runtime,'beta','71')))=='legacy-owner')
  check('legacyFailureDoesNotEraseEvidence',json.loads(legacy.read_text())['intent']==intent)
 report['passed']=True
except Exception as error:report.update(error=repr(error),traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
