# Native child-only qualification fixture

Additive to original preview13 and the frozen sampled-tree revision contract.
This fixture is an isolated Wayland client; it supplies observable native state,
never production authority or a second Elm policy.

- CHILD-01: WHEN a desynchronized child alone applies a new buffer, the campaign
  SHALL observe an advanced native client context, reject the prior context and
  independently decode the new child pixels without an artificial root commit.
- CHILD-02: WHILE a synchronized child change is queued without its parent
  applying it, capture SHALL retain the applied context and prior child pixels;
  WHEN the parent applies that change, the context and pixels SHALL advance.
- CHILD-03: WHEN position, stacking or nested child membership changes apply,
  capture SHALL preserve the actual accumulated geometry and applied paint order.
- CHILD-04: WHEN a child detaches or its surface/role is destroyed and replaced,
  the native context SHALL advance or become unavailable without retargeting the
  retired resource. Independent pixels SHALL exclude retired child content.
- CHILD-05: WHEN the fixture and producer retire, the campaign SHALL verify
  consumer mapping/FD closure, exact export release, producer retirement, no live
  client before unload, normal process exits and private-runtime cleanup.

Derive protocol and buffer ownership from the reviewed xdg-origin-fixture-v184
source. Retain its bounded allocation and native acknowledgement/barrier facts.
Use the exact applied-revision-core-v2/source-revisions-v1/AQ155 tuple, the shared
native lock and unchanged protected launcher. Preserve original two-second
capture and three-second IPC deadlines. An unrelated overlapping peer must never
enter client pixels. No production eligibility, family coverage or full release
claim follows from fixture/component tests.

Omarchy command/binding adoption remains mandatory and separate. Native fixture
placement uses installed typed Lua dispatcher constructors with unchanged user
configuration; no main-desktop reload or activation is authorized by this fixture.
