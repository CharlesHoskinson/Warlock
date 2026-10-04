"""Protected CPU proof. Synthetic schema fixtures are not GPU measurements."""
import copy, hashlib, importlib.util, json, pathlib, random, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]; REPO=ROOT.parents[1];OUT=ROOT/'qa'
spec=importlib.util.spec_from_file_location('budget_validator',ROOT/'validator.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
UNITS={'latency':'ms','cpu':'percent-one-core','wakeups':'count-per-second','memory':'KiB','frame-misses':'count','power':'W','copy-transfer':'bytes'}
def valid():
 doc={'schema':'elm-budget-preflight/1','frozenUTC':'2026-10-01T00:00:00Z','approvalReference':'SYNTHETIC-TEST-NOT-PRODUCT-APPROVAL','workloads':[]}
 for name in v.WORKLOADS:
  row={'id':name,'fixtureSHA256':'a'*64,'warmCold':'cold' if name=='cold-start' else 'warm','definition':'synthetic '+name,'metrics':{}}
  for kind in v.METRICS:
   m={'unit':UNITS[kind],'definition':'synthetic '+kind,'minimumSamples':3,'limits':{'absoluteMax':4,'regressionMaxPercent':10,'overheadMax':.5}}
   o={'sourceTuple':'synthetic source','evidenceReference':'fixture only','evidenceSHA256':'b'*64,'clockDomain':'CLOCK_MONOTONIC','clockMapping':'same-domain','startEvent':'native-seat-input' if kind=='latency' else 'sample-start','endEvent':'native-present' if kind=='latency' else 'sample-end','measurementKind':'native-input-to-present' if kind=='latency' else 'whole-process-group-sample','adapter':'synthetic gpu','driver':'synthetic driver','backend':'synthetic backend','engine':'synthetic engine','wholeProcessGroupComplete':True,'output':{'id':'synthetic-output','width':800,'height':600,'refreshHz':60,'scale':1,'transform':'normal'},'unit':m['unit'],'definition':m['definition'],'samples':[1,2,3],'count':3,'p50':2,'p95':3,'p99':3,'instrumentationOverhead':.1,'measuredUTC':'2026-10-02T00:00:00Z'}
   m['baseline']=copy.deepcopy(o);m['candidate']=copy.deepcopy(o);row['metrics'][kind]=m
  doc['workloads'].append(row)
 return doc
checks=[]
def check(name,ok,**data):
 checks.append({'name':name,'passed':bool(ok),**data});assert ok,name
base=valid();(OUT/'valid-synthetic-matrix.json').write_text(json.dumps(base,indent=2)+'\n');r=v.validate(base);check('synthetic-complete-schema-ready-not-accepted',r['schemaReady'] and not r['performanceAccepted'],verdict=r['verdict'])
def mutation(name,edit,expected):
 d=copy.deepcopy(base);edit(d);r=v.validate(d);check(name,not r['schemaReady'] and not r['performanceAccepted'] and any(expected in i['path'] or expected in i['reason'] for i in r['issues']),issues=r['issues']);return d
m=lambda d:d['workloads'][0]['metrics']['latency'];o=lambda d:m(d)['candidate']
for value,label in [(None,'null'),(True,'boolean'),(-1,'negative'),(float('nan'),'nan'),(float('inf'),'infinite'),(10**1000,'overflow-integer')]:
 mutation('reject-'+label+'-absolute-limit',lambda d,x=value:m(d)['limits'].__setitem__('absoluteMax',x),'absoluteMax')
mutation('missing-regression-limit',lambda d:m(d)['limits'].pop('regressionMaxPercent'),'regressionMaxPercent')
mutation('missing-overhead',lambda d:o(d).__setitem__('instrumentationOverhead',None),'instrumentationOverhead')
mutation('overhead-exceeds-frozen-maximum',lambda d:o(d).__setitem__('instrumentationOverhead',.6),'instrumentationOverhead')
mutation('missing-clock-domain',lambda d:o(d).pop('clockDomain'),'clockDomain')
mutation('missing-clock-mapping',lambda d:o(d).pop('clockMapping'),'clockMapping')
mutation('wrong-clock-comparison',lambda d:o(d).__setitem__('clockDomain','WALL_CLOCK'),'clockDomain')
mutation('helper-dom-not-native-presentation',lambda d:o(d).__setitem__('measurementKind','helper-to-DOM'),'measurementKind')
mutation('missing-native-present-end-event',lambda d:o(d).pop('endEvent'),'endEvent')
mutation('empty-samples',lambda d:o(d).__setitem__('samples',[]),'samples')
mutation('false-sample-count',lambda d:o(d).__setitem__('count',4),'count')
mutation('minimum-samples-not-met',lambda d:m(d).__setitem__('minimumSamples',4),'count')
mutation('inconsistent-p99',lambda d:o(d).__setitem__('p99',2),'p99')
mutation('infinite-sample',lambda d:o(d).__setitem__('samples',[1,2,float('inf')]),'samples')
mutation('missing-workload-fixture-identity',lambda d:d['workloads'][0].pop('fixtureSHA256'),'fixtureSHA256')
mutation('missing-workload-category',lambda d:d['workloads'].pop(),'workloads')
mutation('duplicate-workload-category',lambda d:d['workloads'][1].__setitem__('id','cold-start'),'workloads')
mutation('wrong-device-comparison',lambda d:o(d).__setitem__('adapter','different GPU'),'adapter')
mutation('missing-driver',lambda d:o(d).pop('driver'),'driver')
mutation('different-output-refresh',lambda d:o(d)['output'].__setitem__('refreshHz',240),'output')
mutation('missing-output-scale',lambda d:o(d)['output'].pop('scale'),'scale')
mutation('partial-process-lifetime',lambda d:o(d).__setitem__('wholeProcessGroupComplete',False),'wholeProcessGroupComplete')
mutation('post-hoc-threshold-freeze',lambda d:d.__setitem__('frozenUTC','2026-10-03T00:00:00Z'),'measuredUTC')
mutation('timezone-free-clock-stamp',lambda d:o(d).__setitem__('measuredUTC','2026-10-02T00:00:00'),'measuredUTC')
mutation('unit-mismatch',lambda d:o(d).__setitem__('unit','seconds'),'units')
mutation('missing-metric-category',lambda d:d['workloads'][0]['metrics'].pop('power'),'metrics')
mutation('unreviewed-applicability-exclusion',lambda d:d['workloads'][0]['metrics'].__setitem__('power',{'excluded':True,'reason':'not measured'}),'exclusion')
d=copy.deepcopy(base);d['workloads'][0]['metrics']['power']={'excluded':True,'reason':'synthetic not-applicable fixture','reviewReference':'synthetic review'};check('explicit-exclusion-structural-only',v.validate(d)['schemaReady'] and not v.validate(d)['performanceAccepted'])
d=copy.deepcopy(base);m(d)['limits']['absoluteMax']=0;check('complete-schema-with-exceeded-budget-never-accepted',v.validate(d)['schemaReady'] and not v.validate(d)['performanceAccepted'])
legacy=REPO/'docs/elm-roadmap/delivery/budgets.json';before=hashlib.sha256(legacy.read_bytes()).hexdigest();r=v.validate(v.load(legacy));check('actual-null-calibration-remains-incomplete',r['verdict']=='calibration-only' and r['completeness']=='incomplete' and not r['schemaReady'] and not r['performanceAccepted']);(OUT/'current-budgets-verdict.json').write_text(json.dumps(r,indent=2)+'\n')
for name,text in [('nan-json','{"schema": NaN}'),('duplicate-field-json','{"schema":1,"schema":2}')]:
 f=OUT/(name+'.json');f.write_text(text)
 try:v.load(f);ok=False
 except ValueError:ok=True
 check('reject-'+name,ok)
for name,inputfile,expected in [('valid',OUT/'valid-synthetic-matrix.json',0),('legacy',legacy,2),('invalid',OUT/'nan-json.json',2)]:
 p=subprocess.run([sys.executable,'-B',str(ROOT/'validator.py'),str(inputfile)],capture_output=True,text=True,timeout=5);(OUT/(name+'-cli.stdout')).write_text(p.stdout);(OUT/(name+'-cli.stderr')).write_text(p.stderr);check('cli-'+name,p.returncode==expected and not json.loads(p.stdout)['performanceAccepted'],exit=p.returncode)
check('original-budgets-byte-unchanged',hashlib.sha256(legacy.read_bytes()).hexdigest()==before)
report={'schema':1,'passed':all(c['passed'] for c in checks),'scope':'CPU structural preflight and synthetic/adversarial fixtures only; no thresholds approved, measurements acquired, evidence authenticity or native/GPU/release acceptance.','checks':checks,'currentBudgetsSHA256':before,'reviewedHistoricalInputs':{p:hashlib.sha256((REPO/p).read_bytes()).hexdigest() for p in ['implementation/elm-shared-measure-v160/qa/native-1791092448672748213/report.json','implementation/elm-related-soak-v164/qa/native-1791092969651719919/report.json']},'sourceHashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'validator.py',pathlib.Path(__file__)]},'mainDesktopActions':False}
(OUT/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(json.dumps({'passed':report['passed'],'checks':len(checks),'actualBudgetVerdict':r['verdict']}))
