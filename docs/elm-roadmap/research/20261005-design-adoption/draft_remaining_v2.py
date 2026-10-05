"""Generate corrected research-only release closure; retain the initial draft bytes."""
from pathlib import Path
import collections, copy, hashlib, json, re, shutil
ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
CHANGE = REPO / 'openspec/changes/elm-release-closure'
ARCHIVE = ROOT / 'drafts-v1'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def preserve(source, destination):
    if destination.exists():
        assert source.read_bytes() == destination.read_bytes(), f'Archive differs: {destination}'
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

# Preserve initial registry/script/prose and all initial change files before rewrite.
for name in ['draft_remaining.py', 'remaining-work.json', 'REMAINING-WORK-EARS.md']:
    preserve(ROOT / name, ARCHIVE / name)
archive_change = ARCHIVE / 'openspec/changes/elm-release-closure'
if not archive_change.exists():
    shutil.copytree(CHANGE, archive_change)
# Subsequent runs intentionally do not copy revised change files over the V1 archive.
base_path = ROOT / 'inputs/docs/elm-roadmap/requirements.json'
backlog_path = ROOT / 'inputs/docs/elm-roadmap/delivery/sprint-backlog.json'
work_path = ROOT / 'inputs/docs/elm-roadmap/delivery/FRP-ELM-WORKPLAN.json'
rc_path = ROOT / 'inputs/docs/elm-roadmap/RIGHT-CLICK.md'
base = json.loads(base_path.read_text())['requirements']
byid = {r['id']: r for r in base}
sprints = json.loads(backlog_path.read_text())['sprints']
initial = json.loads((ROOT / 'remaining-work.json').read_text())
work = json.loads(work_path.read_text())
adoption_path = ROOT / 'candidates-v2.json'
adoption = json.loads(adoption_path.read_text())['requirements']
reviews = []
for path in sorted((ROOT / 'consensus').glob('*.votes.json')):
    ballot = json.loads(path.read_text())
    reviews.append({'reviewer': ballot['reviewer'], 'source': str(path.relative_to(ROOT)),
                    'sourceSHA256': digest(path), 'remainingWork': ballot['remainingWork']})
assert len(reviews) == 10
assert len(base) == 242 and sum(len(r['scenarios']) for r in base) == 417
mapping = collections.defaultdict(list)
for sprint in sprints:
    for rid in sprint['items']:
        mapping[rid].append(sprint['id'])
assert set(mapping) == set(byid) and all(len(v) == 1 for v in mapping.values())
coverage = copy.deepcopy(initial['coverage'])
for row in coverage:
    original = byid[row['baselineId']]
    assert row['originalEARS'] == original['ears']
    assert row['originalScenarios'] == original['scenarios']
    assert row['verification'] == original['verification']
    row['originalRequirement'] = copy.deepcopy(original)

rc_text = rc_path.read_text()
rc_blocks = []
heads = list(re.finditer(r'^### Requirement: (ELM-RC-\d{3})[^\n]*\n', rc_text, re.M))
for i, head in enumerate(heads):
    end = heads[i + 1].start() if i + 1 < len(heads) else len(rc_text)
    block = rc_text[head.start():end]
    scenarios = re.findall(r'^#### Scenario: (ELM-RC-[^\n]+)', block, re.M)
    rc_blocks.append({'id': head.group(1), 'originalMarkdown': block,
                      'originalScenarioNames': scenarios, 'source': 'inputs/docs/elm-roadmap/RIGHT-CLICK.md'})
assert len(rc_blocks) == 24 and sum(len(r['originalScenarioNames']) for r in rc_blocks) == 48

# These map qualification obligations, not acceptance or new product scope.
work_packages = {
 'W01': ['S05','S07','S08','S13','S15','S16'],
 'W02': ['S05','S07','S10','S15','S16'],
 'W03': ['S05','S09','S11','S15','S16'],
 'W04': ['S05','S07','S08','S12','S15','S16'],
 'W05': ['S05','S08','S09','S10','S11','S15','S16'],
 'W06': ['S09','S10','S11','S14','S16'],
 'W07': ['S04','S07','S08','S12','S13','S14','S16'],
 'W08': ['S02','S04','S07','S08','S12','S14','S16'],
 'W09': ['S05','S06','S07','S10','S13','S16'],
 'W10': ['S09','S10','S11','S15','S16'],
 'W11': ['S03','S04','S05','S09','S11','S15','S16'],
 'W12': ['S10','S11','S13','S16'],
}
frp_items = []
for item in work['workItems']:
    frp_items.append({'workItem': item['id'], 'originalWorkItem': copy.deepcopy(item),
                     'packages': work_packages[item['id']], 'findingIds': item['findings'],
                     'closureRule': 'Each affected package remains open until relevant finding obligations are independently qualified or explicitly reconciled to accepted exact-tuple evidence; a partial component pass does not close an integration gap.'})
