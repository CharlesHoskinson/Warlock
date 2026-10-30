# Bounded architecture and integration review

Disposition: READY for publication of this Python backend correction and its bounded evidence. No blocking issue remains in the reviewed Pending-read poison delta or fixture/API adaptations. This is not approval to enable the C/Elm cancellation route or accept an original scenario.

Review method: read source and diffs, inspect retained reports and failure output, independently rehash recorded stdout/stderr, compare all seven public backend modules byte-for-byte with private v2, and rehash all current input entries in the three public reports (28/25/27 respectively; no mismatch). No QA, compiler, native process or model was executed by this reviewer.

## Source correspondence

- The v2 projection change catches OSError from the exact Pending read, poisons the shared ledger and rethrows. Expected absence remains a normal None result; an actual Pending still refuses settlement. The read remains under the existing single host guard, with no nested lock, _sync, network call or recursive _current added. The injected projection-read error checks refusal, shared poison, subsequent direct-read refusal and unchanged persistent bytes.
- The inherited reviewed cache predicate still requires the exact strict companion/certificate/retired V7 join, rejects ACK evidence ahead of the durable state, and completes file/directory durability barriers before allowing another key to use the target. It does not trust shape-valid cached evidence alone. The exact old companion key remains excluded from legacy begin/settlement/projection; cached retirement only lifts the separate target fence.
- The actual daemon supplies the mandatory settlement sink. Known local retirement emits its Pending ACK receipt before native ACK and emits the stored acknowledged update afterward; receipt lookup is read-only and startup separates current delivery binding from immutable old authority. Unknown never becomes a terminal cleanup receipt. Local cache receipt is not native execution or ACK permission.

## Fixture and evidence adjudication

- The old pending() fixture remains unchanged and continues to represent ordinary legacy admissions. Only typed cancellation setup uses cancellation_pending(), an explicitly labelled host-writer double producing a strict Submitted companion. It does not prove the actual C Reserved/Pending/Submitted write sequence.
- The base and legacy-isolation positive same-target/different-key reuse assertions remain intact. host_cached_retirement() obtains the actual producer frame, strictly validates it and durably writes the explicit C-cache double before those assertions. It neither unlinks the immutable companion nor supplies a caller exemption. The retained initial private regression failed precisely at the old positive reuse assertion because the new prerequisite was absent; that failure is not reclassified as a production defect.
- History routing preserves the old single historical recovery-record assertion by selecting that frame kind and separately checks the additional terminal settlement count, exact old certificate and new delivery binding. Other source changes are mandatory sink arguments, typed setup substitutions and public-relative import paths; no old negative assertion was removed.
- The retained private v2 run passes nine store and three coordinator groups. The actual public runs independently pass the same 9 + 3 groups plus two focused groups. Focused output reports 204 cache assertion events and 146 fault-group assertion events, including repeated setup/guard checks. The latter covers four injected I/O cuts and two independent V7/ACK prerequisite controls, not 146 distinct injected faults or original scenarios.
- The public focused runner retains partial output on timeout. The older private drivers do not retain TimeoutExpired partial output; the inspected successful terminal reports and preserved actual first regression failure are unaffected. No broader failure-retention claim is made.

## Remaining mandatory scope

The actual owning C parser/cache receiver and durable writer, original host acceptance/deadline origin, Elm negotiation/current and historical delivery, physical Escape and post-close recipient lifetime, authenticated native transport/resource retirement and full original ARC007/008/012/013 obligations remain unproved by this Python/double evidence. Normal host enablement is unchanged. Default V6 is covered by its retained positive controls, not by a claim that V7 companion scanning was installed in V6. No original acceptance, release qualification, live deployment or power-loss proof follows. Canonical LIMITS.md accurately preserves these boundaries.

## Exact reviewed public source

- adapter/cancellation_ledger.py: `35101521cdee18a8d27d0a3d068c037ff8188802cf7884bda896bb1bb40acec4`
- adapter/cancellation_host_cache.py: `6ff8900a5050e2eb07eef23989648fc3a5fc1f93b71c682b858f6d73fc9f8ea8`
- adapter/cancellation_host_admission.py: `21afd0b786c69a5a3978c26ff400944b62ca00c3d5f215c0eae2f48ee8336417`
- adapter/cancellation_host_settlement.py: `839c9d207ae0a827143fca44e235c1a996d758a8373cdf853a91cbfae89d1ade`
- adapter/cancellation_coordinator.py: `c6f35f2a22c948a5c6c7dbcbc69de9f85b6018647054d892a9ed101acb0a2282`
- adapter/recovery_store.py: `1c21e905fd1a7ce47583e3fa033843d902aaa710995336a5130e6d3117cdca7d`
- adapter/daemon.py: `70cbfe83a6e6913ec249c895773d32a9d0e0ff429786ef22a267f49a1a3e2906`

## Retained report identities

- /home/charles/.local/state/warlock-team/20261028/native-rebuild/cancellation-host-cache-root-v2/checks-1793375586325942307/report.json: `cd5624df7bdd19ea4e48f41cbfd186d75163b5a1234070e7d0223c2162a39da8`
- /home/charles/.local/state/warlock-team/20261028/native-rebuild/cancellation-host-cache-root-v2/regressions-1793376767032680329/report.json: `636181efdb0153ee8517e31874bebd4212d37153d24cd5be4a58e2fde9b4093d`
- /home/charles/.local/state/warlock-team/20261028/native-rebuild/cancellation-host-cache-root-v2/regressions-1793376795000740852/report.json: `62057295fb8aff9ae45fba56a1e333974de009143e4da95a5f86387c3cc3b0c2`
- /home/charles/Warlock/implementation/warlock/qa/runs/cancellation-store-1793376905033329051/report.json: `571d796a9fa52bcc74bc5886e349410c69a615d5f54f4fd963ac86622c9d09a9`
- /home/charles/Warlock/implementation/warlock/qa/runs/cancellation-coordinator-1793376918486105524/report.json: `6b0900170f4d15f5a07be9eea706806c94e42eabc5154ee5fcf87bd3cf44a2d3`
- /home/charles/Warlock/implementation/warlock/qa/runs/cancellation-host-cache-1793376978337210597/report.json: `8ca1ba6e66a7bb099da035215bab3234218f268abe593506341febc5a6644892`
