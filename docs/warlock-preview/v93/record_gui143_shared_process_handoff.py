"""Record known native drain before recovery; keep whole-host recovery open."""
import json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');docs=pathlib.Path(__file__).parent;d=json.loads((docs/'component-report-gui143-shared-process-drain.json').read_text());assert d['passed'] and d['actualKnownSharedProcessNativeDrainQualified'] and not d['wholeHostRestartQualified']
text='''
GUI142 holds actual shared WebKit process failure: explicit private API stops
the original related controller/popup/bar process only after first current
snapshot/write. Original termination reason2/three actual view signals/current
source red19200 pass, but Native18618-check strict-close-before-GTK-recovery
oracle fails: recovery appears with original known models/realm still live,
then original final failure1/incomplete native teardown. Seven other normal
owned exits/private cleanup pass. Original normal18529/13/full119 pass; failed
source142/186 remain held. No native settlement follows process disappearance.

GUI143 is held: the owning shared termination handler urgently quarantines the
same known native realm and retains original failure/real reason/recovery path.
Original input/step/poll/receipts continue to strict policy/physical/ticket/
journal/confirmation close/empty custody BEFORE GTK recovery. Multiple actual
view termination signals cannot cancel drain. Original evaluation finish/error
has an optional owning known-duty drain hook; standalone/noncontrolled default
remains original. Unretired or uncertain custody explicitly refuses recovery
controls; it never becomes restart authority through process disappearance.

Exact unchanged186 oracle now18721 controls passes real shared process stop,
first source red19200, known owning/closing/strict closed before original GTK
recovery/backend normal, explicit dismissal retains failure1/seven other normal
exits/private cleanup/no criticals or incomplete teardown. No renderer/new realm/
reset/replay/inferred settlement. Original normal18829/13, known-reload18934/12,
current-error19022/host1 plus seven other normal, old-canceled19136/13,
rapid19251/17, delayed19318/8 and old-success19435/13 pass separately. Full119,
new shared-process-drain Quint9 named/200 samples and6 actual projected stages
pass. Exact hashes: component-report-gui143-shared-process-drain.json.

CONTROL047 is bounded to known preview-duty drain before GTK recovery in this
actual process-stop schedule. Actual native uncertainty, all evaluation-error/
termination schedules, whole-host restart/window-command journal/durable Unknown
remain open; the model does not qualify them. Original opacity0/physical/hardware,
pressure/expiry/full workload/RSS/full S09/release/AT/IME/journeys/deployment gates
remain. Next PUBLIC104 then actual uncertainty and durable Unknown/window-command/
whole-host restart work. Installed desktop/drafts/foreign edits are preserved;
the full GUI goal remains active.
'''
p=docs/'HANDOFF.md';s=p.read_text();assert 'GUI143 is held:' not in s;p.write_text(s+text)
p=docs/'NATIVE-ADMISSION-CONTROLS.md';s=p.read_text();marker='Bounded CONTROL-047 known shared process duty drain:';assert marker not in s
p.write_text(s+'\n'+marker+' GUI143 keeps original\nfailure while actual shared related WebKit termination signals quarantine the\noriginal realm; original native input/step/poll/receipts and strict policy/\nphysical/ticket/journal/confirmation close precede GTK recovery. Native187 exact\n186 oracle passes21: actual API/reason2/first source red19200/known closing/\nclosed-empty custody BEFORE recovery/backend normal, dismissal retains failure1/\nseven other normal/private cleanup/no criticals or incomplete teardown. Original\nnormal18829/13/reload18934/12/current-error19022/host1 plus seven normal/old-canceled\n19136/13/rapid19251/17/delayed19318/8/old-success19435/13/full119/new Quint9/200/6\nactual projections pass. Failed142/186 retained. Unretired/uncertain recovery\ncontrols are refused by source; actual uncertain recovery, whole-host restart/\nwindow-command journal/durable Unknown/all delivery-error or process schedules\nremain open. No native settlement from process death/reset/replay; physical/\nhardware/pressure/full S09/release remain open.\n')
p=r/'openspec/changes/warlock-preview-actor-retirement/tasks.md';s=p.read_text();needle='- [ ] Implement/qualify CONTROL-047 actual shared WebKit process stop after current';assert s.count(needle)==1;s=s.replace(needle,'- [x] Implement/qualify CONTROL-047 actual shared WebKit process stop after current')
s+='''
  Bounded GUI143/Native18721 exact186 oracle/full119/Quint9/200/6 actual projections:
  real shared termination reason2/first source pixels/quarantine/strict closed-empty
  native custody BEFORE GTK recovery/backend normal, failure1 after dismissal,
  seven other normal/private cleanup/no criticals. Original normal/reload/current-
  error/old-error/rapid/delayed/success regressions pass. Failed142/186 held.
- [ ] Qualify actual native uncertainty and all asynchronous delivery-error/process
  schedules with original strict-close/refused recovery/no-reset/no-replay gates.
- [ ] Implement/qualify whole-host restart with original window-command journal,
  pending outcomes and durable Unknown preserved; known preview drain before GTK
  recovery does not establish successful shared-host restart or healthy release.
''';p.write_text(s);print(docs/'HANDOFF.md')
