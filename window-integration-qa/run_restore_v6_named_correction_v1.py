#!/usr/bin/python3
"""Execute actual named restore scenarios skipped by the default Quint filter."""
import datetime,hashlib,json,os,re,stat,subprocess,time
from pathlib import Path
from qa_launch import require_qa_scope
Q=Path('/home/hoskinson/window-integration-qa');B=Q/'restore-focus-transaction-design-v6';O=Q/'restore-v6-actual-named-correction-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def publish(path,row):
    raw=(json.dumps(row,indent=2)+'\n').encode()
    with os.fdopen(os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
scope=require_qa_scope();O.mkdir(mode=0o700)
models=[B/'focus_transaction.qnt',B/'focus_transaction_test.qnt']
before={str(p):dict(sha256=sha(p),mode=stat.S_IMODE(p.stat().st_mode)) for p in models}
names=re.findall(r'^\s*run\s+([A-Za-z_][A-Za-z0-9_]*)\s*=',models[1].read_text(),re.M)
assert len(names)==45 and len(set(names))==45
command=['quint','test','focus_transaction_test.qnt','--backend=rust','--seed=2026100228','--match=^('+'|'.join(names)+')$']
start=time.monotonic();log=O/'named.log'
with os.fdopen(os.open(log,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as stream:
    result=subprocess.run(command,cwd=B,stdout=stream,stderr=subprocess.STDOUT,timeout=120)
    stream.flush();os.fsync(stream.fileno())
text=log.read_text();actual=re.findall(r'^\s*ok ([A-Za-z_][A-Za-z0-9_]*) passed \d+ test\(s\)',text,re.M)
after={str(p):dict(sha256=sha(p),mode=stat.S_IMODE(p.stat().st_mode)) for p in models}
passed=result.returncode==0 and before==after and len(actual)==45 and set(actual)==set(names) and '45 passing' in text
old=json.loads((B/'formal-before-runtime.json').read_bytes())
assert len(old['checks'])==3
for x in old['checks']:assert sha(x['log'])==x['sha256']
assert Path(old['checks'][1]['log']).read_text().strip()=='focus_transaction_test'
row=dict(result='pass' if passed else 'fail',schema='actual-restore-v6-named-correction-v1',observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope=scope,
    command=command,cwd=str(B),exitCode=result.returncode,elapsedSeconds=time.monotonic()-start,log=str(log),logSHA256=sha(log),sourceBefore=before,sourceAfter=after,sourceStable=before==after,
    expectedNames=names,actualPassedNames=actual,actualNamedScenarios=len(actual),originalDefaultNamedScenariosExecuted=0,originalFalseNamedClaim=45,
    originalReportSHA256=sha(B/'formal-before-runtime.json'),retainedOriginalInvariant=dict(samples=2000,steps=100,log=old['checks'][2]['log'],sha256=old['checks'][2]['sha256'],exitCode=old['checks'][2]['exitCode']),
    invariantNewlyRun=False,productionSourceChanged=False,GUI=False,nativeAccepted=False,mainChanged=False)
publish(O/'report.json',row)
print(json.dumps(dict(result=row['result'],actualNamedScenarios=len(actual),expected=45,sourceStable=before==after,reportSHA256=sha(O/'report.json'))))
raise SystemExit(0 if passed else 1)
