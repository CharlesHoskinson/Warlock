# Native window snapshot producer prototype

S09 producer prerequisite on the owning205/594 ancestry. The native-only producer
uses the compositor snapshot framebuffer, synchronous SHM readback, independent
RGBA storage and bounded PNG encoding. It neither supplies pixels in JSON nor
establishes a production preview lease. Authenticated QA probe commands return
metadata/checksums only, retain at most one completed CPU payload per session,
and retire it explicitly or on session retirement. Native clock, subject
incarnation, output identity/generation, session lock and rendering eligibility
are checked before and after capture. Source stop alone retains the owned bytes.

Prototype limits (128 MiB conservative owned-plane charge, two retained/progress
items, dimensions up to4096) are engineering bounds, not frozen release budgets.
Charge reserves nominal RGBA framebuffer + CPU readback + complete stored PNG
before allocation and remains conservatively charged until physical CPU release.
Driver overhead, compositor render intermediates, color management, family/modal
coverage, output transform/crop and presentation are unqualified. PNG encoding
converts bottom-up premultiplied RGBA8 into top-down straight-alpha samples.
No production profile/transfer-function claim follows from that conversion.

The probe is excluded from Elm's production actor protocol; its identifiers are
not fetchable URI tokens. Native WebKit view enrollment, authenticated FD bridge,
production broker/admission/receipts, asynchronous GPU fences, supervised shutdown,
original S09 native cases and coherent release remain open. Default installed
session is unchanged. Compilation and codec checks do not establish GUI acceptance.

434 corrects the actual432 native crash: CHLBufferReference::~ -> IHLBuffer::unlock -> inherited sendRelease dereferenced absent client resource. Internal CPU readback now overrides sendRelease; it sends no fake Wayland release and establishes no GPU/consumer fence. Crash reports are preserved; RLIMIT_CORE=1 suppressed coredump as required.

445 adds an authenticated, bounded, compositor-event-loop Unix SOCK_SEQPACKET
image descriptor channel. SO_PEERCRED PID/start/grant authenticate recipients.
Exactly one sealed memfd export per native capture is charged separately before
allocation. Retained exporter reservations survive revocation until native host
import completion. Caller attestations are trusted native bridge operations,
not frontend flags. Old hello/retire refuse outstanding imports. Lock, reload
and output removal listeners revoke completed captures without pretending that
consumer mappings have disappeared. Core unload still requires prior consumer
drain; no policy can forcibly destroy an import in another living process.
The transport carries native lifetime/clock, epochs, completed time, original
capture deadline, bounds and source presence. Full monitor plane remains ineligible
for production family/crop/color claims. Request/read clocks do not reset the
original capture deadline. Retention TTL is an explicit prototype5s bound.
