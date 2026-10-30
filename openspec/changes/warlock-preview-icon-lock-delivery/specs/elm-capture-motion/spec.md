## ADDED Requirements
> Current production-language decision (2026-10-30): Warlock-authored production uses Elm and Haskell only; all GUI elements are Elm. Haskell owns native/runtime capabilities, Haskell supplies pure policy where selected, and Elm owns GUI presentation with one authoritative policy owner per domain. Only Elm and Haskell authored production components may ship, including behind an allowed-language wrapper. Development/formal tooling and separately inventoried third-party libraries are distinct. Preserve original IDs, scenarios, behavior, deadlines and historical evidence; old passes do not accept replacements. Implementation remains paused pending readiness and root/Muse authorization. See `warlock-production-language-migration`.

### Requirement: WARLOCK-ICONDELIVERY-001 — Bounded original frontend delay

WHERE explicit private native icon qualification is selected, WHEN frontend delivery waits across actual native lock, the host SHALL retain at most four structurally valid original controller commits of at most131072 bytes each without fabricated batch disposition, delay their normal admission until the same Elm policy renders an actual concealed snapshot, then flush them unchanged in FIFO order through original validation; overflow or outstanding packets at teardown SHALL fail qualification without erasing owned jobs, readers, resources or receipts.

#### Scenario: WARLOCK-ICONDELIVERY-001 actual closure resumes after concealment

- GIVEN an authenticated actual icon reader and original native preview/popup presentation
- WHEN the private session locks while original controller commits wait
- THEN the own native held/new icon endpoint refuses before policy, exact locked denial conceals title/icon before producer retirement, and original pending controller commits resume once after actual snapshot without renewing the preview job or changing ordinary popup closure
