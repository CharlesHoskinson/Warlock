# V2 producer refusal and focus classification

Retain V2 attempt2 report SHA300d5f93dcd3bd9efd303914155badb69ef570bd2b432c9434e20ae85051556d.
It passed13 reached checks including actual flushed startup transport, then first
held-key stdin flush failed with BrokenPipe. It retained the correct first error,
normal quiescent plugin unload, no owned survivors and healthy parent transport.
Focus was false only because app-owned title changed; old18/19 result stays failed.

Frozen native-input.c requires /tmp/kbn-* before wl_display_connect and returns20
silently for the actual wqa runtime. Native-pointer.c has the same guard and
returns2. Running both exact old binaries against the retained runtime/display
reproduced those exact silent exits without a compositor connection. Source and
binary hashes plus real exits are in old-producer-rejection.json. This is a fixture
migration omission, not evidence of a bridge or permission-policy defect.

Fresh V3 changes producer authorization/bootstrap only, passing its verified owned
peer FD to libwayland with no inherited/default target. Actual keymap/key/modifier,
repeat/EOF release, pointer movement/precision/frame algorithms remain unchanged.
Protocol headers/XML used for compilation are now explicit local dependencies.
Every native producer performs a sync-only roundtrip before first input. Failed
startup records PID, exit status, response and stderr tail; no keys establish
readiness. All existing acceptance oracles remain, with only readiness calls added.

Main focus compares exact address/stableId/PID; full before/after objects remain
recorded alongside independent title hashes. The previous natural title change
is retained separately in title-only-classification.json. Native client state
and full set remain exact; a changed focus identity still fails. Main writes and
restoration remain absent. No V3 native run has occurred.
