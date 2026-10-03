# KeyboardMonitor packet ordering

Both examined primary implementations use a pre-event mask:

- [KWin keyboard input](https://raw.githubusercontent.com/KDE/kwin/master/src/keyboard_input.cpp) invokes its accessibility manager before updating its normal XKB state. The manager serializes the effective modifier state and derives the keysym from that state.
- [Mutter native seat](https://raw.githubusercontent.com/GNOME/mutter/main/src/backends/native/meta-seat-impl.c) creates the key event before its XKB update. [Its event builder](https://raw.githubusercontent.com/GNOME/mutter/main/src/backends/native/meta-xkb-utils.c) serializes the supplied XKB state's depressed/latched/locked/effective masks and derives the keysym before returning the event.

v5 prepares its observer packet before changing either accepted or captured shadow key state. Raw held non-locking modifiers are visible, while latched/locked state remains accepted native state. The same `packetBeforeKey` helper is used by the compiled plugin source and standalone replay.

| Sequence event | Expected packet state | Accepted state after event |
| --- | --- | --- |
| ordinary Shift down | no Shift yet | Shift held |
| H down while Shift held | Shift, keysym H | Shift held |
| Shift up | Shift still in pre-event mask | Shift released |
| first ordinary Caps down | Caps lock absent | Caps locked |
| next ordinary Caps unlock up | Caps lock present | Caps unlocked |
| next H after unlock | Caps lock absent, keysym h | Caps unlocked |
| captured custom Caps then H | Caps lock absent, keysym h | Caps unlocked |
| captured custom Insert then H | no native modifier, keysym h | native state unchanged |

Real XKB replay caught a separate custom Caps problem: a locking key contributes a depressed modifier bit while held, even with its locked state suppressed. The observer must remove locking bits contributed by currently captured keys; otherwise the suppressed Caps press still uppercases the chord. v5 removes those contributions using actual keymap locking-key bits. It retains ordinary captured Shift/Ctrl contributions and accepted preexisting locks.

v4's attempted post-event signal change was rejected after checking primary source ordering. v3 and v4 remain unexecuted artifacts; neither is a deployment candidate. This source/replay evidence does not establish actual native reader command handling.
