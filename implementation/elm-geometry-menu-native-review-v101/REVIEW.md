# V100 independent source review

The reviewed V100 source is held by manifest
`7a7c0ed9c3559afea1140ffb51fdc6baafaa25a5b8334d42a3e84a9b7ef479f5`.
The protected independent review passed 19 checks against actual source; the
protected final inventory verification records every reviewed V100 file and
publishes this review's separate immutable manifest. No GUI was launched and no
V100 or production source was edited. V97 remains historical and unchanged.

The QA ObserverEndpoint.request method is AST-identical to the owning captured
Endpoint.request except for its first deadline initializer:
`min(time.monotonic()+3,self.parentDeadline)`. Peer credentials, process/start and
executable identity, socket/path identity, request/reply bounds, remaining-time
checks at connect/send/shutdown/read/EOF/final parse, exact protocol/refusal schema
and Unicode reason bound are unchanged. Boundary evaluation of the actual
initializer confirms the smaller parent budget wins, the original three seconds
remain the upper bound, bootstrap infinity retains that bound, and an expired
parent remains expired. Scenario09 supplies its original six-second deadline and
restores the default in finally. No production endpoint or global clock changes.

The runner explicitly proves observer lifetime matches the Elm authority while
observer session differs. The actual native implementation keys sessions by
SO_PEERCRED PID and verified start, so observer hello/attach does not modify the
receipt child broker's binding. Observer snapshots remain diagnostic and are not
injected into Elm. Normal client quits and webview shutdown are followed by an
actual native client census returning empty before plugin unload.

The previously reviewed full09 design is retained: exact original protocol2
binding/intent and live actorB owner identify the real held Committed packet;
closed menu plus Pending/outstanding1/registry1 stay live without delivery;
actual configure/ACK/new buffer/interior serial-RGB and native facts prove restore;
real host notifications pass before unchanged receipt releaseonce. ActorA's06
receipt is forwarded by ordinal2, then exact normal EOF/retirement precedes fresh
immutable actorB ordinal1 configuration. Every original 01–10 scenario identity
and six-second transition gate remains present. No effect replay or fabricated
receipt/notification was introduced.

The initial independent test failed because it searched for a guessed assertion
label instead of the actual `observerHasIndependentPeerBinding`. Its captured
script and report are preserved. The corrected check compares the actual assertion
expression to the independent exact lifetime-equality/session-inequality oracle.
It did not change the runner.

No source blocker remains for the reviewed native launch. These are source/CPU
claims only. Full09 and all native/release acceptance remain false pending the
actual frozen tuple's serial private run, artifact/source integrity, unchanged
deadlines, normal exits and cleanup. Broader contract/roadmap completion remains
separate even if all ten bounded scenarios later pass.
