# Native motion observer

Temporary Hyprland ABI-guarded plugin. It observes one captured window/PID,
successful synchronous output commits and Aquamarine presentation feedback.
It does not hook functions, change geometry or write files in frame callbacks.
Each capture expires after 20 seconds and stops at 12,000 samples. Only the
selected disposable app's geometry is recorded. The live fixture unloads it.

## Reproduce

The installed compositor and development headers must have identical ABI hashes.
Build to a fresh filename; never rewrite a loaded `.so`:

```sh
make TARGET=motion-probe-v4.so
python3 live.py --library "$PWD/motion-probe-v4.so" --output "$HOME/.cache/window-motion-new"
```

The fixture requires one physical output at origin 0,0. It creates Foot, GTK4
and Qt Quick windows, measures caption drag, snap/restore, maximize/restore,
rapid snap reversal, reduced motion and reduction during an active transition.
It restores the motion file, runtime setting, initial focus and pointer, and
terminates only its own apps. A previous `smoke.py` run checked the observer
in the dedicated `nested.lua` compositor before physical-output use.

## Data and limits

- `frames`: `[relativeMs,x,y,w,h,goalX,goalY,goalW,goalH,fade,pointerX,pointerY,animating]`.
- `presentations`: `[observedMs,hardwareMs,sequence,flags,refreshNs,commitID,displayed,frameIndex]`.
- `inputs`: `[relativeMs,x,y]`; `marks`: `[validatedLabel,relativeMs]`.

The renderer's `monitor.preCommit` event samples current geometric values.
Aquamarine's synchronous DRM `events.commit` emits after successful submission.
The next presentation is associated only when exactly one submission is pending
and the queued-commit API is unused (`commitID == 0`). Unmatched/ambiguous
feedback is retained and excluded from paired metrics; no timestamp is invented.
The physical run requires VSYNC, hardware clock and hardware completion flags.

`analyze.py` measures presentation gaps across movement **including repeated
frames**, and separately measures changing geometry while animation error is
greater than one logical pixel. Spring subpixel tails are excluded from the
geometry-stall metric. Drag uses the complete injected-motion interval. Rapid
retargeting is not incorrectly classified as overshoot past its final target.

The 33.4 ms stall gate is a coarse visible-stall check, not a promise of one
new frame every 4.167 ms at 240 Hz. Refresh misses are reported independently.
Captures prove compositor rectangle/cadence behavior under this workload;
they do not prove application content repaint latency, every animation,
browser/GPU stress behavior, other refresh rates or physical multi-monitor use.

Source references: [Hyprland 0.56.2 monitor commit](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/output/Monitor.cpp),
[Aquamarine 0.15.0 DRM submission/presentation](https://github.com/hyprwm/aquamarine/blob/v0.15.0/src/backend/drm/DRM.cpp).
