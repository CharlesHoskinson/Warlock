# Remaining release work — EARS draft

This audits release closure, not whether every behavior is missing. Component evidence exists; this inventory makes no new acceptance decision. The frozen242 requirements/417 scenarios are copied verbatim into remaining-work.json and mapped exactly once to S01–S16 or conditional C00–C06. Existing right-click24 remains separate. Reconcile accepted component evidence before assigning implementation work.

The canonical baseline and its existing OpenSpec deltas remain authoritative. These24 additive closure requirements name the release evidence still needed; they do not replace the baseline or create24 new product features. All tasks remain open.

| Package | Remaining release outcome | Gate | Baseline requirements / scenarios |
| --- | --- | --- | --- |
| S01 | Baseline and inherited acceptance | Every inherited case has its original identity/oracle/deadline or a blocking missing-evidence entry; no historical CPU pass is relabeled native. | 11 / 11 |
| S02 | Product policy and measured budgets | Numeric applicable budgets and usability criteria are frozen; Generic replacement-desktop regression fixtures and native diagnosis evidence are retained. | 9 / 18 |
| S03 | Native host and protocol spikes | A real native shell surface, passthrough regions and versioned decoder/ABI rejection fixtures pass; no main-desktop activation. | 26 / 31 |
| S04 | Accelerated and accessible host selection | Nonsoftware webview composition and measured budgets pass; actual IME/popup/focus/AT route passes; unavailable WebGPU is honestly conditional. | 14 / 24 |
| S05 | Typed Elm policy and reliable authority | Named Quint/fuzz/replay tests and native stale/cancel/Unknown rejection pass; no effect is inferred from send or transport acceptance. | 30 / 57 |
| S06 | Canonical layering and focus | Generic eligibility/layering, genuine blocker/no-focus and workspace races pass with independent pixels, input recipients and focus receipts. | 28 / 42 |
| S07 | Taskbar vertical slice | Zero/single/group/active/minimized action fixtures, delayed/refused outcomes and keyboard overflow pass without duplicate effects. | 12 / 44 |
| S08 | Switcher and shell interaction lifecycle | Release-before-open, cancellation, incarnation reuse, native popup changed/same/stale routes and actual taskbar/switcher accessibility pass. | 14 / 24 |
| S09 | Retained family captures | Native source-stop and family pixel/fence/capability fixtures pass; historical/live/unavailable labels match actual source state. | 9 / 13 |
| S10 | Minimize and restore transactions | Original baseline38/recovery34 and case-34 deadline oracle pass; atomic proxy-to-live handoff and exact normal retirement receipts hold. | 15 / 20 |
| S11 | Graphics fault and resource qualification | Fault/lock/fence/output cases and whole-tree preview budgets pass; device loss retires invalid storage or exposes unavailable state. | 12 / 19 |
| S12 | Launcher, menus and system integration | Current-query launch/refusal and notification identity cases pass; adapters expose unavailable state; Files semantics and shortcut preferences persist. | 9 / 18 |
| S13 | Task View, snapping and physical outputs | Workspace transfer/refusal, scale/rotation/hotplug and active fullscreen/pin/modal policies pass; no invisible focus trap remains. | 10 / 21 |
| S14 | Accessibility and representative user flows | Every surface passes keyboard/AT and configured usability thresholds; original pin/input/popup/drag and representative app cases have exact receipts. | 8 / 37 |
| S15 | Reproducible release and recovery | One release tuple is reproducible; restart/resync and offline rollback restore compatible settings; only qualified targets are advertised. | 13 / 13 |
| S16 | Integrated release qualification | All applicable mandatory gates pass with the same source/runtime/ABI tuple; failed/unobserved outcomes block release; authorized activation has rollback receipts. | 10 / 13 |
| C00 | Optional compositor feasibility | Representative native compatibility evidence and a documented go/no-go decision; a no-go does not block the mandatory shell. | 3 / 3 (conditional) |
| C01 | Optional compositor roles and lifecycle | Representative native role/lifecycle and legacy X11 fixtures pass in nested sessions. | 2 / 2 (conditional) |
| C02 | Optional compositor outputs and seat | Isolated hotplug and input/output transition fixtures pass without losing ownership. | 1 / 1 (conditional) |
| C03 | Optional compositor IME and portals | Current-focus IME and session-bound portal consent/revocation fixtures pass. | 2 / 2 (conditional) |
| C04 | Optional compositor isolation and policy | Malformed clients and stalled frontend cannot bypass lock isolation or native input deadlines. | 2 / 2 (conditional) |
| C05 | Optional compositor compatibility qualification | No Hyprland-only receipt substitutes for a new-compositor gate; all applicable mandatory scenarios rerun. | 1 / 1 (conditional) |
| C06 | Optional compositor hardware and cutover | Hardware acceptance and independently rehearsed rollback pass before any authorized session cutover. | 1 / 1 (conditional) |
| RC | Right-click amendment closure | All24 ELM-RC amendment identities and their scenarios remain additive and independently qualified; native application client menus and Files semantics remain preserved. | 0 / 0 |

