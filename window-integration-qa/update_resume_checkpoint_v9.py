#!/usr/bin/python3
"""Record bounded progress while preserving previous status and deployed metadata."""
import datetime,hashlib,json,os,stat
from pathlib import Path
Q=Path('/home/hoskinson/window-integration-qa');S=Path('/home/hoskinson/window-behavior-spec')
C=Q/'root-resume-checkpoint-20261002-v9'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
targets=[S/'overnight-status.json',S/'PARITY_STATUS.md']
selected=[Q/'family-preparation-thumbnail-v14/frozen-inputs.json',Q/'pin-max-native-campaign-b-v4/frozen-inputs.json',Q/'pin-frontend-composition-v2/source-ready-v2.json',S/'process-private-qs-route-plan-v1/source-plan-handoff.json']
for p in selected:
    row=json.loads(p.read_bytes())
    assert all(str(t) not in row.get('inputs',{}) for t in targets)
pin=Q/'pin-max-native-campaign-b-v4/attempt-1/native/campaign-b-trace.json'
trace=json.loads(pin.read_bytes())
cases=[x['caseResult']['case'] for x in trace['trace'] if 'caseResult' in x]
assert cases[:7]==['B%02d'%i for i in range(1,8)]
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
state=dict(timestampUTC=now,fullParity=False,automaticLoopReactivationConfirmed=False,mainChanged=False,
    nativePinA=dict(accepted=True,featureChecks=14),
    pinB=dict(candidate='pin-max-native-campaign-b-v4',completedCases=cases,attemptStatus='running',componentIncrementAccepted=False,fullCampaignAccepted=False,rootSourceReviewSHA256=sha(Q/'pin-max-native-b-v4-root-source-review-v1.json')),
    processV9=dict(componentAccepted=True),
    processReuse=dict(requiredComponents=5,actualComponentsAccepted=True,rootReviewSHA256=sha(Q/'process-terminal-v10-root-component-review-v1.json')),
    popupComposition=dict(sourceReviewed=True,formalNamed=24,formalTraces=2000,actualInstalledQuickshellAccepted=False,rootReviewSHA256=sha(Q/'popup-composition-root-source-review-v2.json')),
    restore=dict(candidate='service-restore-focus-transaction-v28',actualCPU=444,baselineResult='fail',reachedChecks=19,passedChecks=17,baselineRequired=38,faultsRequired=34,baselineAccepted=False,faultsAuthorized=False,focusTransactionAndThreeRefreshesCompleted=True,allHelpersNormal=True,actualCaptures=3,rendererSeedAndUploadsAbsent=True,rootFailureSHA256=sha(Q/'thumbnail-v14-root-failure-audit-v1.json'),next='Model and review a pixel-preserving capture/image preparation optimization before a fresh derivative.'),
    next=['Finish actual B01–B12 and independent source/main/normal teardown verification; remaining B13–B24 and fuller-case predicates remain open.',
          'Review restore capture optimization proposal, then actual original baseline38 and recovery34 with unchanged deadlines.',
          'Review exact real Quickshell launcher/ABI/materialization packet, then private required routes and fixed reliability campaign.',
          'Complete original52 drag/resize/reload, cancellation and reduced motion native gates.',
          'Complete display/hardware cadence/accessibility, combined regression and deployment.'])
def publish(p,raw,mode=0o600):
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode)
    with os.fdopen(fd,'wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
def encoded(r):return (json.dumps(r,indent=2)+'\n').encode()
C.mkdir(mode=0o700)
before={p:p.read_bytes() for p in targets}
for p,raw in before.items():publish(C/('before-'+p.name),raw)
old=json.loads(before[targets[0]])
deployed=old.get('deployed')
old.update(updated=now,updatedUTC=now,complete=False,currentWork='Private pin Bv4 native cases; restore capture deadline proposal; real Quickshell wrapper and owning-header probe preparation.',
    latestProgress=dict(updated=now,classification='meaningful-progress-full-parity-incomplete',checkpoint=state,fullParityAccepted=False,previousProgressRetainedIn=str(C/'before-overnight-status.json')),
    latestUserStatusCheckpoint=state,next=state['next'])
assert old.get('deployed')==deployed
tail=before[targets[1]].decode().split('## Feature audit',1)[1]
head='''# Windows 11 window-system parity status

## Current checkpoint — resumed work, 2026-10-03 UTC

Full parity remains incomplete. Candidates remain private; the main desktop is unchanged.

- **Pin campaign A passed:** 14 feature checks. The fresh Bv4 run has completed B01–B07, including both MAX pin/unpin/normal-return paths and actual overlapping-window click delivery. B08–B12 and teardown are running; full B and its remaining cases are unaccepted.
- **Restore remains rejected:** V28 passed 444 CPU checks and its original collector passed169 CPU checks. The unprofiled native baseline reached19 checks/17 pass. Six real focus actions and three refreshes completed before metadata at about692 ms; three actual PNG captures exist. Renderer seed/uploads were absent before the original two-second deadline. All helpers exited normally, all15 main preservation checks and native unload passed. Original baseline38/recovery34 remain mandatory and unaccepted. A pixel-preserving image preparation optimization is being modeled.
- **Process verifier:** the V9 actual Qt-signal fault component and all five V10 required CPU components are independently accepted. Actual Quickshell/menu and reliability remain open.
- **Popup/input composition:** source review passed, with24 Quint cases and2000 traces,28 decoder/controller CPU tests, one receipt-loop CPU test and six exact-QML-as-JavaScript checks. Those checks do not establish Qt/Quickshell native behavior. The exact private launcher and owning-header probe pair are being prepared.
- **Remaining acceptance:** full pin/MAX/focus/scroll/transfer; restore baseline38/recovery34; original52 dragging/resize/reload; cancellation/reduced motion; actual popup/input/reliability; multiple displays/hardware cadence/accessibility; final combined regression and deployment.

The [live status record](overnight-status.json) and immutable QA artifacts preserve failed runs and bounded successes. Work continues after the resume request; automatic loop reactivation is unconfirmed.

## Feature audit'''
after={targets[0]:encoded(old),targets[1]:(head+tail).encode()}
for p,raw in after.items():
    assert p.read_bytes()==before[p]
    temp=p.with_name(p.name+'.resume-v9.new');publish(temp,raw,stat.S_IMODE(p.stat().st_mode));temp.replace(p)
    publish(C/('after-'+p.name),raw)
publish(C/'checkpoint.json',encoded(state))
for folder in [C,S]:
    fd=os.open(folder,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
print(json.dumps(dict(result='recorded',checkpoint=str(C/'checkpoint.json'),completedPinCases=cases,fullParity=False,mainChanged=False)))
