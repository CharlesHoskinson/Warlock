# Native uniquely owned decoration borrowing V5 / V21

Root familyV6 crashed during idle exact retirement in frozen V20. Preserve the
failed V6 attempt, ToolkitV4, ServiceV12 and GPUV7. The exact frozen SO resolves
plugin +0x294e8 to luaRetireGestureCurrent's terminate cold path. Actual
main.cpp constructs CHyprBar with makeUnique, records WP<CHyprBar>, then moves
unique ownership to the compositor decoration list. WeakPtr.hpp180 forbids
lock() because that would manufacture shared ownership of a unique object.

The retirement API retains exact address/stable-native-ID, live mapped/visible
owner and exact captured shared target checks. It synchronously borrows each
nonexpired unique-backed bar weak reference through get(), without promotion.
Expired or destroying bars are skipped. Neither the checked borrow nor
retireCaptionIntent invokes compositor/Lua callbacks, erases decorations or
changes ownership; the borrow is never stored outside this synchronous method.
The method resets local flags only, preserving genuine-release suppression.
Native drag retirement runs before borrowing bars because it may invoke core
and Lua callbacks. Window/target weak refs stay legitimately shared.

Idle correct identity returns success=true, retired=false; pending caption or
exact held drag returns success=true, retired=true; stale/hidden/unmapped owner
refuses; unrelated current drags and decorations keep their intent/geometry.
Destroyed weak handles never adopt replacements. Mid-destruction handles are
skipped even when get() remains non-null. Actual Hyprutils unique/weak types
and actual Lua VM exercise extracted exact retirement and caption method text.
Frozen V20 extracted idle function must reproduce SIGABRT with coreLimit1.

Formal model includes live/destroying/dead unique decoration states, current
owner identity, pending and active gestures, synchronous scoped borrow, no
shared promotion, and unchanged genuine-release semantics. All inherited
move/resize/drop/focus/old-close source/formal/helper checks remain required.
No native/toolkit acceptance, reload, deployment, main writes or root commands.
