#!/usr/bin/python3
"""Execute the 14 actual producer scenarios omitted by Quint's default filter."""
import datetime,hashlib,json,os,re,stat,subprocess,time
from pathlib import Path
from qa_launch import require_qa_scope
Q=Path('/home/hoskinson/window-integration-qa');B=Q/'pin-max-native-campaign-b-v4';O=Q/'pin-producer-actual-named-correction-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
scope=require_qa_scope();O.mkdir(mode=0o700)
model=B/'producer_closure.qnt';before=dict(sha256=sha(model),mode=stat.S_IMODE(model.stat().st_mode))
assert before['sha256']=='80baba7aa866171269068baa2b94c1589c279e16d25ac6c32fae42052cb0af57'
names=re.findall(r'^\s*run\s+([A-Za-z_][A-Za-z0-9_]*)\s*=',model.read_text(),re.M)
assert len(names)==14 and len(set(names))==14
command=['quint','test',str(model),'--backend=rust','--seed=2026100228','--match=^('+'|'.join(names)+')$']
log=O/'named.log';start=time.monotonic()
with os.fdopen(os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as stream:
    result=subprocess.run(command,cwd=B,stdout=stream,stderr=subprocess.STDOUT,timeout=120)
    stream.flush();os.fsync(stream.fileno())
text=log.read_text();actual=re.findall(r'^\s*ok ([A-Za-z_][A-Za-z0-9_]*) passed \d+ test\(s\)',text,re.M)
after=dict(sha256=sha(model),mode=stat.S_IMODE(model.stat().st_mode))
passed=result.returncode==0 and before==after and len(actual)==14 and set(actual)==set(names) and '14 passing' in text
prior=json.loads((B/'producer-formal-before-classification-final.json').read_bytes())
assert Path(prior['commands'][1]['log']).read_text().strip()=='producer_closure'
for x in prior['commands']:assert sha(x['log'])==x['logSHA256']
row=dict(result='pass' if passed else 'fail',schema='actual-pin-producer-named-correction-v1',observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope=scope,command=command,cwd=str(B),exitCode=result.returncode,elapsedSeconds=time.monotonic()-start,
    log=str(log),logSHA256=sha(log),model=str(model),sourceBefore=before,sourceAfter=after,sourceStable=before==after,expectedNames=names,actualPassedNames=actual,actualNamedScenarios=len(actual),originalDefaultNamedScenariosExecuted=0,originalFalseNamedClaim=14,
    originalReportSHA256=sha(B/'producer-formal-before-classification-final.json'),retainedInvariant=dict(samples=2000,steps=100,log=prior['commands'][2]['log'],sha256=prior['commands'][2]['logSHA256'],exitCode=prior['commands'][2]['exitCode']),invariantNewlyRun=False,
    historicalNamedBeforeClassifierClaim=False,productionSourceChanged=False,GUI=False,nativeAccepted=False,mainChanged=False)
p=O/'report.json'
with os.fdopen(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps(dict(result=row['result'],actualNamedScenarios=len(actual),expected=14,sourceStable=before==after,reportSHA256=sha(p))))
raise SystemExit(0 if passed else 1)