frp_findings = []
for finding in work['findings']:
    frp_findings.append({'findingId': finding['id'], 'workItem': finding['workItem'],
                        'packages': work_packages[finding['workItem']],
                        'originalFinding': copy.deepcopy(finding),
                        'status': 'reconcile existing component evidence; no new acceptance'})
assert len(frp_items) == 12 and len(frp_findings) == 44
assert {f['findingId'] for f in frp_findings} == {f for w in work['workItems'] for f in w['findings']}

adopt_owners = {
 1:'S05',2:'S05',3:'S15',4:'S07',5:'S05',6:'S05',7:'S05',8:'S05',9:'S09',10:'S05',
 11:'S05',12:'S14',13:'S05',14:'S15',15:'S15',16:'S07',17:'S14',18:'S12',19:'S14',20:'S07',
 21:'S10',22:'S05',23:'S10',24:'S02',25:'S05',26:'S11',27:'S09',28:'S09',29:'S07',30:'S12'}
adopt_rows=[]
for i, requirement in enumerate(adoption, 1):
    packages = set([adopt_owners[i]])
    packages.update(mapping[rid][0] for rid in requirement['baselineIds'] if rid in mapping)
    if i in [26,27]: packages.add('S02')
    adopt_rows.append({'id': requirement['id'], 'title': requirement['title'],
        'owningPackage': adopt_owners[i], 'affectedPackages': sorted(packages),
        'baselineIds': requirement['baselineIds'], 'workItems': requirement['workItems'],
        'status': 'deferred-conditional-draft' if i == 15 else 'corrected-draft-refinement; final consensus/selection pending',
        'releaseGating': False,
        'scopeRule': 'No additional release gate or product feature unless separately accepted; existing mapped baseline obligations still govern. Export015 remains deferred and conditional.'})
assert len(adopt_rows) == 30

policy_freeze = [
 {'id':'feedback-quiescence','source':'inputs/docs/elm-roadmap/INTERACTION.md:41', 'obligation':'Freeze numeric feedback and quiescence intervals at P0 before candidate evaluation.'},
 {'id':'interaction-geometry','source':'inputs/docs/elm-roadmap/INTERACTION.md:47', 'obligation':'Freeze measurable contrast, target/focus geometry and supported text scaling/reflow before evaluating results.'},
 {'id':'context-timing-geometry','source':'inputs/docs/elm-roadmap/RIGHT-CLICK.md:172', 'obligation':'Freeze gesture tolerance, hover/submenu timing, bounds and geometry budgets before measuring candidates.'},
 {'id':'workload-matrix','source':'inputs/docs/elm-roadmap/REQUIREMENTS.md:1517', 'obligation':'Freeze applicable numeric absolute/regression budgets, distributions, sample/device/output metadata and exclusions under ELM-QA-021/ELM-REV-020/021.'},
 {'id':'conditional-preview-impact-pacing','source':'candidates-v2.json:ELM-ADOPT-026/027', 'obligation':'If drafts026/027 are separately adopted, freeze presentation-impact and preview-pacing workload rows under S02 before their evaluation; this does not add mandatory release features.'},
]
final_dependencies = {
 'S04':[{'evidencePackage':'S12','baselineIds':['ELM-UI-012','ELM-UX-028'], 'requiredEvidence':'Actual launcher and other applicable shell field IME/native input targets, in addition to minimal-host evidence, qualified on the same release tuple.'}],
 'S07':[{'evidencePackage':'S12','baselineIds':['ELM-UI-010'], 'requiredEvidence':'Settings, notifications and adapter-unavailable native semantic/announcement scenarios on the actual S12 surfaces, on the same release tuple.'},
         {'evidencePackage':'S02','baselineIds':['ELM-UI-015'], 'requiredEvidence':'Frozen numeric feedback and geometry policy before evaluating taskbar reachability/feedback.'}],
 'S11':[{'evidencePackage':'S02','baselineIds':['ELM-UI-017'], 'requiredEvidence':'Frozen quiescence and relevant performance/resource policy before evaluating demand suspension.'}],
 'RC':[{'evidencePackage':'S02','baselineIds':[r['id'] for r in rc_blocks], 'requiredEvidence':'Frozen context gesture, hover/submenu timing, bounds/geometry and feedback policy before amendment measurement.'}],
}

