- [x] Compile current full Elm/GTK/native host and preserve original controls (GUI76, full95).

> Current production-language decision (2026-10-30): Warlock-authored production uses Elm and Haskell only; all GUI elements are Elm. Haskell owns native/runtime capabilities, Haskell supplies pure policy where selected, and Elm owns GUI presentation with one authoritative policy owner per domain. Only Elm and Haskell authored production components may ship, including behind an allowed-language wrapper. Development/formal tooling and separately inventoried third-party libraries are distinct. Preserve original IDs, scenarios, behavior, deadlines and historical evidence; old passes do not accept replacements. Implementation remains paused pending readiness and root/Muse authorization. See `warlock-production-language-migration`.
- [x] Execute selected Quint and actual compiled feedback traces (9 cases, 21 traces).
- [x] Verify actual native C outcomes and same Elm lifecycle/counters (49 C, 18 compiled Elm wire checks; 43 guards).
- [ ] Qualify three-window full host on serialized exact native tuple.
- [ ] Freeze and publish owned evidence, then continue all original release gates.
