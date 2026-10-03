# Bounded thumbnail admission (design only)

The immutable V24 product immediately rejects a busy per-address preview lock.
The external genuine renderer/Keeper/unchanged production preview-writer replay
reproduced errno 11, then normal writer completion and six actual batch PNGs.
This establishes a reachable production contention path. The native V9 exception
site and actual lock holder are not proved. All native baseline failures remain.

## Intended scope

An exact current receipt may wait briefly for genuine preview-writer contention
within its ORIGINAL receivedNs + 2,000,000,000ns deadline. No timer begins anew
at batch entry, any retry, helper launch, or publication. Expired preparation
refuses even if all locks become available. This may leave the native baseline
failing when captures have already consumed its original budget.

Only EAGAIN/EWOULDBLOCK from the exact flock invocation on authenticated owned
regular per-address lock descriptors is retryable. Source/path/descriptor or
family identity change, malformed material, unknown error, source supersession,
uncertain helper closure, and exited/rebound/foreign renderer still refuse.

Before retry, release ALL acquired address locks and all receipt/Keeper/lifecycle
locks. Acquire addresses in stable order with nonblocking flock. Do not wait
holding a partial set. After quiet acquisition, recheck original deadline and
current receipt, exact opened descriptor/path identities, complete family and
all original source/job/renderer guards. Admission itself grants no seed,
upload, presentation, native endpoint, helper-zero, or campaign authority.

Receipt guards use timed RLock acquisition bounded by the remaining ORIGINAL
deadline, with an exact monotonic-nanosecond check after acquiring. These checks
never hold the receipt/Keeper/lifecycle lock while waiting. A complete address
lock set may remain held across a receipt guard, preserving the original
publication transaction; a partial address set may not wait or retry. Time
advances during guard/descriptor scans and while any lock is held. Every boundary
rechecks the deadline after work; expiry closes/unlocks the exact owned resources
and prevents launch/publication. No helper group or unknown material is deleted
merely because admission timed out.

## Proposed source boundary, not implemented

1. SceneController passes the exact record.profile.receivedNs deadline to its
   finisher. NativeDesktop passes it unchanged to BatchPreviews.finish. Tests'
   fixture-only finisher callbacks accept the explicit parameter; outcome
   assertions and original deadlines remain unchanged.
2. BatchPreviews retains the immediate-failure path when called without an
   explicit deadline (existing standalone busy-lock refusal test remains exact).
   Production always supplies the immutable original deadline. The bounded
   admission loop handles selected busy flock only, releases all addresses on
   retry and revalidates owned lock identities/current receipt before committing.
3. PNG/material IO, source guards, exact renderer binding, Keeper guards,
   ImageMagick's original 1s timeout, current-family guards, source/cache/order,
   publication transaction, quarantine and disposal are preserved. No polling
   pause, preview-writer replacement, service deadline extension or fake success.

The model represents admission authority and clock/lock ordering. It does not
prove arbitrary kernel IO finishes on time or reconstruct the native exception.
Dispatch is the guarded call into commands.run, not the child's eventual G
release. Existing sealed helper setup, durable registration and gated release
remain exact. A helper may actually begin or finish after receipt expiry; its
registered ownership/uncertain closure remains, and expiry prohibits subsequent
cache publication and scene seeding. This patch claims no child-exec deadline.

Admission time is admittedAt. Dispatch time, normal helper closure, each cache
replacement and completed publication are separate model boundaries. Before
each replacement and final pending-source commit, recheck the original deadline
while current receipt is protected. Deadline/fault during multi-file replacement
can leave valid partial cache files (as an existing OS publication failure can);
this remains a rejected scene, with no complete-publication or seed authority.

Stable ordering maps model index1..N to the actual immutable tuple
`sorted(row['window']['address'] for _, row in rows)`. Acquire must select the
next index. Busy retry resets that index and releases all previously opened
descriptors, then reopens the SAME captured device/inode/type/owner. Lock size,
mtime and ctime are not stable: the production shell writer truncates the inode
before flock. Replacement/unlink/symlink/rebinding and hardlink alias refuse.

The inherited final PinnedPNG.check inside the receipt-protected publication
transaction remains exact. This admission model makes no new global claim that
all inherited material IO is outside receipt locks. Batch lifecycle means BatchPreviews.lock; inherited NativeDesktop.capture_lock
remains held across finish as before. New waits/descriptor IO are
outside receipt/Keeper/lifecycle locks.

SceneController also rechecks the same receivedNs+2s deadline under its existing
lock immediately before setting first-scene sources/visual and sending seed.
Output/fresh-state reads after cache completion cannot silently extend authority.
Its current receipt/family/material checks and all reversal paths remain exact.

Runtime and exact intended diff require independent root source approval first.
