GUI112 adds readonly recovery of the original controlled native realm after
JavaScript context loss. It retains the Native binding, receiver epoch, issued,
delivered and independently confirmed prefixes, immutable original tickets and
all purpose/physical/proof/Unknown obligations. It never replaces the Native
grant, creates an ordinal or invokes a control while inventorying recovery.

ControlReservations::recover returns at most one original unconfirmed ticket
and native prefixes without mutation. The C begin API validates creator thread,
original popup and sender epoch and starts at the native confirmed prefix. Each
next page requires the same captured issued/delivered/confirmed frontiers and
original epoch, rejecting changed progress before inventory. Pages are bounded
to16384 bytes with one original4096-byte ticket; no aggregate unbounded message
or new recovery counter is used. In-flight dispatch and positions outside the
current confirmed-to-issued interval refuse. An exhausted issued frontier never
wraps because its next increment is conditional on after<issued.

The new recovered-native-preview-control-outbox.js constructor checks complete,
contiguous, consistently bound pages and every original ticket before returning
an object. It prepares original confirmed state and queues only native tickets
above it. Construction emits neither data nor confirmation; the host's next
bounded poll retries the original oldest wire. Native delivered-but-unconfirmed
tickets remain queued and repeat only their original receipt. Complete confirmed
prefix can rehydrate without replaying data. Every transport confirmation remains
separate from application/Elm or physical settlement. A new JavaScript context
cannot recover the missing Elm model or replay Unknown effects from this page
inventory alone. The exact Native grant and native realm remain owned throughout.

Current evidence:
- qa/native-outbox-recovery-check-v3-1791355285169842681/report.json passes129
  actual sanitizer-backed controlled C/Bootstrap/Native authenticated socket/
  Broker/ReceiptDelivery and JS checks. Two isolated new JS VMs recover original
  native prefixes/tickets; a native-issued pending neighbor survives lost context,
  first native receipt and confirmation loss remain separate, two same-Active-
  subject epochs strictly close on the unchanged Native grant. Inconsistent or
  incomplete pages emit no data; original C refuses stale prefix and foreign
  epoch. Peers and fixture exit normally. These are synthetic native applications
  and JavaScript VM recreation, not actual Core/Wayland/WebKit context reload.
- qa/recovered-pages-model-check-v3-1791355359626645528/report.json passes24
  selected Quint scenarios/36 actual JS traces/498 state comparisons/200 bounded
  samples. Frontiers, queue occupancy, ordered data/confirmation attempts and
  operation outcomes are compared; constructor callbacks are separately observed
  before the new object is installed. Native issuance is a trace fixture. The
  lastKnown flag tracks whether this fresh JS context actually retained the last
  delivered wire, distinct from native confirmation recovery. Nine executable
  variants fail exact observations, including early constructor post, mixed
  recovery prefix and wrong page position in addition to the original six.
- Current98-command full host build retains every original97 plus recovered
  outbox syntax. All four original resource/capture/ticket/FD regressions pass
  against the changed current native bank/C source. All four current scoped-detachment
  regressions also pass:original C77/FD60+64+51/cohort66/model21/33/715/five guard
  variants, retaining normal exits and original physical/proof barriers.
- qa/recovery-native-variants-v2-1791355389638849943/report.json compiles three
  native variants; each fails its unchanged named actual C/JS witness:allowing
  stale captured confirmed prefix, foreign epoch and changed recovered bytes.

Three failed fixtures are retained: the two-ticket driver incorrectly attributed
actual cancellation cleanup to confirmation; its fresh derivative checks the
unchanged physical assertion before that independently invoked cancellation.
The first recovery model assumed a new context retained a past wire it had never
seen; its fresh model tracks that distinct state and compares actual results.
The first unsafe native variant did not compile after removing a parameter use;
a fresh variant retains that use while weakening the corresponding guard. No
product guard or original physical assertion/deadline was relaxed.

Existing Elm policy/src/adapter and legacy host routes stay unchanged. Neither
new outbox is activated by popup.html. Actual WebKit callback/ref ownership,
typed incoming/outgoing host realm channels, full Elm recovery and controlled
Core/capture/FD/Wayland-window integration remain required. Native130 current
GUI110 legacy/core16/plugin19/AQ155 remains2518/278/full cleanup. GUI111 is public80
620566103509a1469c6d75401f753dc32a4bcb3c; source
 d8a51e4141fe3d7d7eb033002fdf37594f23060c, receipt
 d029415cf596ad30892b1fe3e8ed851fa3bf89d7. Full release remains incomplete.
