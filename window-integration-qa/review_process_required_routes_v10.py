#!/usr/bin/python3
"""Independently review recorded CPU reuse components; never replay them."""
from pathlib import Path
import base64, datetime, hashlib, json, os, stat
QA=Path('/home/hoskinson/window-integration-qa')
H=QA/'process-terminal-v10-required-components-actual-handoff-v1.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(H)=='3f037aaceb6e3e7eea383e0736ef08228af2add26119711d6f0afb9d4b74d167'
h=json.loads(H.read_bytes())
assert set(h['inputs'])==set(h['inputModes'])
for name,wanted in h['inputs'].items():
    assert sha(name)==wanted,name
    assert stat.S_IMODE(Path(name).stat().st_mode)==h['inputModes'][name],name
ancestor=json.loads((QA/'process-terminal-required-routes-source-proposal-handoff-v1.json').read_bytes())
for field in ['inputs','inputModes']:
    assert all(h[field].get(k)==v for k,v in ancestor[field].items())
build=json.loads(Path(h['actualBuildPath']).read_bytes())
assert sha(h['actualBuildPath'])==h['actualBuildSHA256']
assert build['result']=='pass' and len(build['commands'])==9
assert all(r['exitCode']==0 for r in build['commands'])
assert len(build['reusedObjects'])==10 and len(build['depfiles'])==4
actual_deps=set()
for name,meta in build['depfiles'].items():
    assert sha(name)==meta['sha256']
    for raw in Path(name).read_text().replace('\\\n',' ').split(':',1)[1].split():
        for path in {Path(raw),Path(raw).resolve(strict=True)}:
            actual_deps.add(str(path))
            assert build['dependencies'][str(path)]['sha256']==sha(path)
            assert h['inputs'][str(path)]==sha(path)
assert actual_deps<=set(build['dependencies'])
replay=json.loads(Path(h['actualReplayPath']).read_bytes())
assert sha(h['actualReplayPath'])==h['actualReplaySHA256']
assert replay['result']=='pass' and len(replay['components'])==5
assert all(all(v is True for v in checks.values()) for checks in replay['checks'].values())
def diagnostic(row):
    raw=base64.b64decode(row['rawBase64'],validate=True)
    assert hashlib.sha256(raw).hexdigest()==row['rawSHA256']
    assert len(raw)==row['capturedBytes'] and row['stableMetadata'] is True
    assert row['truncated'] is False and not row.get('readError') and not row.get('parseError')
    assert stat.S_IMODE(row['statBefore']['mode'])==0o600
    value=json.loads(raw);assert value==row['parsed'];return value
actor_pids=[]
for item in replay['components']:
    path=Path(item['path']);assert sha(path)==item['sha256']
    row=json.loads(path.read_bytes());assert row['result']=='pass' and row['exitCode']==0
    assert stat.S_IMODE(path.stat().st_mode)==0o600
    if item['case'] not in ['normal-changed-command','cancelled-changed-command','same-command-reuse']:
        continue
    assert row['sourcesUnchanged'] is True and row['normalCPUPrivateRuntimeRemoved'] is True
    assert row['normalFixtureCleanup'] is True and row['originalEachHelperTransactionSeconds']==2
    values=[]
    for line in row['stdout'].splitlines():
        try:value=json.loads(line)
        except ValueError:continue
        if type(value) is dict and value.get('registryCase')==item['case']:values.append(value)
    assert len(values)==1
    value=values[0]
    assert value['result']=='pass' and value['helperLaunches']==2 and value['helperRetries']==0
    assert value['cpuAdapterOnly'] is True and value['actualQSProcessAccepted'] is False
    assert value['independentSecondActor'] is True and len(value['typedRefusals'])==8
    assert all(r['refused'] is True for r in value['typedRefusals'])
    first,second,armed=value['first'],value['second'],value['freshArmed']
    for field in ['historicalKernelProof','normalLifecycle','workerJoined','receiptVerified','stdoutEOF','stderrEOF','kernelGone']:
        assert first[field] is True and second[field] is True,field
    assert second['kernelBound'] is True and second['complete'] is True
    assert int(second['lease'])>int(first['lease'])
    for field in ['started','historicalKernelProof','stdoutEOF','stderrEOF','receiptVerified','complete']:
        assert armed[field] is False,field
    assert diagnostic(row['durableBeforeHookEvidence'])['state']==first
    assert diagnostic(row['durableBeforeSecondHelperEvidence'])['state']==armed
    if item['case']=='cancelled-changed-command':
        assert first['current'] is False and first['kernelBound'] is False and first['complete'] is False
    else:assert first['complete'] is True
    if item['case']!='same-command-reuse':assert value['terminalRetire']['terminalRetired'] is True
    receipts=row['durableReceipts'];assert receipts['entryLimitExceeded'] is False and len(receipts['files'])==2
    saved=[diagnostic(r) for r in receipts['files'].values()]
    assert sorted(saved,key=lambda x:x['authority']['frontend']['pid'])==sorted([json.loads(first['stdout']),json.loads(second['stdout'])],key=lambda x:x['authority']['frontend']['pid'])
    for receipt in saved:
        actor=receipt['authority']['frontend'];actor_pids.append(actor['pid'])
        assert not (Path('/proc')/str(actor['pid'])).exists()
assert len(actor_pids)==6 and len(set(actor_pids))==6
assert h['actualInstalledQSRetirePositiveAccepted'] is False and h['variedReliabilityAccepted'] is False
out=QA/'process-terminal-v10-root-component-review-v1.json'
result=dict(schema='root-process-required-routes-v10-review-v1',observedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    handoffSHA256=sha(H),inputsVerified=len(h['inputs']),wholeProposalInputsConserved=len(ancestor['inputs']),
    actualBuildCommands=9,currentDepfiles=4,actualCurrentDependencies=len(actual_deps),reusedCoreObjects=10,
    independentlyMatchedDurableFirstAndFreshStates=True,independentlyMatchedSixHelperReceipts=True,
    fiveCPUComponentsAccepted=True,helperTransactions=6,helperRetries=0,
    installedQSPositiveAccepted=False,nonNullWindowPopupAccepted=False,variedReliabilityAccepted=False,mainChanged=False)
raw=(json.dumps(result,indent=2)+'\n').encode();fd=os.open(out,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'wb')as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
print(json.dumps(dict(result='pass',reviewSHA256=hashlib.sha256(raw).hexdigest(),inputs=len(h['inputs']),components=5,helpers=6)))
