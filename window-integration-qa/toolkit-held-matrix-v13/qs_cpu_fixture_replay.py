from pathlib import Path
import hashlib,json,tempfile,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
import test_qs_lifecycle as test
import helper_observer as observer
B=Path(__file__).resolve().parent;scope=require_qa_scope();rows=[];case=test.QS()
for index in range(30):
 with tempfile.TemporaryDirectory() as folder:
  p,authority=case.owned(folder)
  try:
   try:authority.guard();error=None
   except Exception as issue:error=repr(issue)
   path=Path('/proc',str(p.pid));rows.append(dict(index=index,error=error,actualArgv=observer.cmdline(p.pid),expectedArgv=authority.command,actualExecutable=str((path/'exe').resolve()),expectedExecutable=str(authority.executable),actualExecutableSHA256=observer.digest((path/'exe').resolve()),expectedExecutableSHA256=authority.executable_sha,actualIdentity=observer.process(p.pid),expectedIdentity=authority.identity,originalPoll=p.poll()))
  finally:case.dispose(p)
report=dict(result='bounded-replay',scope=scope,cases=rows,sourceSHA256=hashlib.sha256((B/'test_qs_lifecycle.py').read_bytes()).hexdigest(),nativeLaunch=False,installedQSExecuted=False,fullOfflineFailureRetained=True)
p=B/'qs-cpu-fixture-readiness-replay.json'
with p.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
p.chmod(0o600);print(json.dumps(dict(cases=len(rows),failures=sum(row['error'] is not None for row in rows),nativeLaunch=False)))