## ELM-CLOSE-S01

WHEN S01 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved gate.

Requirement mapping: ELM-ARC-001, ELM-DEL-001, ELM-DEL-002, ELM-QA-001, ELM-QA-002, ELM-QA-016, ELM-REN-001, ELM-REV-005, ELM-REV-006, ELM-REV-035, ELM-UX-001

## ELM-CLOSE-S02

WHEN S02 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved gate.

Requirement mapping: ELM-GNO-001, ELM-GPU-002, ELM-QA-021, ELM-REV-020, ELM-REV-021, ELM-REV-032, ELM-UI-003, ELM-UI-013, ELM-UI-021

## ELM-CLOSE-S03

WHEN S03 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved gate.

Requirement mapping: ELM-ARC-002, ELM-ARC-003, ELM-ARC-004, ELM-ARC-005, ELM-ARC-021, ELM-ARC-022, ELM-ARC-024, ELM-ARC-025, ELM-DEL-006, ELM-DEL-013, ELM-DEL-014, ELM-QA-009, ELM-QA-010, ELM-QA-011, ELM-QA-012, ELM-QA-013, ELM-REN-002, ELM-REV-007, ELM-REV-012, ELM-REV-014, ELM-REV-015, ELM-REV-027, ELM-REV-029, ELM-REV-030, ELM-REV-034, ELM-TEA-005

## ELM-CLOSE-S04

WHEN S04 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved gate.

Requirement mapping: ELM-DEL-026, ELM-DEL-027, ELM-GPU-001, ELM-GPU-003, ELM-GPU-004, ELM-GPU-005, ELM-GPU-010, ELM-QA-022, ELM-QA-024, ELM-QA-026, ELM-REV-025, ELM-UI-012, ELM-UX-012, ELM-UX-028

## ELM-CLOSE-S05

WHEN S05 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved gate.

Requirement mapping: ELM-ARC-006, ELM-ARC-007, ELM-ARC-008, ELM-ARC-009, ELM-ARC-010, ELM-ARC-011, ELM-ARC-012, ELM-ARC-013, ELM-ARC-014, ELM-ARC-015, ELM-ARC-016, ELM-ARC-026, ELM-DEL-010, ELM-DEL-011, ELM-DEL-012, ELM-DEL-015, ELM-DEL-017, ELM-QA-004, ELM-QA-005, ELM-QA-006, ELM-QA-007, ELM-QA-008, ELM-REV-001, ELM-REV-008, ELM-REV-009, ELM-REV-010, ELM-REV-011, ELM-TEA-001, ELM-TEA-002, ELM-TEA-003

## ELM-CLOSE-S06

WHEN S06 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved gate.

Requirement mapping: ELM-GNO-002, ELM-GNO-003, ELM-GNO-004, ELM-GNO-005, ELM-KDE-001, ELM-KDE-002, ELM-KDE-003, ELM-KDE-004, ELM-KDE-005, ELM-KDE-007, ELM-KDE-009, ELM-LAY-001, ELM-LAY-002, ELM-REN-015, ELM-REN-016, ELM-REN-018, ELM-REV-002, ELM-REV-013, ELM-REV-016, ELM-REV-017, ELM-REV-018, ELM-REV-024, ELM-REV-026, ELM-REV-031, ELM-UI-001, ELM-UI-002, ELM-UX-015, ELM-UX-016

## ELM-CLOSE-S07

WHEN S07 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved gate.

Requirement mapping: ELM-DEL-009, ELM-UI-004, ELM-UI-007, ELM-UI-008, ELM-UI-010, ELM-UI-015, ELM-UX-002, ELM-UX-003, ELM-UX-004, ELM-UX-005, ELM-UX-008, ELM-UX-009

## ELM-CLOSE-S08

WHEN S08 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved gate.

