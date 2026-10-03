#!/usr/bin/python3
"""Record failed native gates and corrected actual named-model evidence."""
import datetime,hashlib,json,os,stat
from pathlib import Path
from qa_launch import require_qa_scope
scope=require_qa_scope();Q=Path('/home/hoskinson/window-integration-qa');S=Path('/home/hoskinson/window-behavior-spec');C=Q/'root-resume-checkpoint-20261002-v10'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
targets=[S/'overnight-status.json',S/'PARITY_STATUS.md']
for p in [Q/'family-preparation-thumbnail-v14/frozen-inputs.json',Q/'pin-max-native-campaign-b-v4/frozen-inputs.json',Q/'pin-frontend-composition-v2/source-ready-v2.json']:
    r=json.loads(p.read_bytes());assert all(str(t)not in r['inputs'] for t in targets)
old=json.loads(targets[0].read_bytes());state=dict(old['latestUserStatusCheckpoint']);now=datetime.datetime.now(datetime.timezone.utc).isoformat()
failure=Q/'pin-max-native-b-v4-root-failure-v1.json';pin=json.loads(failure.read_bytes())
assert pin['actualCompletedCases']==['B%02d'%i for i in range(1,11)] and pin['mainPreservationPassed']==18
state.update(timestampUTC=now,automaticLoopReactivationConfirmed=False,automaticGoalStatus='blocked',GUIRunning=False)
state['pinB']=dict(candidate='pin-max-native-campaign-b-v4',attemptStatus='fail',actualCompletedCases=pin['actualCompletedCases'],fullIncrementAccepted=False,fullCampaignAccepted=False,
    rootFailureSHA256=sha(failure),normalPrivateClosureObserved=True,mainPreservationPassed=18,
    primaryFailure='B11 invalid QA assumption: allows_input=false does not block input; genuine native blocker setup under review.',
    actualProducerNamedScenarios=14,originalDefaultProducerNamedScenariosExecuted=0,correctedNamedProofSHA256=sha(Q/'pin-producer-actual-named-correction-v1/report.json'))
state['restore'].update(actualCorrectedTransactionNamedScenarios=45,originalDefaultTransactionNamedScenariosExecuted=0,correctedNamedProofSHA256=sha(Q/'restore-v6-actual-named-correction-v1/report.json'),
    next='Review fresh fused capture proposal separating normal helper closure and both output files; apply only after model/source approval, then actual original38/34.')
state['next']=['Review genuine native input blocker setup and independent no-focus case, preserving non-revival assertions; full B13–B24 and broader predicates remain open.',
    'Review capture fusion refinement; original restore baseline38/recovery34 with unchanged deadlines remain required.',
    'Review actual Quickshell launcher/owning-header probe; required real routes precede fixed reliability campaign.',
    'Finish original52 dragging/resize/reload, cancellation and reduced-motion native QA.',
    'Complete display/hardware cadence/accessibility, combined regression and deployment.']
def enc(r):return (json.dumps(r,indent=2)+'\n').encode()
def publish(p,raw,mode=0o600):
    with os.fdopen(os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode),'wb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
C.mkdir(mode=0o700);before={p:p.read_bytes() for p in targets}
for p,raw in before.items():publish(C/('before-'+p.name),raw)
deployed=old['deployed'];old.update(updated=now,updatedUTC=now,complete=False,
    guiOwner='Root sole serial native GUI launcher. No current GUI run; latest Bv4 failed at B11 after ten completed cases. No main deployment.',
    loop='User requested resume; current turn working. Goal tool reports blocked; automatic continuation has not been reactivated.',
    currentWork='Native blocker source proposal; capture fusion output/closure refinement; private actual-Quickshell launcher and owning-header probe.',
    latestProgress=dict(updated=now,classification='meaningful-progress-full-parity-incomplete',checkpoint=state,fullParityAccepted=False,previousProgressRetainedIn=str(C/'before-overnight-status.json')),
    latestUserStatusCheckpoint=state,next=state['next'])
assert old['deployed']==deployed
text=before[targets[1]].decode();tail=text.split('## Feature audit',1)[1]
head='''# Windows 11 window-system parity status

## Current checkpoint — resumed work, 2026-10-03 UTC

Full parity remains incomplete. Candidates remain private; the main desktop is unchanged.

- **Pin campaign A passed:**14 feature checks. Bv4 completed B01–B10, including both MAX pin/unpin paths, two overlapping-window click cases and modal focus. It failed B11 because the QA incorrectly treated `allows_input=false` as an input blocker. A genuine native blocker setup is under review; the non-revival assertion remains mandatory. All18 main preservation checks and normal private closure/module unload passed. B12, remaining full-case predicates and B13–B24 remain unaccepted.
- **Restore remains rejected:** V28 passed444 CPU checks and its original collector passed169 CPU checks. The unprofiled baseline reached19 checks/17 pass: six focus actions and three refreshes completed before metadata at about692 ms; three captures exist, but no renderer seed/uploads before the original two-second deadline. All helpers exited normally and all15 main checks passed. Original baseline38/recovery34 remain mandatory. A pixel-preserving fused capture proposal is being refined before application.
- **Quint coverage corrected:** default name filtering previously executed zero of the declared45 restore transaction scenarios and14 producer scenarios. Both exact source models now passed explicit45 and14 named runs; original invariant traces remain separately retained. The selected35 pin design,20 transfer,24 hit and original205 collector named proofs were independently checked and unaffected. Historical false counts remain preserved and disclosed.
- **Process verifier:** V9 actual Qt-signal fault component and five V10 CPU components are independently accepted. Actual Quickshell/menu and reliability remain open.
- **Popup/input:** source review passed24 Quint cases/2000 traces,28 decoder/controller tests, one receipt-loop test and six QML-as-JavaScript checks. A fresh actual-Quickshell launcher and probe compiled against the owning candidate headers are being prepared. No actual Quickshell/native input/reliability acceptance yet.
- **Remaining:** complete pin/focus/masks/scroll/transfer; restore38/recovery34; original52 dragging/resize/reload; cancellation/reduced motion; actual popup/input/reliability; multiple displays/hardware cadence/accessibility; combined regression and deployment.

The [live status record](overnight-status.json) preserves failures and bounded evidence. This session is working after resume; the saved automatic goal remains marked blocked and automatic continuation has not been reactivated.

## Feature audit'''
after={targets[0]:enc(old),targets[1]:(head+tail).encode()}
for p,raw in after.items():
    assert p.read_bytes()==before[p]
    temp=p.with_name(p.name+'.resume-v10.new');publish(temp,raw,stat.S_IMODE(p.stat().st_mode));temp.replace(p);publish(C/('after-'+p.name),raw)
publish(C/'checkpoint.json',enc(state))
for folder in [S,C]:
    fd=os.open(folder,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
print(json.dumps(dict(result='recorded',checkpoint=str(C/'checkpoint.json'),actualPinCases=10,restoreNamed=45,producerNamed=14,fullParity=False,mainChanged=False)))
