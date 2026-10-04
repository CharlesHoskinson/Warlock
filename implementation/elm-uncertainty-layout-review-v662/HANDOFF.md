# V662 narrow uncertainty layout review and native preparation

Status: preparation/source review accepted; **native renderer execution, visual
layout acceptance, participants and native accessibility/IME remain pending**.
640 is unchanged. No native GUI was launched and no desktop configuration,
session, backend, shared ledger, network or Git action was performed.

Protected CPU evidence:

- `qa/prepare-1791155393716206568/report.json`: 152 checks. Runs the actual held
  640 compiled Probe/SurfaceController/Surface packet reducer against captured
  synthetic transport frames with a long title inside the authoritative 256
  character scene limit. Produces Ready, Pending, Unknown, blocked menu and
  read-only Refresh packets. Every actual build input and corresponding compiled
  probe source is checked against640; the exact built Bar/Popup assets are copied.
- `qa/review-1791155917908466495/report.json`: 129 checks. Independent actual
  packet/markup/CSS contracts, runner syntax/deadlines/geometry/API preparation,
  installed WebKit2 4.1 API and cairo bridge availability. No browser constructed.
- Initial preparation exceeded the scene title bound, so the actual reducer
  refused the snapshot and no Pending transaction existed. Its failed event/row
  files remain under the earlier preparation directory. A review path-conversion
  error is also preserved as an empty failed-attempt directory; later reports
  supersede it. Neither failure established an actual rendering result.

Source findings (actual pixels and native AT still pending):

| Finding | Requirement IDs | Evidence and minimal proposed change |
|---|---|---|
| UX-UNC-001 high | ELM-UI-013/015, ELM-UX-027 | Actual renderer places long label text before trailing detail. CSS278 applies nowrap, overflow hidden and ellipsis to the whole 240px bar button. Separate a `.control-label` sibling, truncate only that label, and preserve the uncertainty detail visibly inside the existing48px bar. The globally visually hidden status is insufficient as visible feedback. |
| UX-UNC-002 medium | ELM-UI-009/010/015 | Actual blocked menu packets have detail `Awaiting native confirmation` but explicit `ariaLabel` only the action name; source picker has the same omission. Add an uncertainty suffix to blocked menu/picker names. DOM aria-label evidence does not establish native AT behavior. |
| UX-UNC-003 medium | ELM-UI-013/015, ELM-UX-027 | Actual popup notice contains the read-only/no-retry explanation, while CSS forces a single ellipsized line. Wrap this explanation and verify subsequent controls remain reachable within the original420px popup viewport. |

The native runner is an **explicit renderer fixture variant**, not the complete
authenticated GUI journey. It loads the actual built640 `bar.html`/`popup.html`,
optimized Elm Bar/Popup JS, original adapter/context scripts and original CSS
through an allowlisted private WebKit scheme. No detached fake markup is used.
Actual compiled root packets enter the original `receivePresentation` port.
Packets from independent reducer traces reload the real renderer rather than
forging newer publication identities. The fixture captures outgoing renderer
actions; it runs no authority/backend and synthesizes no native proof.

Root alone may launch after reviewing the runner. It uses the reviewed595 private
host with unchanged800x600 output, original six-second observation deadlines and
native keyboard helper. It resizes an actual floating WebKit viewport to320,480
and800px. These are viewport fixtures, **not physical narrow-output acceptance**.
Each case captures actual DOM glyph ranges clipped against ancestor/viewport
bounds, PNGs with decoded pixel dimensions and rendered color variation, disabled
states and explicit aria-label text. Pixel evidence supports DOM layout analysis;
there is no OCR assertion or participant reading-comprehension claim. In Unknown,
native Tab must skip the disabled target and reach Refresh; native Enter must
emit exactly one current Refresh renderer action. The separate compiled reducer
test proves that Refresh emits only observation reads without changing effect
counters/history. These component observations do not imply backend/native
proof authority integration.

The execution report deliberately keeps `layoutAcceptance:false`: the current
known defect is a diagnostic target. Full glyph visibility and accessible
uncertainty are reported as findings, not silently turned into passing behavior.
The runner retains fixed deadlines and requires normal fixture exits and private
host cleanup. Every frozen662 file and original640 input is verified before
launch. A fresh root-owned output path outside662 is mandatory, for example:

```
ELM_LAYOUT_NATIVE_OUTPUT=/home/hoskinson/omarchy-windows-parity/implementation/elm-uncertainty-layout-native-vNNN/qa/native-1 \
/usr/bin/python3 -B implementation/elm-build-loop-v1/loop.py native \
  --runner /home/hoskinson/omarchy-windows-parity/implementation/elm-uncertainty-layout-review-v662/qa/native.py
```

Use a new root-assigned NNN; no native campaign directory is created here.
Future663 minimal correction is proposed, not implemented by this packet. Its
acceptance should compare original vs corrected pixels/DOM with original48px bar,
420px popup, full names, unchanged identities/disabled policy, popup keyboard and
reachable controls. Remaining coverage includes actual full640 backend Pending/
Unknown/read-only Refresh journeys with long native titles, picker variants,
physical small outputs, enlargement/reflow/contrast thresholds and native AT/IME.
No baseline requirement or scenario is marked complete.
