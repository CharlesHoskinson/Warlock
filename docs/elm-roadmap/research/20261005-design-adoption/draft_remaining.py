"""Draft additive release closure contracts without changing frozen requirements."""
from pathlib import Path
import collections,hashlib,json,re
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[3]
assert (REPO/'AGENTS.md').exists()
base=json.loads((ROOT/'inputs/docs/elm-roadmap/requirements.json').read_text())['requirements'];byid={r['id']:r for r in base}
backlog=json.loads((ROOT/'inputs/docs/elm-roadmap/delivery/sprint-backlog.json').read_text());sprints=backlog['sprints']
assert len(base)==242 and sum(len(r['scenarios']) for r in base)==417
mapping=collections.defaultdict(list)
for s in sprints:
 for rid in s['items']:mapping[rid].append(s['id'])
assert set(mapping)==set(byid) and all(len(v)==1 for v in mapping.values())
index=[]
for r in base:
 index.append({'baselineId':r['id'],'package':mapping[r['id']][0],'capability':r['capability'],'originalEARS':r['ears'],'originalScenarios':r['scenarios'],'ownerRole':r['accountableOwnerRole'],'verification':r['verification'],'acceptanceStatus':'unresolved-release-closure; reconcile component evidence before implementation','draftClosureId':'ELM-CLOSE-'+mapping[r['id']][0],'conditional':mapping[r['id']][0].startswith('C'),'source':'inputs/docs/elm-roadmap/requirements.json'})
contracts=[]
for s in sprints:
 gate=s['exitGate']
 if s['id']=='S06':gate='Generic eligibility/layering, genuine blocker/no-focus and workspace races pass with independent pixels, input recipients and focus receipts.'
 conditional=s['id'].startswith('C')
 sid=s['id'];ears=(f'WHERE compositor replacement is selected, WHEN {sid} qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved applicable gate.' if conditional else f'WHEN {sid} qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved gate.')
 contracts.append({'id':'ELM-CLOSE-'+sid,'title':s['title'],'capability':'elm-verification','ears':ears,'pattern':'complex' if conditional else 'event-driven','baselineIds':s['items'],'package':sid,'classification':'release-closure-refinement','conditional':conditional,'gate':gate,'dependsOn':s.get('dependsOn',[]),'ownerRole':'Release integration lead','verifierRole':'Independent acceptance reviewer','status':'draft; implementation and acceptance pending','scenarios':[{'name':'exact-evidence','given':f'a candidate submitted for {sid}'+(' after an explicit compositor go decision' if conditional else ''),'when':'the verifier reviews all applicable linked requirements and their original scenarios','then':'the gate ledger records exact source/runtime/ABI identity, original deadlines, independent required observations and each disposition; only complete accepted evidence permits closure'},{'name':'missing-or-substituted-evidence','given':f'a {sid} candidate with a failed native case, absent required evidence or only a lower-level component pass','when':'package closure is requested','then':'closure is refused; missing/failed evidence and the next qualifying action remain explicit without changing original scenarios or deadlines'}]})
contracts.append({'id':'ELM-CLOSE-RC','title':'Right-click amendment closure','capability':'elm-verification','ears':'WHEN right-click release qualification is submitted, the release verifier SHALL retain the amendment identities and native targeting, keyboard, focus, refusal and accessibility evidence before closing the amendment.','pattern':'event-driven','baselineIds':[],'package':'RC','classification':'release-closure-refinement','conditional':False,'gate':'All24 ELM-RC amendment identities and their scenarios remain additive and independently qualified; native application client menus and Files semantics remain preserved.','dependsOn':['S05','S08','S12','S14'],'ownerRole':'Desktop experience lead','verifierRole':'Independent acceptance reviewer','status':'draft; implementation and acceptance pending','scenarios':[{'name':'identity-safe-menu','given':'a context menu for an authenticated current target and publication','when':'pointer and keyboard actions and supported disabled states are qualified','then':'native recipients, outcome receipts, focus/dismissal and AT observations match the24 frozen amendment identities'},{'name':'stale-menu-or-unsupported-action','given':'a target is replaced, output changes or an action is unavailable while the menu is open','when':'the user requests that action','then':'the native action is refused or safely revalidated under the existing contract and the menu cannot retarget a different window'}]})
registry={'schema':1,'status':'draft; no baseline acceptance changed','baselineCounts':{'requirements':242,'scenarios':417},'sourceHashes':{p:hashlib.sha256((ROOT/'inputs'/p).read_bytes()).hexdigest() for p in ['docs/elm-roadmap/requirements.json','docs/elm-roadmap/delivery/sprint-backlog.json']},'coverage':index,'closureRequirements':contracts,'rightClick':'Existing24 additive identities retained separately; no baseline inflation.','scope':'Generic compatibility; no named Brave/Heroic repair targets; compositor optional.'}
(ROOT/'remaining-work.json').write_text(json.dumps(registry,indent=2)+'\n')
lines=['# Remaining release work — EARS draft','','This audits release closure, not whether every behavior is missing. Component evidence exists; this inventory makes no new acceptance decision. The frozen242 requirements/417 scenarios are copied verbatim into remaining-work.json and mapped exactly once to S01–S16 or conditional C00–C06. Existing right-click24 remains separate. Reconcile accepted component evidence before assigning implementation work.','','The canonical baseline and its existing OpenSpec deltas remain authoritative. These24 additive closure requirements name the release evidence still needed; they do not replace the baseline or create24 new product features. All tasks remain open.','','| Package | Remaining release outcome | Gate | Baseline requirements / scenarios |','| --- | --- | --- | --- |']
for c in contracts:
 n=sum(len(byid[r]['scenarios']) for r in c['baselineIds']);lines.append(f"| {c['package']} | {c['title']} | {c['gate']} | {len(c['baselineIds'])} / {n}"+(' (conditional)' if c['conditional'] else '')+' |')
