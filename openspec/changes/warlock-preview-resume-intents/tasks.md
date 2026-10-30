- [ ] Compile changed full GUI and native bridge.

> Current production-language decision (2026-10-30): Warlock-authored production uses Elm and Haskell only; all GUI elements are Elm. Haskell owns native/runtime capabilities, Haskell supplies pure policy where selected, and Elm owns GUI presentation with one authoritative policy owner per domain. Only Elm and Haskell authored production components may ship, including behind an allowed-language wrapper. Development/formal tooling and separately inventoried third-party libraries are distinct. Preserve original IDs, scenarios, behavior, deadlines and historical evidence; old passes do not accept replacements. Implementation remains paused pending readiness and root/Muse authorization. See `warlock-production-language-migration`.
- [ ] Execute explicitly selected Quint scenarios coupled to actual allocator.
- [ ] Verify typed C retries and optimized Elm rejected-job settlement.
- [ ] Qualify changed production on the serialized owning native ABI tuple.
- [ ] Freeze evidence, publish only owned paths, and continue original release gates.