extras = {
 'S02':'Numeric feedback and quiescence intervals, measurable contrast/target/focus/text-reflow policy, gesture tolerance and hover/submenu timing/bounds/geometry budgets are frozen at P0 before candidate evaluation under INTERACTION.md and RIGHT-CLICK.md; applicable workload budgets include units, hardware/output metadata, distributions and reviewed thresholds, with no invented numbers.',
 'S04':'Final release acceptance additionally includes ELM-UI-012/ELM-UX-028 actual-field evidence from S12 on the same release tuple; a minimal-host experiment alone is insufficient.',
 'S05':'Named Quint/fuzz/replay and native rejection of unauthorized stale mutations, automatic Unknown replay and unsafe cancellation pass; authenticated exact historical receipts/reconciliation evidence remain admissible to settle retained Unknown under the declared protocol. Native-to-Elm control delivery continuity, reserved cleanup capacity and diagnostic redaction/canary evidence are qualified; sends and transport admission never imply effects.',
 'S07':'Final release acceptance additionally includes ELM-UI-010 settings/notification/adapter-unavailable scenarios on actual S12 surfaces with single-owner native AT outcome deduplication; S02 feedback/geometry policy is frozen before evaluation.',
 'S09':'All original13 native preview identities/oracles pass with production provider ownership, reader/fence drain and real family/source-stop pixels; source liveness, captured revision and frame freshness are separately verified under the frozen historical/live/unavailable policy. Live source or retained lease alone cannot describe stale pixels as current.',
 'S10':'Original restore38/recovery34 identities, oracles and deadlines, including independent case-34 time origin and late-completion failure, remain required; physical handoff/normal retirement use exact native evidence.',
 'S11':'S02 quiescence and applicable capture/presentation/resource policy is frozen before evaluation; production ownership and physical drain are not established by fallback labels.',
 'S14':'The inherited drag/resize52 campaign retains all original identities, input/pixel/geometry oracles and original deadlines; actual application recipients, keyboard/AT/IME and representative generic application cases require exact native receipts.',
 'S15':'Authenticated historical settlement, retained Unknown/replay floors, storage-full/interrupted migration and normal owned-process drain are reconciled on the coherent tuple; no restart replays mutations or renews deadlines.',
 'S16':'All applicable original gates, including native preview13, restore38/recovery34 and drag/resize52 with their original identities/oracles/deadlines, pass on one coherent reversible release tuple. Unfinished provider integration, failed or unobserved obligations cannot be relabeled complete.',
}
contracts = copy.deepcopy(initial['closureRequirements'])
for contract in contracts:
    sid=contract['package']
    contract['buildDependsOn']=copy.deepcopy(contract['dependsOn'])
    contract['finalAcceptanceDependencies']=copy.deepcopy(final_dependencies.get(sid,[]))
    contract['frpWorkItems']=[w['workItem'] for w in frp_items if sid in w['packages']]
    contract['frpFindingIds']=[f['findingId'] for f in frp_findings if sid in f['packages']]
    contract['draftAdoptionIds']=[r['id'] for r in adopt_rows if sid in r['affectedPackages']]
    if sid=='S05': contract['gate']=extras[sid]
    elif sid in extras: contract['gate']=contract['gate']+' '+extras[sid]
    if sid=='RC':
        contract['gate']='All24 separate ELM-RC amendment requirements and all48 original scenarios pass independently with native targeting, keyboard/focus, refusal and AT evidence; application client menus and Files semantics remain preserved. S02 numeric gesture, hover/submenu timing and geometry/feedback policy is frozen before measurement.'
        contract['amendmentIds']=[r['id'] for r in rc_blocks]
        contract['baselineIds']=[]
        contract['amendmentCounts']={'requirements':24,'scenarios':48}
    prefix='WHERE compositor replacement is selected, ' if contract['conditional'] else ''
    rule=f"{prefix}WHEN {sid} qualification is submitted, the release verifier SHALL keep {sid} open until the following package-specific gate is independently satisfied with exact requirement/scenario identities and original oracles/deadlines on the coherent source/runtime/ABI release tuple: {contract['gate']}"
    rule+=' The verifier SHALL also retain all linked baseline/amendment evidence, final cross-surface acceptance evidence and relevant FRP finding dispositions; failed, unobserved or lower-level substitute evidence SHALL NOT close the package.'
    contract['ears']=rule
    contract['gateNormative']=True
    contract['status']='corrected draft; implementation and native/full-release acceptance pending'
    contract['scenarios'][0]['then']='The normative '+sid+' gate above and every linked original oracle pass with exact tuple/deadlines; cross-surface final evidence and relevant FRP findings are independently reconciled, and only then may the package close.'
    contract['scenarios'][1]['then']='Closure is refused and failed/missing obligations remain explicit; component passes, build readiness and draft adoption advice cannot substitute for the normative package gate, original scenarios or deadlines.'

