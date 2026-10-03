# One-read cache mapping

The fresh MappingBatch collector retains a distinct RAII descriptor per actual
canonical disk image for one readKernel call. It captures all selected exact
VMA rows and all actual map_files readlink names before first source hashing.
Each distinct image is opened once, hashed once with pread, and has its current
named/FD/statx/fstatfs/flags/mount facts captured. All descriptors remain open
through the last selected VMA/readlink and source/selected-mount resampling.
Fresh disk rows outside the original captured set refuse; unrelated anonymous
non-executable mappings are not promoted to code authority. Producer identity
and consumer/observer namespace remain exact across collection. Each row's
pure validator consumes the actual original row, source before/after facts,
selected mount before/after facts and both actual kernel backing-name links.
Raw source/VMA partial evidence and errors persist before any refusal.

The cache is local to a stack invocation. RAII closes every descriptor on
success and every exception. No cross-call, cross-lease or process cache, no
added helper sleep, no artificial pause of the product helper, no retry.
The actual diagnostic's unavailable map_files follow operations are retained
in immutable diagnostic artifacts; runtime uses only the mandatory observed
readlink, never claiming an opened mapped-target FD. Kernel source establishes
the separate meanings of readlink and follow; the actual bounded named-image
property was reviewed independently by root before correction.

The approved temporal model already binds FD allocation, mount, device,
subvolume, raw row/offset/protection/path and child identity at both boundaries.
Caching changes the number of source/hash syscalls, not these obligations.
The numeric relation model separately requires Btrfs mapping device equals
the actual selected mount's filesystem device while named/FD/statx devices
match the actual subvolume device. Direct device equality remains mandatory
for non-Btrfs.
