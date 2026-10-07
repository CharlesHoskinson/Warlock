# Native read-only visual custody

GUI118 adds a creator-owned getter returning a detached `g_malloc` string from
the last successfully processed private output. It copies only the six typed
visual fields. It calls no JavaScript and advances no policy, effect or ordinal.
The original policy implementation, native issuer and physical authority remain
unchanged. A caller must free its copy and conceal on refusal.

Missing owners/destinations refuse INVALID_INPUT; foreign threads refuse
WRONG_THREAD; inflight or uncertain processing refuses PROCESSING_UNKNOWN;
absent or closed control authority refuses NO_VISUAL_AUTHORITY. Ordinary input
backpressure preserves the last committed projection. The getter neither accepts
refused inputs nor releases known jobs, proposals or physical resources.

Qualification retains the original207 native C/JSC controls plus90 visual
comparisons and adds74 read-only comparisons, with two native epochs, one
persistent policy, two transport contexts and normal owned exits. Lifetime
qualification retains37 original boundaries and13 pre-grant constructor faults,
adds15 readonly boundaries, executes14 selected Quint scenarios and26 actual
C/JSC traces/430 states with200 invariant samples, and detects five compiled
native guard variants. Caller-mutated copies do not alter subsequent reads.
Backpressure retains48 original controls and adds28 exact visual comparisons;
ticket/terminal/close inputs in that fixture remain explicitly synthetic.

This is committed data custody, not a freshness or authenticated delivery channel.
Actual renderer leases, monotonic delivery, context/reload concealment, durable
host input/ticket custody, delayed proposal outcome/order and uncertain worker
recovery remain open. Actual WebKit/Core/DOM/URI/captured-resource acceptance and
all original full release gates remain separate. The host route is inactive;
Native130 GUI110 legacy2518/278 remains the actual bounded native baseline.