registry={'schema':2,'status':'corrected research draft; no baseline or native/full-release acceptance changed',
 'baselineCounts':{'requirements':242,'scenarios':417}, 'mandatoryCounts':{'requirements':230,'scenarios':405},
 'conditionalCompositorCounts':{'requirements':12,'scenarios':12},
 'amendmentCounts':{'requirements':24,'scenarios':48,'separateFromBaseline':True},
 'sourceHashes':{str(x.relative_to(ROOT)):digest(x) for x in [base_path,backlog_path,work_path,rc_path,adoption_path]},
 'initialDraftSHA256':digest(ROOT/'remaining-work.json'), 'coverage':coverage,
 'rightClick':{'counts':{'requirements':24,'scenarios':48},'separateFromBaseline':True,'requirements':rc_blocks},
 'closureRequirements':contracts,'policyFreezeObligations':policy_freeze,
 'dependencySemantics':{'build':'buildDependsOn preserves frozen sequencing and cannot be reordered by research advice.',
 'finalAcceptance':'Cross-package evidence dependencies refer to actual-surface qualification on a common release tuple, not recursive package build/closure prerequisites. Early experiments/build milestones may finish while final acceptance remains open; S04/S07 requiring S12 evidence does not introduce a cyclic build schedule.'},
 'frpWorkItemCrosswalk':frp_items,'frpFindingCrosswalk':frp_findings,'adoptionPackageCrosswalk':adopt_rows,
 'reviewerCorrections':reviews,
 'scope':'Generic representative compatibility only; no removed named-app repair targets. S01-S16 mandatory; C00-C06 conditional. All original13/38/34/52 campaign identities/oracles/deadlines remain unchanged; right-click24/48 additive; export015 deferred; no new implementation or acceptance claims.'}
(ROOT/'remaining-work-v2.json').write_text(json.dumps(registry,indent=2)+'\n')

lines=['# Remaining release work — corrected EARS V2','','This is a research draft for release closure, not a missing-feature inventory or acceptance report. Reconcile existing component evidence before assigning implementation. The frozen baseline242 requirements/417 scenarios are copied verbatim; mandatory S01–S16 account for230/405 and conditional C00–C06 for12/12. The separate right-click amendment retains24 requirements/48 scenarios. The24 closure requirements below add no product features and remain unchecked. V1 bytes and its OpenSpec tree are preserved under drafts-v1.','','Each Gate column is a **normative package-specific closure outcome**, incorporated verbatim into its EARS requirement. Original IDs, complete requirement records, scenario objects and verification oracles remain unchanged in remaining-work-v2.json. Source, CPU, model, replay, native, hardware and AT evidence remain distinct. Production provider/full GUI drain remains unqualified until actual evidence establishes it. Original preview13, restore38/recovery34, case-34 and drag/resize52 identities/oracles/deadlines remain required.','','## Package gates','','| Package | Normative gate | Baseline counts or separate amendment |','| --- | --- | --- |']
for c in contracts:
    sid=c['package']; count='24 / 48 (separate amendment)' if sid=='RC' else f"{len(c['baselineIds'])} / {sum(len(byid[r]['scenarios']) for r in c['baselineIds'])}"+(' (conditional)' if c['conditional'] else '')
    lines.append(f"| {sid} | {c['gate']} | {count} |")
