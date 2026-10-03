# Native family fixture pin correction

The preserved failed run at `~/.cache/window-minimize-freeze-family-pinned` stopped during fixture setup, before the motion driver. It directly pinned only the owner then asserted all modal children had their native `pinned` bit set. Native family following intentionally preserves separate pin bits; existing pinned modal acceptance tests explicitly exercise independently pinned children.

This fresh wrapper captures every member's pin bit before setup, verifies the backend family equals the exact stable ID/PID/address set and deepest modal focus, pins the owner, then requires owner=true and all peer bits unchanged. It records before/after setup and backend plan before any assertion. The unchanged copied motion observer still checks every original pin/identity/geometry at endpoints and retains strict `--require-freeze` gates.

```bash
python3 ~/window-behavior-spec/minimize-motion-stage/fixture-family-pin/test_fixture_pin_policy.py
```

Eight offline policy checks pass; syntax checks pass. No GUI run performed. Coordinated native replay:

```bash
python3 ~/window-behavior-spec/minimize-motion-stage/fixture-family-pin/native_motion_fixture.py \
  --toolkit family --pin --require-freeze --reduced-motion-trial \
  --output ~/.cache/window-minimize-freeze-family-pinned-corrected
```
