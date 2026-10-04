# Read-only native live-grab census

Fresh observer derivative of held223, compiled against unchanged owning Core205.
The original302/297 GTK02 failure remains frozen. No action/native geometry guard
changes, no caller-selected resource and no permission to dispatch an effect.

`elm_grab_census` is restricted to the original canonical private QA runtime and
owner compositor thread. It samples the current strong seat-grab reference and
uses owning public `CWLCompositorProtocol::forEachSurface` to visit all live
compositor surfaces, including unmapped resources and non-popup/foreign clients.
It reports every live resource accepted by that grab. Unlike223 popup membership,
this list can expose an unrelated accepted surface. It refuses on invalid resource,
duplicate client/resource identity, more than4096 surfaces, more than256 members,
member JSON beyond60000 bytes, changed grab reference or exhausted sequence.
No partial success response is emitted. Sampling invokes no setters or effects.

Resource IDs are scoped by actual wl_client credentials, not renderer input.
The snapshot also reports native lock, exclusive-layer presence, layout drag,
held buttons and current pointer/keyboard focus. These preserve conservative
blocking: an exclusive-layer list containing expired entries still blocks.
Native role/global observations do not replace current target modality/family
eligibility. Query sequence is a decimal string and specific to this plugin
lifetime; it is not a full session/binding token or an authorization capability.

## Explicit limits and next producer work

This is a QA diagnostic, not yet an authenticated production authority response.
It does not identify the protocol that created the grab: a same-host focus-grab
with the same members cannot be classified as the menu's XDG grab from this
snapshot alone. Absence of that provenance must continue to refuse own-popup
admission. It reports live accepted resources, not expired weak entries in the
private grab vector. It does not expose object pointers as authority.

Production integration must additionally bind trusted host-derived actual popup
resource/client PID/start and root relation to exact controller/view/topology,
publication/menu/lease, current native session/full target binding and correlated
query. Exact XDG grab ownership needs a separately reviewed owning public API
or native lifecycle observation; no private-member/ABI tricks. All unrelated
blocking causes and target/family/output/constraint changes must reject planning
admission. After exact close/retirement/sync, newly correlated action and geometry
facts must be independently accepted before the unmodified native effect guard.

## Validation scope

The build verifies owning694 headers, unchanged205 manifest/binary, compilation,
all strong undefined symbols against actual core/linked-library exports, system
dependencies and input closure. It does not load the plugin or qualify native
snapshot completeness. Compiled production budget tests exercise boundary refusal,
cross-client resource-ID reuse using actual libwayland server resources and four
unsafe mutated budget bodies. Those tests do not create a real compositor grab.
Native actual same-host/mixed/foreign/unmapped-member census, GTK02 selection,
fullGTK/Qt campaigns and release/user-flow gates remain open.

Public Wayland client/resource enumeration documentation was consulted during
design: https://wayland.freedesktop.org/docs/html/apc.html . The implementation
uses the owning compositor's public surface visitor to avoid casting arbitrary
Wayland resource user data.