lines+=['','## Policy freezing before evaluation','']
for row in policy_freeze:lines.append(f"- {row['id']}: {row['obligation']} Source: `{row['source']}`.")
lines+=['','## Build and final acceptance dependencies','','Frozen build sequencing remains unchanged. Final evidence dependencies below refer to actual surface/field qualification, not recursive package closure or a new build graph. An early S04/S07 host/build experiment may finish while final release acceptance stays open pending S12 evidence on the same tuple.','','| Owning package | Evidence package | Original requirements | Final acceptance evidence |','| --- | --- | --- | --- |']
for sid,deps in final_dependencies.items():
    for dep in deps:lines.append(f"| {sid} | {dep['evidencePackage']} | {', '.join(dep['baselineIds'])} | {dep['requiredEvidence']} |")
lines+=['','## Existing FRP work and all44 findings','','Every relevant finding is a closure obligation until independently qualified or reconciled to accepted exact-tuple evidence. Partial component passes remain partial. These mappings preserve all12 W-items and their original44 findings; they add no baseline IDs.','','| Work item | Affected closure packages | Finding IDs |','| --- | --- | --- |']
for w in frp_items:lines.append(f"| {w['workItem']} — {w['originalWorkItem']['title']} | {', '.join(w['packages'])} | {', '.join(w['findingIds'])} |")
lines+=['','## All30 adoption drafts','','Each adoption remains a draft refinement and adds no release gate unless separately accepted. Existing baseline obligations already govern where mapped. ELM-ADOPT-015 is explicitly conditional and deferred. Candidates026/027 only add S02 presentation-impact/preview-pacing measurement rows if separately adopted; they create no mandatory release feature.','','| Adoption | Owning package | Affected packages | Status |','| --- | --- | --- | --- |']
for row in adopt_rows:lines.append(f"| {row['id']} | {row['owningPackage']} | {', '.join(row['affectedPackages'])} | {row['status']} |")
for c in contracts:
    lines+=['',f"## {c['id']}",'',c['ears'],'','Original mapping: '+(', '.join(c['baselineIds']) or 'Separate ELM-RC-001–024 /48 original scenarios.'),'','Build dependencies: '+(', '.join(c['buildDependsOn']) or 'none')+'. Final evidence dependencies: '+(', '.join(d['evidencePackage'] for d in c['finalAcceptanceDependencies']) or 'none additional')+'.','', 'Relevant FRP items: '+(', '.join(c['frpWorkItems']) or 'none')+'. Findings: '+(', '.join(c['frpFindingIds']) or 'none')+'.']
(ROOT/'REMAINING-WORK-EARS-V2.md').write_text('\n'.join(lines)+'\n')

