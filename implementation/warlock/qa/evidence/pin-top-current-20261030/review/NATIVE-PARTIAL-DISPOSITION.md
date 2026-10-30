# Pin/top partial evidence and AT helper boundary

Disposition: PARTIAL original ELM-UI-004 pin/top-independence evidence, NOT accepted. Both native runs remain failed. Stop the native investigation; do not launch further trials, reset counters, close the original EARS clause or revive the stopped New instance/Menu opener. This is read-only source/evidence adjudication; no reviewer QA or product edits.

## Actual v2 result

Report pin-top-root-v2/native-pin-independence-1793326280257913949/report.json SHA25611216afd1bd502cca51713ef85e84624e7b484926042a1386083046721fb0042 records194/195 checks passing and failed overall. The sole failed check is feedback-helper-83NormalExit. Source traceback now correctly names v2/executed-framework.py and shows first top_change('at',True) stopping in at_press's helper call. Five application Saved intervals and two native top transitions are observed:

* Application keyboard pin while native top=false; pointer unpin and re-pin while false.
* Native pointer pin=true with saved application membership/order/raw bytes unchanged and no preference write or launch.
* Application keyboard unpin/re-pin while native top=true, with no native effect or launch.
* Native keyboard unpin=false after physical secondary menu opening, with saved application state unchanged and no preference write or launch.

These exact receipts and observed states establish useful bounded pointer/keyboard independence. They do not supply the missing AT action result or full original acceptance. Persistent file mutation in this process is not UX004 restart/order qualification. No keyboard-only menu-opening claim follows.

Actual first AT target was an owned focused visible check-menu item named Always on top, accessible identity1558, DOM menu:3:2, PID560926, WebKitGTK button/menuitemcheckbox role, actual document/menu ancestry. It was checkable and unchecked, matching native top=false. Current geometry, full containment, screenshot paint and current-frame guards passed before helper invocation. The helper returned exit1 at its name-whitelist assertion with actions=['']; line35 do_action was never reached. No pin-semantics-at-0.json receipt exists and no pinAtActions result was recorded. The passing AT observation guards do not count as accepted AT activation.

Raw helper log: /home/charles/window-integration-qa/warlock-window-feedback-1793326280258040133/feedback-helper-83.log SHA2564c9906bf6f3b5e9a983d5be64db0ec785de12dbdf3dd6480981bcdcda322fe15. Seven owned normal exits, plugin unload and cleanup passed; runtime /run/user/1000/wqa/07c1 is absent. Frozen v1 report2588f14a... remains the earlier Tab-navigation fixture failure with165 recorded passing checks and partial observations. The v2 fix did not alter native policy or weaken assertions.

The actual v2 runtime report binds fresh facade6e1f46... and hosta6b0f0.../hostreport65b7e0..., matching the previously reviewed current65b909... frontend/ba97d48... composition path. A failed run does not produce its later postComposition success record; do not invent one.

Independently viewed and rehashed v2 screenshots0,6,8. Pin Peer/Add to taskbar is visibly distinct from the window-menu Always on top checkbox. Screenshot6 shows the checked target before keyboard unpin; screenshot8 shows the unchecked focused target before the failed AT helper. The target controls are visible; this is not acceptance of all other menu rows or whole-system accessibility. Image hashes are eb2b9081602f9582bb2e43edf752eedfaf7870d00511465fe77b55a7f150934c, c06785e73e768d104aa6d28257568810beffbe5a3ea0e645cdc00a7c2c02feae, c7b7feb58d1ecb16c6137ef0facb601a6de6b8853ca9628595d8e7dbe8cd4759.

## Exact API versus helper constraint

Read local primary interfaces, without running an AT query:

* /usr/share/gir-1.0/Atspi-2.0.gir SHA25675642551fd2964f1a2ae29aea25c8118b9a3664e3d1a44e9e653b8ee331663ec, Action.get_n_actions/get_action_name/do_action.
* window-integration-qa/orca-reader/physical-commands/at-spi2-core-2.60.7/xml/Action.xml SHA256ae8df12ef63c6c50284e172ecc904f74b6431e4d4b961cf6da9c9207480fb588, NActions/GetName/DoAction.
* Corresponding atspi/atspi-action.c SHA256eec80b3efeea9462400fd7b6bc5f007fd48b24ee9c26b949bb710bb836a65bd4.

AT-SPI exposes a count of actions, zero-based indices and invocation by index. Action.xml describes the first action as default by convention when multiple actions exist; one action has only valid index0. GetName provides a machine-readable name, but DoAction does not take a name or require the helper's English click/press/activate whitelist. The observed singleton empty name fails that extra helper restriction. This establishes the refusal location; it does not establish why the exported name is empty, declare its metadata correct, or prove the actual indexed action works.

The local C implementation has deprecated get_name delegate to get_action_name, which calls D-Bus GetName. Therefore switching method spelling merely because the helper prints a deprecation warning is not an evidenced fix. The retained Orca ax_action.py also invokes by checked index and warns that a true return alone may not establish completed behavior; actual native receipts/state remain necessary.

A separate future source-only compatibility proposal could retain unique known named-action selection, and otherwise permit index0 only for exactly one exported action whose name is empty, on the exact currently owned, enabled, focused and visible supported button/check-menu role with existing identity/ancestry/checked-state guards. Zero actions, multiple ambiguous actions, unknown nonempty names and any identity/lifetime failure would still refuse. Record the observed action count/name/index/selection rule without inventing a name, and retain the original production-path native effect/outcome checks. That proposal is not implemented, tested, accepted AT or permission for another native trial in this stopped investigation. No new production defect is asserted.
