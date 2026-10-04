# Cancellation on keyboard leave and capability retirement

Fresh derivative of frozen AQ138. Public headers/layout and every exported
symbol shall remain compatible. Parent transport and pointer cancellation,
publication/output/render/poll fences remain unchanged.

When a current live keyboard receives parent leave, it shall clear its private
focus/key/modifier state before callbacks and release only its recorded keys.
Other keyboards shall retain their independent records. Leave shall retire no
keyboard, pointer, output or backend. Duplicate leave shall emit no extra events.

When keyboard capability is removed, all current parent keyboards shall cancel
before their vector is cleared. The strong cancellation snapshot and clear-first
behavior shall preserve callback reentry/removal safety. Parent transport loss
retains the same cancellation hook before retirement.

When enter names an owned parent output surface for a current nonfailed keyboard,
the private focus flag shall become true. Its supplied held-key array shall not
invent key presses or populate the admitted-key ledger. Subsequent legitimate
key/modifier events may resume. Key/modifier events while unfocused or from a
failed/retired keyboard shall emit nothing. Constructor/destructor shall leave
public ABI unchanged and erase private records on normal keyboard destruction.

Quint shall model one keyboard with two abstract keys, parent failure, focus
leave/reentry and capability loss/restoration. C++ actual helpers and installed
typed signal/ownership primitives shall check bounds, reentry, multiple devices
and actual extracted callback bodies separately. Native152 capability/focus
failures remain evidence: both stranded A/Shift input/shortcut state and Shift
modifier1 for the original6s, with normal cleanup. Native acceptance requires
same GTK recipient releases, preserved pointer/output, restored real input,
exact owning Core89/plugin90/AQ tuple and ordered protected cleanup. Full device,
multiple physical keyboard, accessibility/IME and roadmap gates remain open.

V154 retains each matched keyboard through key/modifier callbacks, and retains the backend throughout capability callbacks. Invalid keyboard states refuse before ledger mutation. Actual153 named16/invariant1000x40 passed, but first mutation matcher retained the old field ordering;154 corrects that matcher only. Model source remains identical153.

V155 retains154 failed full library compile: keyboard callbacks cannot read private CWaylandOutput state.155 adds a private nonowning surface-to-output index populated by output construction and forgotten by destroy/destructor. Enter requires both index identity and current parent output membership; no public header/friend change and no pointer-focus dependency. Typed constructor28 and key2737/model16/1000x40/10 controls passed154 before that full-build failure;155 requalifies actual map, callbacks, output retirement and complete owning library.