spec=CHANGE/'specs/elm-verification/spec.md'
spec.write_text('# Release closure evidence\n\n## Purpose\n\nDefines normative package-specific closure outcomes for the unchanged baseline242/417 and separate right-click24/48. This corrected research draft does not claim implementation or acceptance. Build dependencies are distinct from final actual-surface evidence dependencies. Original preview13, restore38/recovery34, drag/resize52 and all original deadlines/oracles remain required.\n\n## ADDED Requirements\n\n'+'\n'.join(f"### Requirement: {c['id']}\n\n{c['ears']}\n\n"+'\n'.join(f"#### Scenario: {c['id']} {s['name']}\n\n- GIVEN {s['given']}\n- WHEN {s['when']}\n- THEN {s['then']}\n" for s in c['scenarios']) for c in contracts))
(CHANGE/'proposal.md').write_text('''# Make remaining release closure explicit

## Why

Component evidence does not establish completion of each original release gate on a coherent tuple. Initial reviewer ballots identified missing normative package outcomes, policy freezing and cross-surface closure dependencies.

## What Changes

Refine24 draft closure requirements for S01–S16, conditional C00–C06 and separate right-click24/48. Preserve baseline242/417 exactly, original preview13/restore38/recovery34/dragresize52 and all identities/oracles/deadlines. Include normative package gates, S02 numeric policy freezes, final actual-field/surface acceptance dependencies, all12 FRP W-items/all44 findings and all30 adoption owning-package mappings. Adoption drafts add no gate unless separately accepted; export015 remains deferred.

## Capabilities

### New Capabilities

- `elm-verification`: additive closure refinements under the existing in-flight draft capability. Merge with the baseline draft before archive; no promoted main spec is overwritten.

### Modified Capabilities

None: no archived main spec is changed.

## Impact

Research release ledger and qualification planning only. No runtime implementation, installed configuration, session or baseline registry changes. The exact registry is docs/elm-roadmap/research/20261005-design-adoption/remaining-work-v2.json; initial draft bytes are retained under drafts-v1.
''')
(CHANGE/'design.md').write_text('''# Release closure design

Use remaining-work-v2.json and REMAINING-WORK-EARS-V2.md as the corrected research-only ledger. Every frozen requirement retains its exact EARS, original scenarios and full original record. Each normative package-specific gate is in its EARS, not only a table. All implementation and acceptance remain pending; existing component evidence must be reconciled before assigning work.

Mandatory S01–S16 remains separate from conditional compositor C00–C06 and separate right-click24/48. Preserve original preview13, restore38/recovery34 and independent case-34 time origin/deadline, and drag/resize52 with original identities and oracles. No removed named-application repair scope returns.

Build dependencies remain the frozen sequence. Final acceptance requires actual-surface evidence even when the source requirement lives in an earlier package: S07 ELM-UI-010 needs S12 settings/notifications/unavailable-adapter evidence; S04 ELM-UI-012/ELM-UX-028 needs S12 actual-field IME/native input target evidence. These are same-tuple evidence links, not cyclic recursive build or closure prerequisites. Early experimental host milestones can finish while final acceptance remains open.

S02 freezes numeric feedback/quiescence, contrast/target/focus/text-reflow, gesture/hover/submenu timing and bounds/geometry policy before candidate evaluation. S07, S11 and RC explicitly depend on these frozen policies. Conditional adoption026/027 presentation-impact and preview-pacing workload rows belong to S02 if separately adopted, without adding mandatory product scope.

S05 rejects unauthorized stale mutations and automatic Unknown replay while admitting authenticated exact historical receipts through declared reconciliation. S09 distinguishes source liveness, captured revision and frame freshness under unchanged historical/live/unavailable oracles; retained authority and live source do not make old pixels current. Production provider, source-stop/family fidelity and physical drain still need native qualification.

All12 FRP W-items and44 findings are crosswalked to affected package gates. Relevant open obligations block closure until independently qualified or reconciled to accepted exact-tuple evidence; bounded component results cannot substitute for integration. All30 adoption drafts have owning/affected packages but add no release gates without separate acceptance; export015 remains deferred.

Preserve source/runtime/ABI lineage and separate model/CPU/replay/native/hardware/AT evidence. Native campaigns use the protected serialized launcher, owning ABI, original clocks and ordered normal cleanup. Numeric budgets are measured and frozen, not invented. No archive/promotion or main-session activation occurs in this research change; a coherent reversible release and authorized activation retain their existing gates.
''')
tasks=['# Remaining implementation and qualification work','','All checkboxes remain unchecked. Reconcile component evidence; no draft marks native/full release complete.','']
for c in contracts:tasks.append(f"- [ ] {c['id']}: independently qualify its normative gate and all original evidence, relevant FRP findings and final cross-surface dependencies. Gate: {c['gate']}")
for w in frp_items:tasks.append(f"- [ ] {w['workItem']}: reconcile/qualify findings {', '.join(w['findingIds'])} for packages {', '.join(w['packages'])}; preserve original evidence levels and deadlines.")
tasks+=['- [ ] Reconcile each adoption draft with its owning package before any separate acceptance; export015 remains conditional and deferred.']
(CHANGE/'tasks.md').write_text('\n'.join(tasks)+'\n')
print(json.dumps({'baselineRequirements':len(coverage),'baselineScenarios':sum(len(r['originalScenarios']) for r in coverage),'separateRCRequirements':len(rc_blocks),'separateRCScenarios':sum(len(r['originalScenarioNames']) for r in rc_blocks),'closureRequirements':len(contracts),'closureScenarios':sum(len(c['scenarios']) for c in contracts),'frpWorkItems':len(frp_items),'frpFindings':len(frp_findings),'adoptionDrafts':len(adopt_rows),'reviewerBallots':len(reviews),'change':str(CHANGE)}))
