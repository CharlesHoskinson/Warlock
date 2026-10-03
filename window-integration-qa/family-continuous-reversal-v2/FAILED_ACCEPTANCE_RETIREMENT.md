# Failure teardown correction

V1 retained a real 334.778 ms API acceptance stall. Its second actual retarget
origin had progress 1, so the original interior-reversal oracle correctly refused.
The incomplete workload also failed the helper count gate; that exception
preceded explicit native module unload. All owned clients/renderers and the
private compositor nevertheless exited normally, with all 15 main observations
preserved. The explicit unload acceptance gate remains failed in V1.

V2 adds a clients-first deferred native retirement callback. It runs while the
exact private session is still live, skips an already successful unload, refuses
remaining clients, and verifies module absence. It changes no product behavior
or reversal oracle. This stage must retain V1 bytes, attempts and attribution.
Native execution is pending a fresh formally reviewed responsive service; do
not rerun V12 and relax the interior-origin requirement.
