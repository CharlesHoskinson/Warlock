# Current query after an obsolete catalog reply

The launcher now forwards its retained query after the native presentation-applied acknowledgement. Previously the live input showed `editor`, while the root query remained empty and launch entries stayed disabled. The adapter keeps one observational query for the current publication/lease, coalesces newer text, retires replacements, and preserves it across duplicate presentations. It does not rebase or buffer effect actions.

Original **ELM-UI-005/search-race**: given a query/catalog fixture, change the query while an old refresh completes; only current-generation results and selection can dispatch. Both real native runs follow this schedule:

1. Open Apps through the Omarchy keyboard chord and type `files`.
2. Hold the genuine request-7, catalog-generation-1 reply before the original bounded writer, without blocking the backend.
3. Type `editor` while loading. Enter issues no launch.
4. Update only the owned desktop fixture and explicitly refresh. Request 8 observes genuine generation 2. Focus its current Editor result through physical Tab.
5. Release the exact old reply. Current query, result, publication and focus remain; old Files/Editor results do not replace them. Actual AT-SPI and Orca agree on the current focused result before and after release.
6. Physical Enter in one run and actual AT-SPI press in another each submit one current identity/generation through the unchanged GIO authority. The recorder observes only `CURRENT_EDITOR`. No window mutation occurs.

`keyboard.png` and `at-action.png` show the real focused result. Counts cover only its and Refresh's interiors below y100; compositor warning pixels are excluded. Both private native campaigns pass normal cleanup. Reports, raw logs, exact held/fresh/delivered receipts and generated fixture source are frozen here. The native path observes existing product catalog/request authority rather than inventing a replacement receipt.

The quint-llm-kit workflow checked executable initialization before implementation, then six named tests and 500 sampled traces of 40 steps, with positive queued/delivered/retired/advanced witnesses. `query-delivery.*.stdout` retains the results. `adapter-before.stderr` and original bytes demonstrate the transport regression. The actual adapter check covers acknowledgement ordering, current-query coalescing, old publication/lease retirement, direct admitted delivery, unchanged effect forwarding and duplicate presentations. The compiled Main/Bar/Popup, original search/ranking, local-field, pins, native host admission and browser IME checks pass. This model abstracts text and assumes FIFO posts on the existing WebKit handler; it does not certify native input/paint/AT or exhaustive model checking.

The original native IME regression passes direct preedit and commit/caret without a launch, then fails `candidate_layers` at the unchanged deadline. The published prior report has the same failure and installed Fcitx/module/profile hashes. Candidate commit/cancel remains open; the failure is not converted into a native IME pass.

**Disposition: partial.** Owner observation is not independent original acceptance. Broad catalog/language/AT modes, audible speech/braille, hardware/resource/journey/package/deployment/rollback remain separate. See `manifest.json` for exact hashes, tuple, source correspondence, original EARS and missing observations. CPU/native artifacts still depend on the recorded machine-local protected environment.
