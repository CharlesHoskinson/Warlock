import ast,hashlib,json,pathlib,resource,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'qa'));from budget_timing import BudgetTiming
OUT=ROOT/'qa'/('timing-'+str(time.time_ns()));OUT.mkdir();r={'passed':False,'nativeAcceptance':False,'checks':[]}
def check(name,value):assert value,name;r['checks'].append(name)
from timing_source import original_ast as same_body
try:
 record={};timing=BudgetTiming(record);token=object();calls=[];assert timing.call('positive',time.monotonic()+6.,lambda:(calls.append(1),token)[1]) is token;check('exact one callback and returned identity',calls==[1]);check('original deadline recorded unchanged',record['budgetTimings'][0]['deadline']>record['budgetTimings'][0]['begin'])
 error=KeyboardInterrupt('primary')
 def failed():calls.append(2);raise error
 try:timing.call('failure',None,failed)
 except BaseException as caught:check('primary BaseException object retained',caught is error)
 check('failed call recorded',record['budgetTimings'][-1]['outcome']=='raised' and calls==[1,2])
 class Context:
  def __enter__(self):calls.append('enter');return token
  def __exit__(self,*args):calls.append(('exit',args[0]));return True
 with timing.context('ctx',None,Context()) as value:assert value is token;raise ValueError('suppressed')
 check('delegate enter and suppression preserved',calls[-2:]==['enter',('exit',ValueError)])
 import budget_timing;clock=budget_timing.time.monotonic
 def bad_clock():raise RuntimeError('clock')
 budget_timing.time.monotonic=bad_clock
 try:check('clock failure does not omit callback',timing.call('clock-refusal',None,lambda:token) is token)
 finally:budget_timing.time.monotonic=clock
 check('clock failure explicitly incomplete',record['timingComplete'] is False and record['timingClockErrors']==['RuntimeError','RuntimeError'])
 for _ in range(1030):assert timing.call('bounded',None,lambda:token) is token
 check('bounded records retain all call counts',len(record['budgetTimings'])==1024 and record['timingOverflow']>0 and record['timingCallCounts']['bounded']==1030)
 source=(ROOT/'qa/native.py').read_text();same_body(source);check('exact original365 AST excluding approved measurements',True)
 for name,changed in [('deadline',source.replace('boot=time.monotonic()+6','boot=time.monotonic()+60')),('guard',source.replace('after=process_guard(bounded.deadline)','after=before'))]:
  try:same_body(changed)
  except AssertionError:check('unsafe source '+name+' rejected',True)
  else:raise AssertionError('unsafe source accepted')
 for name in ('stdlib_origin.py','preflight.py','host_guard.py'):check('byteexact365 '+name,(ROOT/'qa'/name).read_bytes()==(ROOT.parent/'elm-own-popup-native-index-guard-v365/qa'/name).read_bytes())
 r.update(passed=True,inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'qa/native.py',ROOT/'qa/budget_timing.py',ROOT/'qa/timing_source.py',pathlib.Path(__file__)]})
except BaseException as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])
