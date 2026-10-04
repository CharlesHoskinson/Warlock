"""Semantically identical original full keys must ignore JSON member order."""
import copy,hashlib,json,resource,sys,tempfile,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT.parent/'elm-multi-recovery-broker-fixed-v286';sys.path.insert(0,str(SOURCE/'adapter'))
from durable_ledger import Ledger
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('order-'+str(time.time_ns()));OUT.mkdir()
report={'passed':False,'checks':[],'scope':'Actual full-key ledger correlation; no native/GUI acceptance','inputs':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),*sorted((SOURCE/'adapter').glob('*.py'))]}}
def check(name,value):report['checks'].append({'name':name,'passed':bool(value)});assert value,name
def reverse(value):return {k:reverse(v) if isinstance(v,dict) else v for k,v in reversed(list(value.items()))}
b={'lifetime':'71','session':'2','frontend':'3'};i={'request':'41','generation':'43','incarnation':'7','operation':'maximize','context':{'lifetime':'71','epoch':'3','output':'14','revision':'13'}}
try:
 with tempfile.TemporaryDirectory(prefix='elm-order-') as tmp:
  runtime=Path(tmp);runtime.chmod(0o700)
  with Ledger(runtime,'fixture','71') as ledger:
   ledger.begin(b,i,2);check('originalPendingDurable',len(ledger.snapshot()['entries'])==1)
   check('reorderedJSONIsSameFullKey',reverse(b)==b and reverse(i)==i)
   outcome={'protocolVersion':3,'kind':'effect-outcome','effectProtocol':2,'binding':reverse(b),'intent':reverse(i),'status':'Committed','reason':'applied','revision':'13','outputGeneration':'14'}
   ledger.settle(outcome);check('reorderedOriginalReceiptSettlesExactlyOne',ledger.snapshot()['entries']==[])
 report['passed']=True
except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc())
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])
