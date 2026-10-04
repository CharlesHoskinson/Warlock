# Negotiated prospective geometry authority

Additive GC001–008/OpenSpec402 applies before source changes. Geometry observation
version2 adds a strict sizePolicy object containing inputs, maximize and restoreGeometry. The inputs fields are profile, rawMinimum/rawMaximum,
layoutMinimum/layoutMaximum, geometryOrigin, reservedTopLeft/reservedBottomRight,
monitorScale. Maximize/restore projections contain logical/visual/real/configure boxes.
An unavailable conversion has null sizePolicy and disables both capabilities.
Version1 retains its broad constrained-size rejection and field shape. Each
session binds its negotiated observation version to its frontend epoch; facts
requests with another version refuse. Effect protocol2 and schema5 keys retain
original semantics. A single canonical version2 fingerprint drives revisions,
including live bound/conversion changes; observing version1 must not toggle it.

When a version2 effect is admitted, the authority shall evaluate the exact
prospective target before mutation and retain its conversion-input fingerprint.
If live conversion inputs or exact target/real/configure readback disagree after
callbacks, then the outcome shall remain Unknown with the original retained.
Native mode commit does not prove client ACK or pixel acceptance. Version1
clients cannot use newly enabled version2 constrained-window operations.

Given GTK minimum108x42/unbounded maxima/zero origin and a fitting decorated
workarea, version2 size policy can enable Max while version1 stays refused.
Given a raw or layout bound below the required target, fixed axis, unsupported
origin, stale revision, unknown barrier or peer/focus mismatch, no new mutation
is authorized. Ordinary restore uses exact saved logical geometry, checks its
prospective real box equals saved visual geometry, and never recaptures it.

Compiler/closure checks do not qualify native loading. Require fresh owning
core89/plugin pair and protocol/typed-consumer fixtures before GTK configure/
ACK/RGB, peer preservation, shared multi-action and original08/09/10 campaigns.

GC009 amendment: effective fixed status includes the intersection in integer configure space; 168 counterexamples must refuse. A sizePolicy object always contains inputs/maximize/restoreGeometry; inputs:null means unavailable or invalid bounds. A finite nonzero origin may be observed in inputs with both projections null, and cannot authorize any capability. The profile name alone is not supported-operation evidence.
