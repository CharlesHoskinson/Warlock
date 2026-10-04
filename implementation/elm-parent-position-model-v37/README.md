# Parent-coordinate adapter contract

This model describes one event-loop adapter, not a second desktop authority.
It represents two distinct outputs, quarter-unit normalized coordinates,
logical boxes, an active parent focus, weak device/backend lifetime, and staged,
ACKed and committed mapping generations. It is a finite abstraction of the
V30 readiness query and V31 parent-coordinate route. Its initial mappings are
already committed; it does not claim startup, overflow, pixels or transport.

Motion projects against its owning output, including the output origin.
Unfocused, uncommitted, retired, disabled or mirrored routes cannot dispatch.
A layout callback reprojects an existing anchor only if its logical box changed
and the device, output and readiness guards still permit it. A programmatic
warp clears that anchor. Focus or mapping changes alone do not assert immediate
anchor removal; subsequent dispatch/layout validates readiness. This matches
the source's distinction between cached state and permitted replay.

The explicit selector executes 19 named scenarios. A separate seeded run checks
the safety invariant for 1,000 samples of up to 40 steps. Three independently
typechecked model mutations fail the relevant named cases. V36 retains the
initial built-in-identifier parsing failure; V37 is the corrected derivative.

V39 converts the named ITF states into typed C++ fixtures. It extracts the actual
V30 query bodies and V31 state, warpTo, parent output projection, layout handler,
detach handler and parent warp listener body. The routing bodies are not
reimplemented in the fixture. It compares anchor/output identity, normalized
point, routed warp count and forwarded/superseding coordinates across 86
states. Three production-fragment mutations fail this comparison.

The typed environment substitutes ownership, monitor lists and InputManager
plumbing. It stubs renderer/idle/DPMS effects and general closestValid clamping;
it compares logical coordinates only for forwarded parent events and explicit
superseding warps. It does not execute a real compositor, prove full-program
refinement, model queued AQ idle work, or certify every physical hotplug path.
Named witness replay and invariant sampling are separate claims. Native V40 separately qualifies bounded capability removal/restoration on the
exact owning tuple. Focus campaigns V41–V44/V46 remain failed; V44 and V46
expose a monitor-change deadline failure while the parent cover owns focus.
