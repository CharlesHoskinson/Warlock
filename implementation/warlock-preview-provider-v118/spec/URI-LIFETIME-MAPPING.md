The uri_callback_lifetime_v2 Quint module specifies native URI callback lifetime
and transport guards; it is not a UI policy or physical resource authority.
Open/Read/CloseReader call actual C router and GIO APIs. DestroyEndpoint destroys
the actual owner while a retained reader may keep Shared storage. ReplaceReceiver
uses actual unregister/re-register with a fresh native epoch in the same Shared
state. Bind/Clear call the actual C router. NewRealm creates a fresh direct-native
fixture/Broker on the original binding after old ownership drains. Expire advances
the fixture native clock to the original packet expiry. ForeignBind constructs an
actual separate foreign-binding fixture. DropOwner releases only the C owner's
router reference while the callback keeps its independently owned reference.

Every event compares actual endpoint presence, registered receiver epoch, callback
open result, reader/epoch, real sealed FD existence, returned byte/EOF count,
clock expiry, remaining owner reference and operation result. Route/through are
history ghosts, excluded from actual comparison; their semantics are witnessed by
next actual bind/open outcomes. A temporary actual callback open/close observes
availability without changing the held reader or signaling any native fence.
Every successful trace clears callback references and closes actual mapped FDs.
The standalone66-control C witness separately detects three compiled unsafe
product guard variants and covers creator-thread and exact opaque URI freshness.

Explicitly select all16 named scenarios;200 bounded invariant samples are distinct
from24 actual compiled traces/320 state comparisons. Synthetic scope/signature
bytes do not establish actual Core/WebKit/Wayland-window or release acceptance.
