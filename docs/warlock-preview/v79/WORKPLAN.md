# Next preview intents and native admission liveness

Public feedback delivery56 is verified at
`498df7d93c334137711c87de7915a7e936ba2074`; source receipt commit is
`693595c473aada8a2bd0cdff4f9fc8f177dcaa1d`. Full release remains open.

The current implementation adds explicit succession for expired, unissued
enrollment in the existing trusted C bridge and full host. Same-stamp polling
does not renew. Both publication and lease increase, the native cutoff remains
two seconds, and current plus one predecessor are bounded per actor. Issued
frames, Broker request floors, receipts and physical ownership are preserved.
Actual native capture eligibility remains unchanged.

The new model maps the actual ledger, native demand/Broker reservation and
bounded history. The C/socket fixture uses the original bootstrap and receipt
delivery, and its actual messages replay through optimized current Elm. The
projection does not establish whole-policy refinement or compositor acceptance.

Code review identifies a remaining GUI scheduling problem: on reopening after
the pool drains, resuming the two previously issued subjects before visiting the
unissued third can consume both items again. The third would receive a new
cutoff but still starve. The next derivative must visit unissued current picker
subjects before resumable issued actors, retain exact physical admission limits,
and qualify an actual third image after expiry/reopen in the same GUI host.
Do not claim this liveness behavior from the isolated C fixture.

Then advance expired unissued resume intents with separate original-job
correlation, and implement proof-safe actor/history retirement. Preserve native
floors and Elm counters; closing presentation is not retirement proof. Continue
ordinary eligible capture and every original S09/S01–S16, restore/recovery/drag,
input/popup/output/hardware/AT/IME/resource/journey and reversible release gate.
This work follows W03/W06/W10 and additive ELM-ADOPT-002/009/010; it changes no
frozen requirement, scenario identity, original deadline or unknown outcome.
