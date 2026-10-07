"""Record bounded known reload evidence; preserve broader original release gates."""
import json,pathlib,resource,sys
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
r=pathlib.Path('/home/hoskinson/omarchy-windows-parity');docs=pathlib.Path(__file__).parent
d=json.loads((docs/'component-report-gui141-known-reload.json').read_text());assert d['passed'] and d['actualKnownRendererReloadQualified'] and not d['reloadRecoveryQualified']
text='''
GUI140 and original Native176 hold the actual same-URI reload counterexample:
real first snapshot/source red19200 and original WebKit reload/LOAD_STARTED
navigation2 pass, but original host continuity fails with failure1 and uncertain
strict teardown refusal. Normal17529/13/full119 pass. Native177 separately holds
an observer filename assertion against the known first snapshot before request2;
its early host termination causes strict teardown refusal/criticals. Fresh184
accepts exactly request1 as pending while retaining request2, all source/current
output/final strict close checks and original six-second observer. Earlier
premature packaging, checkpoint-path, historical build-entry and coupling
closed-command schema failures remain immutable with provenance receipts.

GUI141 is held: known trusted current initialized same-URI LOAD_STARTED removes
renderer authority and urgently quarantines the original realm, keeping original
Native input/step/poll/receipts progressing. Original strict policy/physical/
ticket/journal/confirmation closure and empty custody precede replacement in
the SAME GTK popup/lease1. Fresh DOM/fixed-grant admission opens epoch2 on the
identical policy/binding, navigation3 and original snapshot request2, without
grant/policy/counter/clock reset or Unknown replay. Unexpected URI or uncertain/
failing custody retains the fail-closed branch.

Native18434/12 passes actual reload, first/current red19200 source pixels,
current image before-after original grim opacity0 output, final strict close,
all normal owned exits/private cleanup/no criticals. Original normal17829/13,
canceled-old17936/13, current-error18022/host1 plus seven other normal,
rapid18151/17, delayed18218/8 and old-success18335/13 pass separately. Full119,
new reload Quint9 named/200 samples and7 actual projected stages pass. Exact
source/build/evidence hashes: component-report-gui141-known-reload.json.
CONTROL046 is bounded to this known real reload; arbitrary/repeated/uncertain/
process schedules, durable Unknown recovery and original-clock pressure/expiry
remain open. Native opacity0 stays mandatory; GTK paint is not Wayland/hardware
presentation. Physical conceal/reveal/hardware, full workload/RSS, original
full S09/release/integrated journeys/deployment remain open. Next PUBLIC103,
then actual uncertain/process recovery and pressure/expiry/physical gates.
Installed desktop/drafts/foreign edits remain preserved; full GUI goal active.
'''
p=docs/'HANDOFF.md';s=p.read_text();assert 'GUI141 is held:' not in s;p.write_text(s+text)
p=docs/'NATIVE-ADMISSION-CONTROLS.md';s=p.read_text();marker='Bounded CONTROL-046 known renderer reload: GUI141';assert marker not in s
p.write_text(s+'\n'+marker+' urgently quarantines after actual original\nWebKit LOAD_STARTED/navigation2 and keeps original native progress until strict\nclose/empty custody BEFORE same-popup lease1 replacement/fresh DOM/fixed grant/\nlater epoch2 on original policy/binding/navigation3/request2. Native18434/12\nproves first/current source red19200, original opacity0 grim region and final\nstrict close/all normal exits/private cleanup/no criticals. Original normal178\n29/13, old-canceled17936/13, current-failure18022/host1 plus seven normal, rapid181\n51/17, delayed18218/8 and old-success18335/13 pass. Full119/new Quint9/200/7\nactual projections pass. Original140/176 failure and177 observer failure retained;\nfresh184 corrects only pending-first-record wait, preserving request2/deadline/\npixel/output/strict close gates. This known schedule is qualified; arbitrary/\nrepeated/uncertain/process reload, durable Unknown, physical/hardware/pressure/\nfull S09/release remain open. No reset/replay/inferred native settlement.\n')
p=r/'openspec/changes/warlock-preview-actor-retirement/tasks.md';s=p.read_text();needle='- [ ] Implement/qualify CONTROL-046 actual known same-URI WebKit reload while a';assert s.count(needle)==1;s=s.replace(needle,'- [x] Implement/qualify CONTROL-046 actual known same-URI WebKit reload while a')
s+='''
  Bounded GUI141/Native18434/12/full119/Quint9/200/7 actual projected stages:
  strict old Native close before same-popup lease1 replacement/fresh DOM/later
  epoch2 on identical policy/binding/navigation3/request2; source/current-output
  opacity0/final strict closure/all normal exits/private cleanup/no criticals.
  Separate normal/current-failure/old-error/rapid/delayed/success regressions pass.
  Original140/176 failure and177 premature observer assertion remain held;
  fresh184 waits for request2 under unchanged6 without rejecting known request1.
- [ ] Qualify actual repeated/unexpected navigation, uncertain/process renderer
  recovery and durable Unknown under original clocks/retirement/no-reset/no-replay
  obligations. Known one-reload schedule does not close broader CONTROL-046.
''';p.write_text(s)
print(docs/'HANDOFF.md')
