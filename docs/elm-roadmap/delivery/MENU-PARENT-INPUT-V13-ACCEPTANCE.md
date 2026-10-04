# Parent-seat input into the Elm menu V13

This derivative connects the frozen V10 Weston parent-seat input module to the
exact V8 Elm menu, native core/plugin and nested Aquamarine tuple. The parent
client injects pointer motion, press and release into Weston; the child receives
the mapped coordinates through the viewport. The existing protected menu
campaign then checks actual Elm popup state, native operation receipts, popup
bounds, keyboard focus, output resize, scale 2, restoration and retirement.

The protected native run passed 68 checks with 19 parent pointer actions and
clean process teardown. It kept the original six-second observation deadlines.
The first retained V13 attempt failed on Shift+F10 after input notifications
returned before the child had settled the preceding click. A bounded 150 ms
post-injection settle interval, matching the inherited campaign's explicit
pointer timing, passed the unchanged behavioral checks. Both attempts and the
exact source and ABI hashes are in
`implementation/elm-menu-parent-input-v13/qa/slice-manifest.json`.

This closes the V8 follow-up for parent pointer delivery into the targeted menu
journey. It does not qualify cursor pixels, rotated or multiple outputs,
injection during parent configure transitions, accessibility, IME or release.
No main-desktop installation or activation occurred.
