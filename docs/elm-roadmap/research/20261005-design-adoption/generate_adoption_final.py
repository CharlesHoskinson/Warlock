#!/usr/bin/env python3
"""Generate draft adoption documentation from the hash-bound v3 ballot.

This is documentation generation, not runtime validation or native acceptance.
No archived baseline or in-flight implementation is modified.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

PACKET = Path(__file__).resolve().parent
REPO = PACKET.parents[3]
BALLOT = PACKET / "candidates-v3.json"
CHANGE = REPO / "openspec/changes/elm-design-adoption"
BASE_WORK = PACKET / "inputs/docs/elm-roadmap/delivery/FRP-ELM-WORKPLAN.json"
NOTICE = (
    "Consensus research drafts ready for internal specification integration and implementation. A reviewed baseline "
    "amendment remains a separate integration step. These artifacts do not change the canonical 242 requirements/417 scenarios, "
    "S01–S16, right-click24, original13 native preview cases, restore38/recovery34/drag-resize52 "
    "or original deadlines. Native authority and no automatic replay of Unknown remain "
    "mandatory. C00–C06 compositor replacement remains conditional."
)
EVIDENCE = (
    "No new native, hardware, IME, AT or full-release evidence is supplied by this packet. "
    "Frozen component/model/CPU/compiled replay evidence is not production-provider or "
    "full GUI ownership/drain/fidelity acceptance. GUI814 and toolkit391 retain separate "
    "owning ABI pairs. Implementation and qualification tasks remain unchecked."
)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def dump(path: Path, value: object) -> None:
    write(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def links(values: list[str]) -> str:
    return ", ".join(values) or "None"


def requirement_md(r: dict, spec: bool = False) -> str:
    heading = "### Requirement:" if spec else "##"
    lines = [f"{heading} {r['id']} — {r['title']}", "", r["ears"], ""]
    lines += [
        f"Status: {r['status']}. Classification: {r['classification']}; original research classification: {r['sourceClassification']}. Priority: {r['priority']}.",
        "", f"Baseline mapping: {links(r['baselineIds'])}.", "",
        f"Existing work mapping: {links(r['workItems'])}.", "",
        f"Source proposals: {links(r['sourceProposals'])}.", "",
        f"Owner: {r['ownerRole']}. Verifier: {r['verifierRole']}.", "",
        f"Guardrails: {r['guardrails']}", "", f"Tradeoffs: {r['tradeoffs']}", "",
    ]
    if r["id"] == "ELM-ADOPT-004":
        lines += ["Adoption gate: enable caching only after profiling demonstrates measured benefit within the existing frozen budgets; otherwise preserve uncached derivation. This is a conditional implementation option, not a mandatory cache feature.", ""]
    if r["id"] == "ELM-ADOPT-015":
        lines += ["Disposition: deferred conditional export. This adds no mandatory release blocker. Product selection, destination/privacy policy and measured budgets require separate review before implementation.", ""]
    if r["id"] == "ELM-ADOPT-029":
        lines += ["Ordering gate: preserve existing P5 keyboard qualification. Earlier feasibility investigation does not promote implementation into the immediate W07/P0 lane.", ""]
    lines += ["Primary sources:", ""]
    lines += [f"- <{url}>" for url in r["sources"]]
    lines += [""]
    for scenario in r["scenarios"]:
        lines += [f"#### Scenario: {r['id']} {scenario['name']}", "",
                  f"- **GIVEN** {scenario['given']}",
                  f"- **WHEN** {scenario['when']}",
                  f"- **THEN** {scenario['then']}", ""]
    return "\n".join(lines)


def main() -> None:
    raw = BALLOT.read_bytes()
    ballot = json.loads(raw)
    sha = hashlib.sha256(raw).hexdigest()
    original = ballot["requirements"]
    assert len(original) == 30
    assert sum(len(r["scenarios"]) for r in original) == 67
    assert len(ballot["proposalDispositions"]) == 53
    assert len(ballot["reports"]) == 10
    reqs = []
    for row in original:
        r = dict(row)
        r["sourceClassification"] = row["classification"]
        r["classification"] = "deferred-conditional-export" if row["id"] == "ELM-ADOPT-015" else "draft-refinement"
        r["status"] = "deferred-conditional-draft" if row["id"] == "ELM-ADOPT-015" else "consensus-draft-implementation-and-qualification-open"
        r["implementationComplete"] = False
        r["nativeAccepted"] = False
        reqs.append(r)
    registry = dict(
        schema=1, status="consensus-drafts-implementation-and-qualification-open",
        sourceBallot="candidates-v3.json", sourceBallotSHA256=sha,
        requirementCount=30, scenarioCount=67, draftRefinementCount=29,
        deferredConditionalExportCount=1, preserve=ballot["preserve"],
        requirements=reqs, proposalDispositions=ballot["proposalDispositions"],
        reports=ballot["reports"], originalSolCandidates=ballot["originalSolCandidates"],
        opusProposalHeadings=ballot["opusProposalHeadings"],
        coordinatorCorrections=ballot["coordinatorCorrections"], corrections=ballot["corrections"],
        baselineAmended=False, nativeAccepted=False, fullReleaseAccepted=False,
        implementationComplete=False, scope=NOTICE, evidenceLimitations=EVIDENCE,
    )
    dump(PACKET / "requirements.json", registry)
    doc = ["# Design adoption — EARS draft registry", "", NOTICE, "", EVIDENCE, "",
           "30 requirements /67 scenarios:29 draft refinements and015 deferred conditional export. Normative EARS, scenario names and GIVEN/WHEN/THEN text below are copied exactly from the v3 ballot. Source duplicate classifications remain recorded separately; they do not inflate baseline scope.", "",
           f"Source: [immutable v3 ballot](candidates-v3.json), SHA256 `{sha}`. [Machine registry](requirements.json) preserves all53 proposal dispositions and10 report provenance entries. The [workplan](WORKPLAN.md) routes work through existing W01–W12; no implementation is completed.", ""]
    for r in reqs:
        doc += [requirement_md(r)]
    write(PACKET / "ADOPTION-EARS.md", "\n".join(doc))

    frozen_work = json.loads(BASE_WORK.read_text())
    items = []
    for source in frozen_work["workItems"]:
        item = dict(source)
        item["sourceStatus"] = source.get("status")
        item["status"] = "draft-implementation-and-qualification-open"
        item["implementationComplete"] = False
        item["candidateIds"] = [r["id"] for r in reqs if source["id"] in r["workItems"]]
        items.append(item)
    assert {i["id"] for i in items} == {f"W{i:02}" for i in range(1, 13)}
    mappings = []
    for r in reqs:
        ws = [w for w in r["workItems"] if w.startswith("W")]
        assert ws
        mappings.append(dict(
            id=r["id"], title=r["title"], status=r["status"], classification=r["classification"],
            priority=r["priority"], baselineIds=r["baselineIds"], workItems=ws,
            originalWorkItems=r["workItems"], baselineTaskReferences=[w for w in r["workItems"] if not w.startswith("W")],
            dependsOn=sorted({d for i in items if i["id"] in ws for d in i.get("dependsOn", [])}),
            guardrails=r["guardrails"], implementationComplete=False, nativeAccepted=False,
            adoptionGate=("after-measured-benefit-within-frozen-budgets" if r["id"] == "ELM-ADOPT-004" else
                          "deferred-product-selection-and-privacy-destination-budget-review" if r["id"] == "ELM-ADOPT-015" else
                          "existing-P5-early-feasibility-only-before-P5" if r["id"] == "ELM-ADOPT-029" else
                          "internal-specification-integration-under-existing-user-authorization"),
        ))
    order = [
        "Preserve immediate integration priority: W07 input identity/focus, then coordinated W01/W02 transport and durable liveness; W03 preview may advance independently on its owning lane.",
        "W07 and W01 share paths and integrate serially; all native campaigns remain serialized through the unchanged protected launcher with the owning ABI.",
        "Preserve every frozen W01–W12 dependsOn edge; candidate P0 labels do not remove those prerequisites or reprioritize inherited sprint phases.",
        "ELM-ADOPT-029 remains existing P5 native keyboard qualification; only feasibility inspection may precede it. Do not treat its W07 mapping as immediate implementation authorization.",
        "ELM-ADOPT-004 remains conditional after profiling and measured benefit inside frozen budgets. Uncached behavior is valid when no benefit is demonstrated.",
        "ELM-ADOPT-015 remains deferred conditional new export behavior; it is not a mandatory shell-release blocker.",
        "W12 additionally retains original S10 native restore/fault/deadline prerequisites and W05/W06 dependencies.",
    ]
    work = dict(schema=1, status="draft-not-executed", sourceBallotSHA256=sha,
                sourceWorkplan="inputs/docs/elm-roadmap/delivery/FRP-ELM-WORKPLAN.json",
                sourceWorkplanSHA256=hashlib.sha256(BASE_WORK.read_bytes()).hexdigest(),
                preserve=ballot["preserve"], orderingConstraints=order, workItems=items,
                candidateMappings=mappings, nativeAccepted=False, fullReleaseAccepted=False,
                implementationComplete=False, baselineAmended=False)
    dump(PACKET / "WORKPLAN.json", work)
    wm = ["# Design adoption — additive workplan draft", "", NOTICE, "", EVIDENCE, "",
          "This plan refines the existing W01–W12 ledger; it neither replaces the earlier44 findings/12 tasks nor treats component checkpoints as wholly missing implementation. Reconcile existing accepted evidence before assigning work. All30 candidates are mapped below, retaining baseline task references where present.", "",
          "## Integration order", ""] + [f"- {o}" for o in order] + ["", "## Existing work items", "",
          "| Work | Existing dependency edges | Candidate drafts | Implementation |", "| --- | --- | --- | --- |"]
    for item in items:
        wm += [f"| {item['id']} — {item['title']} | {links(item.get('dependsOn', []))} | {links(item['candidateIds'])} | Open; reconcile component evidence |"]
    wm += ["", "## Candidate routing and tasks", ""]
    for m in mappings:
        wm += [f"### {m['id']} — {m['title']}", "",
               f"Status: {m['status']}. Existing work: {links(m['workItems'])}. Existing priority: {m['priority']}.", "",
               f"Baseline: {links(m['baselineIds'])}. Baseline task references: {links(m['baselineTaskReferences'])}.", "",
               f"Inherited prerequisites: {links(m['dependsOn'])}. Adoption gate: {m['adoptionGate']}.", "",
               f"Guardrails: {m['guardrails']}", "",
               "- [ ] Reconcile frozen component evidence and resolve the observable contract before implementation.",
               "- [ ] Implement only within the existing lane and prerequisite order after internal specification integration under existing user authorization.",
               "- [ ] Qualify exact scenario identities with model/CPU/compiled evidence and separate required native/hardware/IME/AT receipts, preserving original deadlines and frozen budgets.", ""]
    wm += ["[Machine workplan](WORKPLAN.json) preserves all existing dependency edges and per-candidate traceability. [Requirement registry](requirements.json) preserves research provenance. No selected contract is accepted native behavior.", ""]
    write(PACKET / "WORKPLAN.md", "\n".join(wm))

    grouped = defaultdict(list)
    for r in reqs:
        grouped[r["capability"]].append(r)
    for capability, rows in sorted(grouped.items()):
        sm = [f"# {capability} — design adoption draft", "", "## Purpose", "",
              f"Draft refinements for the existing in-flight `{capability}` capability. This change contains ADDED research contracts only; it does not create or archive a main spec, replace existing pivot/right-click deltas, or establish release acceptance.", "",
              NOTICE, "", EVIDENCE, "", "## ADDED Requirements", ""]
        sm += [requirement_md(r, spec=True) for r in rows]
        write(CHANGE / "specs" / capability / "spec.md", "\n".join(sm))
    write(CHANGE / ".openspec.yaml", "schema: spec-driven\ncreated: 2026-10-05\n")
    write(CHANGE / "proposal.md", "\n".join([
        "# Design adoption research refinements", "", "## Why", "",
        "The frozen design and ten independent research reviews expose sharper contracts for typed boundaries, replay, ownership, cancellation, recovery, accessibility and measured presentation. Component evidence does not qualify production integration. This consensus draft makes the reviewed candidates concrete and traceable without asserting they are implemented.", "",
        "## What Changes", "", "- Add30 candidate EARS contracts and67 exact scenarios across the in-flight capabilities.",
        "- Record29 draft refinements and015 deferred conditional export, with guardrails, tradeoffs, sources and existing baseline/work-item mappings.",
        "- Preserve53 proposal dispositions and10 report provenance entries in the machine registry and immutable v3 ballot.", "",
        "## Capabilities", "", "### New Capabilities", ""] +
        [f"- `{capability}`: ADDED draft requirements within its existing in-flight change; no main-spec archive." for capability in sorted(grouped)] +
        ["", "### Modified Capabilities", "", "None: no archived main specs exist for these in-flight capabilities.", "", "## Impact", "", NOTICE, "", EVIDENCE, "",
         "Ratification of research text is distinct from a separate reviewed baseline amendment, implementation, native acceptance and deployment. Cache004 remains optional after measured benefit; keyboard029 retains P5; export015 remains deferred and is not a mandatory release blocker.", "",
         "Canonical registry: `docs/elm-roadmap/research/20261005-design-adoption/requirements.json`; immutable source: `candidates-v3.json`. No runtime/configuration/source changes, GUI actions or installed activation are included.", ""]))
    write(CHANGE / "design.md", "\n".join([
        "# Design adoption — draft design", "", "## Context and status", "", NOTICE, "", EVIDENCE, "",
        "The source of truth for this additive packet is the hash-bound v3 ballot. `generate_adoption.py` copies normative EARS and all GIVEN/WHEN/THEN strings without rewriting them. The registry retains original research classifications separately from29 normalized draft refinements;015 remains deferred conditional export.53 proposal dispositions and10 report provenance entries are retained, including discarded or consolidated options.", "",
        "## Decisions and alternatives", "",
        "Keep modern Elm Architecture: one authoritative controller, immutable model, typed messages/pure transitions, read-only bar/popup projections, inspectable effect descriptions and narrow JSON boundaries. Native owns input/window effects, pixels, authenticated provenance, monotonic clocks and physical retirement. No Signals, automatic Unknown replay or JavaScript safety authority.", "",
        "Dependent effects use matching protocol-specific proofs. Proof IDs are not delivery ordinals; continuity uses a declared qualified mechanism and safe idempotent acknowledgement retries. Domain wrappers help internal construction but do not authenticate a sender. Typestate/session types inspire contracts; Elm has no linear type system and no static-session-typing claim is made.", "",
        "Ownership accounting covers admissions and transfers and remains charged until native producer/consumer completion and reader drain permit physical retirement. Cancellation/release intent, presentation closure, image-load and compositor frame callback are not retirement or hardware presentation evidence. Current availability and source liveness do not prove past success or fresh pixels.", "",
        "Measured derived caching is an optional mechanism after demonstrated benefit, not a mandated cache implementation. Vector clocks, new language/runtime rewrites, universal lossy streams, regenerated deadlines and unconditional disabled-control focus are not adopted. Existing per-protocol outcomes, per-surface disabled navigation and frozen source-state policies govern behavior.", "",
        "## Ordering and scope", ""] + [f"- {o}" for o in order] + ["",
        "## Risks and qualification", "",
        "Codec and transition-table changes may affect cross-language behavior; preserve wire contracts unless separately reviewed versions require evolution. Missing numerical budgets require measurement and freezing of the existing workload contract; academic papers do not supply production thresholds. Compare state, commands, accounting and explicit abstraction assumptions, disclose bounded sampling, and retain mutants/failures without upgrading them to native proof.", "",
        "Accessibility requires native names/roles/state/focus and speech/braille/IME transcripts on the actual qualified host. Performance requires same-machine input/feedback/presentation/resource spans and minimally observed runs. Frozen component ABI pairs cannot be cross-loaded. Production provider/full family/decor/modal/subsurface fidelity and integration drainage remain unqualified.", "",
        "Original13 S09, restore38/recovery34/case34,52 drag-resize/reload, multi-output/hardware/AT/IME, performance/resource budgets, coherent release and rollback remain independently mandatory. This change adds draft contracts; all implementation remains unchecked and no release closure is inferred.", "",
        "## Traceability", "",
        f"V2 ballot SHA256: `{sha}`. Full registry, source URLs, guardrails, tradeoffs and existing baseline/work-item mappings are preserved in `docs/elm-roadmap/research/20261005-design-adoption/requirements.json`, with exact OpenSpec copies grouped by capability.", ""]))
    tm = ["# Design adoption — unchecked tasks", "", NOTICE, "", EVIDENCE, "",
          "## Review and scope", "",
          "- [ ] Ratify corrected research requirements and preserve explicit reviewer dissent/dispositions.",
          "- [ ] Prepare and review a separate baseline amendment before these drafts govern implementation or release.",
          "- [ ] Reconcile existing component evidence against exact source/tool/ABI pairs without asserting production integration acceptance.", "",
          "## Implementation and qualification", ""]
    for m in mappings:
        gate = " (deferred conditional export; no mandatory release blocker)" if m["id"] == "ELM-ADOPT-015" else " (existing P5; early feasibility only beforehand)" if m["id"] == "ELM-ADOPT-029" else " (only after measured cache benefit)" if m["id"] == "ELM-ADOPT-004" else ""
        tm += [f"- [ ] {m['id']}: reconcile/implement/qualify through {links(m['workItems'])} with original prerequisite edges and exact scenario receipts{gate}."]
    tm += ["", "## Release evidence", "",
           "- [ ] Retain original242/417, right-click24,13 native preview,38/34/case34,52, deadlines, hardware/output/IME/AT and frozen budgets in the independent release ledger.",
           "- [ ] Qualify production preview provider, ownership/drain/fidelity and stage-specific native presentation evidence with the owning ABI.",
           "- [ ] Complete one coherent reversible release and separately authorized activation; conditional C00–C06 remain conditional.", ""]
    write(CHANGE / "tasks.md", "\n".join(tm))
    # Lightweight structural invariants; no CPU/native QA campaign is invoked.
    generated = json.loads((PACKET / "requirements.json").read_text())
    assert generated["proposalDispositions"] == ballot["proposalDispositions"]
    assert generated["reports"] == ballot["reports"]
    for before, after in zip(original, generated["requirements"]):
        assert before["ears"] == after["ears"]
        assert before["scenarios"] == after["scenarios"]
        assert before["scenarioIDs"] == after["scenarioIDs"]
        spec = (CHANGE / "specs" / after["capability"] / "spec.md").read_text()
        assert f"\n{before['ears']}\n" in spec
    assert "[x]" not in (CHANGE / "tasks.md").read_text()
    print(f"Generated30 EARS /67 scenarios across{len(grouped)} in-flight capabilities;29 refinements +1 deferred conditional export.")


if __name__ == "__main__":
    main()
