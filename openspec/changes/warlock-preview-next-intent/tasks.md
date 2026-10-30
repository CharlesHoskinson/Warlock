- [x] Implement native bounded monotonic succession and explicit C/host route.

> Current production-language decision (2026-10-30): Warlock-authored production uses Elm and Haskell only; all GUI elements are Elm. Haskell owns native/runtime capabilities, Haskell supplies pure policy where selected, and Elm owns GUI presentation with one authoritative policy owner per domain. Only Elm and Haskell authored production components may ship, including behind an allowed-language wrapper. Development/formal tooling and separately inventoried third-party libraries are distinct. Preserve original IDs, scenarios, behavior, deadlines and historical evidence; old passes do not accept replacements. Implementation remains paused pending readiness and root/Muse authorization. See `warlock-production-language-migration`.
- [x] Compile the full Elm/native host and preserve original controls (GUI79 full95).
- [x] Run explicitly selected Quint cases and coupled ledger/Broker traces (10 cases,22 traces,two unsafe mutations detected).
- [x] Verify actual C/socket outputs through the current optimized Elm presenter (C45,Elm21).
- [ ] Qualify native GUI expiry/reopen/actual image/normal cleanup on the owning ABI.
- [ ] Freeze, commit and publish exact owned evidence; retain all full release gates.
