# Native preview demand coordination

This implements the scheduling part of ELM-ADOPT-022/027 and preserves ELM-ADOPT-006/009/010/028. It is a provider component using the actual v517 Broker, not an installed provider or S09 acceptance.

WHEN an authorized native demand observes newer tracked content during capture, the coordinator SHALL retain one latest desired scope per enrolled entry and admit a fresh request only under the configured native-clock pacing and actual available broker capacity.

WHEN a demand closes or its native eligibility is revoked, the coordinator SHALL withdraw queued demand and request cancellation of retained jobs without erasing broker ownership, charge, original deadlines or replay floors.

WHEN the trusted producer completes, the coordinator SHALL allow separately available capacity to service newer demand while the broker continues to own old consumer-held storage until exact physical retirement.

WHEN a boundary input is invalid or stale, the coordinator SHALL reject it locally without inventing a terminal native refusal or authorizing a replacement scope.

A source revision is native tracked content only. No family/subsurface fidelity is added. Pacing is a required caller-supplied positive policy; no universal frame interval or product performance claim is introduced. Clocks belong to one explicit native lifetime/domain. Entry/record/item/byte bounds remain fail-closed. Closed lease identities cannot reopen; a fresh higher native lease is required. This component does not compact authority history or reclaim actor identities without scope-retirement proof.

The Quint model covers latest-demand retention, pacing, close/reopen, producer versus consumer ownership and bounded capacity for one native entry. Compiled two-entry and exact-scope checks cover boundaries outside that abstraction. Concrete trace replay compares scheduling and broker charge/ownership after each selected event; it does not qualify compositor pixels or presentation.
