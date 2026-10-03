# Intended mapping before implementation

| Model | Proposed runtime obligation |
| --- | --- |
| active / lease | Exact selected QObject pointer plus existing invocation lease and guarded generation; owning thread only; drain queued current faults first |
| command / boundCommand | Actual Process.command getter with original type, both guarded reads; helper route/source fixed; no final-argv inference |
| worker / joined / budget | Actual registered immutable-value worker full live result, original 2s/16 epochs, exact child/lease and normal pthread join |
| historical / exit / normal / out / err / gone / receipt | Every approved V7 actor condition and strict old receipt, independently observed, preserved raw |
| actor/source/current | Original QPointers, contexts, engine/provider activation and compiled source/config/image checks; current consumer additionally required for new action completion |
| Retire(lease) | Validate old lifecycle and receipt, stable old fields before/after, then atomic disconnect/history/no-current commit; no process/input effect |
| sealed / pastLease / pastCommand | Immutable normal past observation only; later setters cannot give it current authority |
| Arm | Fresh full original guards, null actual processId, monotonic allocator/capacity; no copying old proof/EOF/receipt or old acceptance |
| OldCallback | Genuine wrong exact object/lease no-op; current duplicates still fault |

V7 Registry callbacks and core mapping/source/worker byte predicates must stay exact except the separately reviewed new terminal operation/arm route. The initial intended frontend sequence is: observe real current receipt → explicit terminal retirement while old command/EOF remain unchanged → select new exact original request command → arm new independent lease → launch unchanged helper once. A busy/pending or refused retirement cannot trigger a new launch.

No frontend QML or native Registry method is implemented here. Caller completion flags, nonce-only identity, old terminal Boolean caches, context assignment and command-address fallback are prohibited. Existing source inverses and original user-facing per-window Toggle pin behavior remain preserved in any future derivative.
