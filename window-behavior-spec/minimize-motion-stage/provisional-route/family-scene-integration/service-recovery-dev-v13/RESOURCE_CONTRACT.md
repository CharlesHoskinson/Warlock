# Family actor and cache lifecycle V12

This extends immutable service V11. Native recovery, presentation and cadence
acceptance are still open. Housekeeping cannot infer native authority from a
cache, create a renderer, or wait on context work in the receipt path.

The registry admits at most its configured actor limit across live and retiring
actors. New family acceptance refuses before writing a receipt if no slot is
available; an existing exact family can still reverse while at capacity. Actor
numbers increase for the entire service lifetime and are never reused.

An actor can detach only while its controller has no current scene, no retained
cancel acknowledgements and no pending ingress. Under the reservation lock,
remove all of its exact owner bindings and revoke obsolete direction state.
Native callbacks from it cannot acquire new authority. Keep its capacity slot
reserved until its workers finish and its renderer closes normally. Closure and
file disposal run outside the reservation lock, so unrelated retained visuals
can be retargeted immediately. Failure is reported and quarantined; it must not
silently free a slot for an actor whose process can still display surfaces.

Housekeeping runs on a separate thread at bounded cadence. Runtime shutdown
joins it before closing live actors. The launcher supplies an explicit cache
pruner. It must guard the selected compositor and validate a complete successful
client observation, including hidden/minimized identities. Missing, malformed,
duplicate, partial or failed client observations preserve the entire cache.
Only the existing exact cache ownership/provenance/lock rules may remove closed
pairs or abandoned own scratch. Current live minimized pairs survive actor
retirement. No shared cache pruning occurs in the receipt or native callback.

After workers and renderer finish normally, an actor snapshot directory can be
disposed only at its exact private owned nonsymlink inode, deleting only regular
owned private files from the actor's strict generated namespaces. Unexpected
entries refuse disposal and remain recorded. Shared cache and public preview
files are outside this directory and never removed by actor disposal.

Normal retirement writes a second durable snapshot after teardown, removing the
retiring slot only after normal closure/disposal. Ownerless obsolete receipt
entries may be collected only after the old workers/renderer finished and when
no newly accepted owner or pending scope still references that identity. A
quarantined slot and error remain durably recorded and block untrusted recovery.

Cache pruning and actor retirement are independent housekeeping operations: a
failed/incomplete native/cache observation preserves cache bytes but cannot
prevent a safely idle actor from closing. Pruning uses the existing global cache
lock nonblockingly; a live publisher/reader causes refusal/retry, never a wait
in the receipt or shutdown path. Shutdown joins the separate housekeeping task
before controller/renderer disposal and reports a bounded normal-stop failure
without racing teardown against a still-running job. It cannot claim successful
cleanup or release the runtime lease while such a job remains active.

Normal service stop first closes receipt admission and revokes every pending
context request under the registry lock. It then closes the socket ingress and
drains its context workers before disposing their actor desktops. Existing
validated scenes may settle only under the unchanged fresh identity/ownership
rules. Shutdown is not a new native authority and cannot validate a pending
intent by itself.

All remaining actors enter durable retiring slots before teardown. Renderer
normal exit and callback drain establish that retained visuals are gone; only
then may the service finish their local evidence records, dispose private actor
files, notify the factory of retirement, and remove their slots. Current scene
and cancellation records remain available during drain. Close, disposal or
persistence failure stays quarantined and reported, rather than leaving an
apparently successful idle journal. A service-wide stop cannot admit another
actor while completing these steps, and repeating successful close is harmless.

The service retains its bounded shared-cache handle independently of actor
registrations. After its last actor retires, successful complete guarded native
identity observations still prune closed own pairs; live minimized pairs remain.
The janitor uses the selected compositor environment directly and creates no
actor, desktop snapshot directory, producer, native request or authority.
