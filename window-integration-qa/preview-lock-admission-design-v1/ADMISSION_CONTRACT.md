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

Receipt checks use bounded nonblocking RLock acquisition; failure to acquire is
another bounded retry, not a blocking wait beyond the original deadline. Time
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
Runtime and exact intended diff require independent root source approval first.