for c in contracts:lines+=['',f"## {c['id']}",'',c['ears'],'','Requirement mapping: '+(', '.join(c['baselineIds']) or 'Existing ELM-RC-001–024 amendment.')]
(ROOT/'REMAINING-WORK-EARS.md').write_text('\n'.join(lines)+'\n')
change=REPO/'openspec/changes/elm-release-closure';spec=change/'specs/elm-verification';spec.mkdir(parents=True,exist_ok=True)
(spec/'spec.md').write_text('# Release closure evidence\n\n## Purpose\n\nDefines traceable evidence and refusal of premature closure for the existing Elm desktop release packages and additive context-menu contract.\n\n## ADDED Requirements\n\n'+'\n'.join(f"### Requirement: {c['id']}\n\n{c['ears']}\n\n"+'\n'.join(f"#### Scenario: {c['id']} {s['name']}\n\n- GIVEN {s['given']}\n- WHEN {s['when']}\n- THEN {s['then']}\n" for s in c['scenarios']) for c in contracts))
(change/'proposal.md').write_text('''# Make remaining release closure explicit

## Why

Component evidence and changing implementation lanes do not show which original release obligations have been accepted together. The user requested an inventory and EARS/OpenSpec drafts of the remaining work.

## What Changes

Add24 release-evidence closure obligations for S01–S16, conditional C00–C06 and the existing right-click amendment. Preserve all242 requirements/417 scenarios, original deadlines, scope amendment, evidence levels and current component results. These are draft acceptance refinements, not missing-feature counts.

## Capabilities

### New Capabilities

- `elm-verification`: additive requirements under the same capability path as the in-flight elm-desktop-pivot draft. There are no promoted main specs; this change must be merged with the existing draft before archive. It does not introduce a second verifier or overwrite baseline requirements.

### Modified Capabilities

None: no archived main spec is changed.

## Impact

Release ledger, package acceptance and test planning only. No installed desktop, source implementation or baseline registry changes. The full exact mapping is in docs/elm-roadmap/research/20261005-design-adoption/remaining-work.json.
''')
(change/'design.md').write_text('''# Release closure design

Read the research inventory and canonical remaining-work.json. Match each frozen baseline requirement exactly once to its existing work package. Preserve its EARS text, all scenarios and evidence oracle. Reconcile newer component evidence against the latest lane checkpoint without inferring a running process from old labels. Every package stays open until its required evidence has been independently accepted on the coherent release tuple.

Mandatory shell S01–S16 remains separate from optional compositor C00–C06. The right-click amendment is additional. Generic representative compatibility remains; named Brave/Heroic-specific repair tasks were removed by user scope amendment. Historical records are retained unchanged.

All native campaigns use the existing serialized protected launcher, owning ABI, original clocks and ordered normal cleanup. Model/CPU/browser-load results never substitute for native output presentation, hardware or AT/IME. Measure and freeze missing numeric budgets before admission; do not guess universal latency thresholds from literature.

Research advice is integrated in a separate additive change after ten-reviewer voting. Neither change may be archived/promoted until implemented and qualified. Build accepted assets and rollback artifacts before any final session-activation approval; do not restart the main compositor or close drafts incidentally.
''')
(change/'tasks.md').write_text('# Remaining implementation and qualification work\n\nAll checkboxes intentionally remain unchecked. Source-only and component passes require reconciliation before reuse. Follow existing dependencies and original acceptance oracles.\n\n'+'\n'.join(f"- [ ] {c['id']}: reconcile existing evidence; finish and independently qualify {c['title'].lower()}. Gate: {c['gate']}" for c in contracts)+'\n')
print(json.dumps({'baselineRequirements':len(index),'baselineScenarios':sum(len(r['originalScenarios']) for r in index),'closureDrafts':len(contracts),'draftScenarios':sum(len(c['scenarios']) for c in contracts),'change':str(change)}))
