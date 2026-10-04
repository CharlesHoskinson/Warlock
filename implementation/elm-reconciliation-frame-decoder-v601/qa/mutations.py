#!/usr/bin/env python3
import hashlib,json,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa'/('mutations-'+str(time.time_ns()));OUT.mkdir()
PRIMARY=max((ROOT/'qa').glob('tests-*/report.json'),key=lambda p:p.parent.name).parent
shutil.copy2(PRIMARY/'cases.json',OUT/'cases.json')
source=(ROOT/'src/ReconciliationFrame.elm').read_text()
mutations=[
 ('queried-binding-guard','proof.queriedBinding==record.binding','True'),
 ('accepted-action-read-id','observation.actionRequestId==expected.actionRequestId','True'),
 ('accepted-geometry-own-revision','observation.geometryContext==expected.geometryContext','True'),
 ('incorrect-cross-domain-equality','expectedValid && correlated','expectedValid && correlated && proof.sequence==observation.actionContext.revision'),
 ('unknown-history-conflation','D.map (\\_ -> Effects.Unknown)','D.map (\\_ -> Effects.Committed)')]
cases=json.loads((OUT/'cases.json').read_text())['cases'];reports=[]
for name,old,new in mutations:
 assert source.count(old)==1,(name,old)
 dest=OUT/name;shutil.copytree(ROOT/'src',dest/'src');shutil.copy2(ROOT/'elm.json',dest/'elm.json');shutil.copy2(ROOT/'qa/Probe.elm',dest/'src/Probe.elm')
 (dest/'src/ReconciliationFrame.elm').write_text(source.replace(old,new))
 commands=[]
 for label,cmd in [('compile',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','--optimize','src/Probe.elm','--output='+str(dest/'worker.js')]),('test',['node',str(ROOT/'qa/probe.cjs'),str(dest/'worker.js'),str(OUT/'cases.json'),str(dest/'results.json')])]:
  proc=subprocess.run(cmd,cwd=dest,capture_output=True,timeout=180);(dest/(label+'.stdout')).write_bytes(proc.stdout);(dest/(label+'.stderr')).write_bytes(proc.stderr);commands.append({'command':cmd,'cwd':str(dest),'exitCode':proc.returncode});assert proc.returncode==0,proc.stderr.decode()
 rows=json.loads((dest/'results.json').read_text());counterexamples=[]
 for case,row in zip(cases,rows):
  valid=row['ok']==case['expectedOk'] and (not row['ok'] or (row['historicalStatus']=='Unknown' and row['intent']==case['frame']['record']['intent'] and row['oldBinding']==case['frame']['record']['binding']))
  if not valid:counterexamples.append({'input':case,'actual':row})
 (dest/'counterexamples.json').write_text(json.dumps(counterexamples,indent=2)+'\n')
 reports.append({'name':name,'detected':bool(counterexamples),'counterexamples':len(counterexamples),'commands':commands,'sourceSHA256':hashlib.sha256((dest/'src/ReconciliationFrame.elm').read_bytes()).hexdigest()})
report={'passed':all(r['detected'] for r in reports),'controls':reports,'primaryCasesSHA256':hashlib.sha256((OUT/'cases.json').read_bytes()).hexdigest(),'nativeAcceptance':False}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'controls':len(reports)}));raise SystemExit(not report['passed'])
