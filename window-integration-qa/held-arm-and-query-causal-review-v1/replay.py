"""Additive retained actual replay after root-confirmed terminal; no live commands."""
from pathlib import Path
import hashlib,json,os
B=Path(__file__).resolve().parent;Q=B.parent;STAGE=Q/'toolkit-held-matrix-v14';A=STAGE/'attempt-1/qt-wayland'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def lines(p):
 raw=p.read_bytes();assert raw.endswith(b'\n');return [json.loads(x)for x in raw.splitlines()]
r=json.loads((A/'report.json').read_text());events=lines(A/'terminal-helpers/helper-events.jsonl');tracepath=A/'terminal-helpers/delegate-diagnostics/3455195-14245997.jsonl';trace=lines(tracepath)
starts=[x for x in events if x['event']=='started'];ends=[x for x in events if x['event']=='terminal'];assert len(starts)==len(ends)==17 and len(events)==34
bad=[x for x in ends if x['exitCode']!=0];assert len(bad)==1 and bad[0]['operation']=='list-json:3455195:14245997' and bad[0]['exitCode']==120
start=next(x for x in starts if x['operation']==bad[0]['operation']);assert start['queryRoot']=='qs' and start['delegate']['pid']==3455266 and start['delegate']['start']=='14246009'
assert trace[-1]['event']=='delegate-wait-terminal' and trace[-1]['complete'] and trace[-1]['errors']==[] and trace[-1]['exitCode']==120 and trace[-1]['rawWaitStatus']==30720
entry=next(x for x in trace if x['event']=='stdio-write-entry' and x['fd']==1);reply=next(x for x in trace if x['event']=='stdio-write-return' and x['entry']==entry['index'])
assert bytes.fromhex(entry['offeredBytesHex'])==b'[]\n' and reply['kernelReturn']==-32 and reply['errno']==32 and reply['deliveredCount']==0
assert entry['parentObservation']['kind']=='absent' and entry['parentObservation']['pidfdExitObserved'] and entry['qsObservation']['kind']=='absent'
qs=r['cleanup']['shell'];kill=next(x for x in qs['records']if x['role']=='normal-kill');assert qs['normalQuit'] and qs['exitCode']==0 and kill['returncode']==0 and kill['completedUtcNs']<qs['exitObservedUtcNs']<entry['utcNs']<trace[-1]['utcNs']
assert all(x['exitCode']==0 for x in ends if x is not bad[0]);assert 'Prior helper boundary changed during arm' in r['cases'][1]['error']
frozen=json.loads((STAGE/'frozen-inputs.json').read_text());witnesses={}
for p in [STAGE/'evaluation_setup.py',STAGE/'helper_observer.py',STAGE/'qs_lifecycle.py',STAGE/'delegate_diagnostics.py',STAGE/'run_native.py',STAGE/'payload/home/.config/omarchy/plugins/hoskinson.windows/widget_v65/Windows.qml']:
 assert frozen['inputs'][str(p)]==sha(p) and frozen['inputModes'][str(p)]==p.stat().st_mode&0o7777
 witnesses[str(p)]=dict(sha256=sha(p),mode=p.stat().st_mode&0o7777)
for p in [A/'report.json',A/'terminal-helpers/helper-events.jsonl',A/'terminal-helpers/helper-config.json',A/'terminal-helpers/delegate-diagnostics/archive.json',tracepath,A/'taskbar-shell.log',STAGE/'frozen-inputs.json']:
 witnesses[str(p)]=dict(sha256=sha(p),mode=p.stat().st_mode&0o7777)
report=dict(result='pass bounded causal replay',wholeCampaign='FAIL',cases={'move-escape':'PASS','move-reload':'FAIL at arm before reload command'},counts=dict(started=17,terminal=17,nonzero=1,refusals=0),failedQuery=dict(start=start,terminal=bad[0],observerRecords=len(trace),firstStdoutEntry=entry,firstStdoutReturn=reply,normalWait=trace[-1]),normalQSQuit=qs,attribution=dict(actualV14PostQSQuitEpipeProved=True,actualParentExitCodeKnown=False,historicalV10CauseProved=False,armDisjunctionBranchProved=False,armSourceGap='outer quiet observation -> proposal/source/IPC authorization -> locked recheck; actual config/row/pending predicate branch not separately retained',exit120Accepted=False,helperBudgetsChanged=False,full52Accepted=False),witnesses=witnesses,nativeLaunch=False,mainChanges=False)
fd=os.open(B/'actual-v14-causal-replay.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
with os.fdopen(fd,'w')as out:json.dump(report,out,indent=2);out.write('\n')
print(json.dumps(dict(result=report['result'],report=str(B/'actual-v14-causal-replay.json'),sha256=sha(B/'actual-v14-causal-replay.json'))))