Requirement mapping: ELM-ARC-017, ELM-ARC-018, ELM-GNO-006, ELM-GNO-007, ELM-GNO-009, ELM-LAY-003, ELM-QA-018, ELM-REV-033, ELM-TEA-004, ELM-UI-011, ELM-UX-011, ELM-UX-013, ELM-UX-014, ELM-UX-025

## ELM-CLOSE-S09

WHEN S09 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved gate.

Requirement mapping: ELM-ARC-019, ELM-REN-003, ELM-REN-004, ELM-REN-005, ELM-REN-014, ELM-REV-023, ELM-UI-016, ELM-UX-006, ELM-UX-007

## ELM-CLOSE-S10

WHEN S10 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved gate.

Requirement mapping: ELM-ARC-020, ELM-GNO-008, ELM-KDE-006, ELM-QA-003, ELM-REN-006, ELM-REN-007, ELM-REN-008, ELM-REN-009, ELM-REN-010, ELM-REN-011, ELM-REN-013, ELM-UI-014, ELM-UI-018, ELM-UX-021, ELM-UX-022

## ELM-CLOSE-S11

WHEN S11 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved gate.

Requirement mapping: ELM-DEL-028, ELM-GPU-006, ELM-GPU-007, ELM-GPU-008, ELM-QA-025, ELM-REN-012, ELM-REN-019, ELM-REV-003, ELM-REV-004, ELM-REV-019, ELM-REV-022, ELM-UI-017

## ELM-CLOSE-S12

WHEN S12 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved gate.

Requirement mapping: ELM-UI-005, ELM-UI-020, ELM-UX-010, ELM-UX-029, ELM-UX-030, ELM-UX-031, ELM-UX-032, ELM-UX-033, ELM-UX-034

## ELM-CLOSE-S13

WHEN S13 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved gate.

Requirement mapping: ELM-KDE-008, ELM-QA-020, ELM-REN-017, ELM-REN-020, ELM-UI-006, ELM-UI-019, ELM-UX-017, ELM-UX-018, ELM-UX-019, ELM-UX-020

## ELM-CLOSE-S14

WHEN S14 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved gate.

Requirement mapping: ELM-ARC-023, ELM-QA-017, ELM-QA-019, ELM-UI-009, ELM-UX-023, ELM-UX-024, ELM-UX-026, ELM-UX-027

## ELM-CLOSE-S15

WHEN S15 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved gate.

Requirement mapping: ELM-ARC-027, ELM-DEL-003, ELM-DEL-004, ELM-DEL-005, ELM-DEL-007, ELM-DEL-008, ELM-DEL-016, ELM-DEL-018, ELM-DEL-019, ELM-DEL-020, ELM-DEL-021, ELM-DEL-022, ELM-REV-028

## ELM-CLOSE-S16

WHEN S16 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved gate.

Requirement mapping: ELM-DEL-023, ELM-DEL-024, ELM-DEL-025, ELM-GPU-009, ELM-QA-014, ELM-QA-015, ELM-QA-023, ELM-REN-021, ELM-REN-022, ELM-UX-035

## ELM-CLOSE-C00

WHERE compositor replacement is selected, WHEN C00 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved applicable gate.

Requirement mapping: ELM-ARC-028, ELM-QA-027, ELM-REN-023

## ELM-CLOSE-C01

WHERE compositor replacement is selected, WHEN C01 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved applicable gate.

Requirement mapping: ELM-ARC-029, ELM-REN-024

## ELM-CLOSE-C02

WHERE compositor replacement is selected, WHEN C02 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved applicable gate.

Requirement mapping: ELM-REN-025

## ELM-CLOSE-C03

WHERE compositor replacement is selected, WHEN C03 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved applicable gate.

Requirement mapping: ELM-REN-026, ELM-REN-027

## ELM-CLOSE-C04

WHERE compositor replacement is selected, WHEN C04 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved applicable gate.

Requirement mapping: ELM-REN-028, ELM-REN-029

## ELM-CLOSE-C05

WHERE compositor replacement is selected, WHEN C05 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved applicable gate.

Requirement mapping: ELM-QA-028

## ELM-CLOSE-C06

WHERE compositor replacement is selected, WHEN C06 qualification is submitted, the release verifier SHALL retain its exact requirement and scenario evidence and keep the package open on any failed or unobserved applicable gate.

Requirement mapping: ELM-REN-030

## ELM-CLOSE-RC

WHEN right-click release qualification is submitted, the release verifier SHALL retain the amendment identities and native targeting, keyboard, focus, refusal and accessibility evidence before closing the amendment.

Requirement mapping: Existing ELM-RC-001–024 amendment.
