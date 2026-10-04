"""Expose loss of an earlier Unknown after an unrelated committed action."""
import hashlib,json,resource,sys,tempfile,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT;sys.path.insert(0,str(SOURCE/'adapter'))
from recovery_store import RecoveryStore as Journal
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('repro-'+str(time.time_ns()));OUT.mkdir()
report={'passed':False,'checks':[],'scope':'Actual durable journal reproduction; no native mutation or GUI acceptance','inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),SOURCE/'adapter/recovery_journal.py',SOURCE/'adapter/endpoint.py']}}
def check(name,value):report['checks'].append({'name':name,'passed':bool(value)});assert value,name
bound={'lifetime':'71','session':'2','frontend':'3'}
a={'request':'41','generation':'43','incarnation':'7','operation':'maximize','context':{'lifetime':'71','epoch':'3','output':'14','revision':'13'}}
b={**a,'request':'42','generation':'44','incarnation':'8'}
try:
 with tempfile.TemporaryDirectory(prefix='elm-unknown-repro-') as tmp:
  runtime=Path(tmp);runtime.chmod(0o700)
  with Journal(runtime,'fixture','71') as j:
   j.begin(bound,a,2);j.settle({'binding':bound,'intent':a,'effectProtocol':2,'status':'Unknown'})
   check('AUnknownDurable',j.read()['status']=='Unknown')
   check('AUncertaintyInitiallyRecoverable',j.uncertain(bound)['intent']==a)
   j.begin(bound,b,2);j.settle({'binding':bound,'intent':b,'effectProtocol':2,'status':'Committed'})
   check('BCommitDurable',j.read()['intent']==b and j.read()['status']=='Committed')
  with Journal(runtime,'fixture','71') as j:
   recovered=j.uncertain(dict(bound,session='4',frontend='5'));report['observedRecovery']=recovered
   check('AUnknownMustSurviveUnrelatedBCommitAndColdRestart',recovered is not None and recovered['intent']==a)
 report['passed']=True
except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
