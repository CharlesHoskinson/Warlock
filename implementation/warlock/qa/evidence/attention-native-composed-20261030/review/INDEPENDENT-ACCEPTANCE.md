# Independent original UX-009 disposition

**ACCEPTED: ELM-UX-009 / ux-009, for the evidenced current source/runtime tuple.** Root may record this disposition after immutable integration of source, passing evidence and both prior failed runs. This is an independent source/evidence review; Astra executed no QA, compiler, native process or public edits.

## Original oracle

Frozen docs/elm-roadmap/requirements.json states that while native observations mark a window active or attention-requesting, Elm exposes distinct active and attention indicators. The sole ux-009 scenario is an inactive window requesting attention, followed by distinct pixels and accessible state. Its verification requires an Elm replay assertion and isolated native recording. The evidence now supplies both, rather than substituting DOM labels or build checks for actual accessible export.

## Evidence and correspondence

Passing raw report: current-native-runtime-attention-root-v5/native-attention-1793322134268636412/report.json, SHA6ccfb8827128b7d9e7ac98142c471d67c918be146a10b300e747a1999370750d. All52 recorded assertions are true, including independent cleanup. Executed runner1d91bad01cbdb25fc2ace6896f5a60586d976e68befedca96cae7f004b92bb57 is the narrowly source-reviewed v5; public wrapper/facade/runtime/hook correspondence was reviewed before execution.

The current CPU evidence manifest at implementation/warlock/qa/evidence/attention-current-20261029 has no file-hash mismatches. Final report074214e1a90699c0bd1819f0b55e4c7cde608d2c4a728e242374e02a8fc0d1bf records compile/replay/boundary exit0,12 true actual Elm checks and11 strict native decoder/coherent-join checks. Inspected AttentionReplay.elm and check-attention.py: these cover actual production decoding/projection/surface, observation-only clearing, same-revision contradiction, active precedence, modal aggregation, negotiated attention shape, exact incarnation, cross-revision refusal and malformed/legacy observations. All99 inputs of current frontend lock match the CPU source map; recorded CPU sources and archived executed driver match current bytes. This is reuse of valid unchanged-source evidence, not a claim that CPU checks were rerun during this review.

Runtime uses frontend report613b4592a37982cedb881ba7edfd68d23349130a057ec9b0e62e213b2b17161d and composition lock56a088c4d83b205f0738954eb6c829b9635703628e14d92a433aa7a5a47351ca, validated before and after the journey by the production API. Actual core b1c582…, authority9ae162…, AQ667a22… and hosta6b0f0… hashes match their selected files; mapped AQ verification is recorded. Native report source map matches current bytes and contains all98 current Elm modules; elm.json is independently bound by the validated frontend lock, not claimed to occur in that native report map. No policy/native product source was changed by the fixture corrections.

## Actual observed behavior

Before request, root1 is focused and root2 inactive/nonattention. Real GTK present() requests attention for root2; native revision2 reports attention=true while focus remains1, with no submitted window effect and unchanged identity/membership. The screenshot records702 amber pixels for root2 versus804 blue pixels for root1 under unchanged thresholds and whole measured visibility. Actual configured and reserved bar height is56; the real clip is [0,0,540,56].

Actual AT-SPI exports under owned host PID537219/start20025838 and private bus show root2's `Activate ELM-ACTIVATION-PEER; Attention; Open` toggle button unpressed, while root1's `Minimize ELM-AUTHORITY-FIXTURE; Active` toggle is pressed/current=true. Both are uniquely joined through native incarnation/application, coherent group, DOM ID, taskbar/document ancestry and stable publication21/lease0 before/after snapshots. AT publication association is contemporaneous; AT-SPI itself exposes no publication field.

The stamped original pointer helper actually sends move201,26 and a left-button press/release. Exactly one window-effect activate intent targets incarnation2 with the matching authority context. Native revision3 focuses2 and clears its urgency. Activated AT records root2 pressed/current=true and Active at publication28/lease0, same native identity and host process. Original evdev keyboard helper then sends key30, and the real peer fixture records keyval97 on ELM-ACTIVATION-PEER. No scratchpad/workspace transfer occurred and no synthetic native-effect fixture was used.

Inspected both actual images and verified bytes:
- taskbar-native-attention.png SHA39182e54c264278448796702a3aa105549940ebe468c923fe884d0948c1ca57d visibly shows amber attention beside blue active.
- taskbar-native-activated.png SHAf31bfe4243f6b6a9354f4c942fda2ca8abaa4d65f59c2681ea6deacba57da7bd visibly shows the peer blue/Active and the previous root Open, with actual window focus changed.

Seven owned client exits, plugin unload and cleanup pass; no remaining/unexpected descendants or cleanup errors are recorded. /run/user/1000/wqa/a136 is actually absent on review. Original observation/helper deadlines and strict provider guard remain unchanged.

## Retained failures and bounded repairs

V2 reportf9ecdb28… remains failed: obsolete literal48 rejected a fully visible rectangle ending at49 despite real56px native allocation/reservation. V4 report2266e59… remains failed: bare visible/point did not satisfy inherited publication-stamp contract, and pointer input was never sent. Neither is a product defect or retroactively passing result. Measured clipping preserves full-box visibility; the stamped-control repair preserves all original current identity/publication/lease/geometry/enabled guards. V3 was never executed. The broader investigation's stopped history/counters remain; this review does not authorize new probes or resets.

## Limits

Accept only original UX-009 / ux-009 for this source/ABI/provider/asset tuple. No full UX025 accessibility, Orca speech/braille, all-output/theme/scale combinations, independent renderer601 repair, package installability, portability, complete tool-source closure or release acceptance is inferred. Raw runner nativeAcceptance/assistiveTechnologyAccepted/fullReleaseAccepted remain false; this separate independent decision closes the named original scenario only. Other native journeys and Windows pin/group/preview obligations retain their own evidence requirements.
