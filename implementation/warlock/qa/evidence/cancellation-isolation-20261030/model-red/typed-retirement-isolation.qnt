// Contract proposal: finite opaque full-key identity classes, not protocol numbers.
module TypedRetirementIsolation {
  type Lane = Legacy | Typed
  type Phase = NoRelease | Prepared | Released
  type TypedStage = Unknown | TerminalStored | AdmissionRetired
  type Entry = { lane: Lane, file: bool, live: bool, phase: Phase,
                 stage: TypedStage, cert: bool, ack: bool }
  type State = { entries: int -> Entry, proofs: Set[int], joins: Set[int],
                 decoderHealthy: bool, replayCount: int }
  val keys = Set(1, 2, 3)
  // 1 is legacy, 2 is typed, 3 is a distinct typed sibling. All may use protocol 1.
  var s: State
  pure def entry(lane: Lane): Entry =
    { lane: lane, file: true, live: true, phase: NoRelease,
      stage: Unknown, cert: false, ack: false }
  pure def legacyEligible(st: State, k: int): bool =
    st.decoderHealthy and validPersisted(st) and st.entries.get(k).lane == Legacy and
    st.entries.get(k).live and st.entries.get(k).file and
    st.entries.get(k).phase == NoRelease and st.proofs.contains(k) and st.joins.contains(k)
  pure def safeFinish(st: State, k: int): bool =
    st.decoderHealthy and validPersisted(st) and st.entries.get(k).lane == Legacy and
    st.entries.get(k).live and st.entries.get(k).phase == Prepared
  pure def validPersisted(st: State): bool =
    keys.forall(k => st.entries.get(k).lane != Typed or st.entries.get(k).phase == NoRelease)
  pure def legacyRecords(st: State): Set[int] =
    keys.filter(k => st.entries.get(k).lane == Legacy and st.entries.get(k).live)
  action init: bool = all {
    s' = { entries: Map(1 -> entry(Legacy), 2 -> entry(Typed), 3 -> entry(Typed)),
           proofs: Set(), joins: Set(), decoderHealthy: true, replayCount: 0 }
  }
  // Proof and observation join concern the exact key; they do not confer typed authority.
  action observeProof(k: int): bool = all {
    keys.contains(k), s.decoderHealthy, s' = { ...s, proofs: s.proofs.union(Set(k)) }
  }
  action observeJoin(k: int): bool = all {
    s.decoderHealthy, s.proofs.contains(k), s' = { ...s, joins: s.joins.union(Set(k)) }
  }
  action legacyPrepare(k: int): bool = all {
    legacyEligible(s, k),
    s' = { ...s, entries: s.entries.set(k, { ...s.entries.get(k), phase: Prepared }) }
  }
  action legacyFinish(k: int): bool = all {
    safeFinish(s, k),
    s' = { ...s, entries: s.entries.set(k, { ...s.entries.get(k), file: false, live: false, phase: Released }) }
  }
  action legacyAck(k: int): bool = all {
    s.decoderHealthy, s.entries.get(k).lane == Legacy, s.entries.get(k).phase == Released,
    s' = { ...s, entries: s.entries.set(k, { ...s.entries.get(k), ack: true }) }
  }
  action exactTerminal(k: int, certificateKey: int): bool = all {
    keys.contains(k), s.decoderHealthy, s.entries.get(k).lane == Typed,
    s.entries.get(k).live, s.entries.get(k).file, k == certificateKey,
    s.entries.get(k).stage == Unknown,
    s' = { ...s, entries: s.entries.set(k, { ...s.entries.get(k), cert: true, stage: TerminalStored }) }
  }
  action typedFinish(k: int): bool = all {
    s.decoderHealthy, validPersisted(s), s.entries.get(k).lane == Typed, s.entries.get(k).live,
    s.entries.get(k).file, s.entries.get(k).stage == TerminalStored, s.entries.get(k).cert,
    s' = { ...s, entries: s.entries.set(k, { ...s.entries.get(k), file: false, live: false, stage: AdmissionRetired }) }
  }
  action typedAck(k: int): bool = all {
    s.decoderHealthy, s.entries.get(k).lane == Typed, s.entries.get(k).cert,
    s.entries.get(k).stage == AdmissionRetired,
    s' = { ...s, entries: s.entries.set(k, { ...s.entries.get(k), ack: true }) }
  }
  // External persisted collision represents corrupt/older prepared data, not a normal transition.
  action injectCollision(k: int): bool = all {
    s.decoderHealthy, s.entries.get(k).lane == Typed, s.entries.get(k).live,
    s' = { ...s, entries: s.entries.set(k, { ...s.entries.get(k), phase: Prepared }) }
  }
  action restart: bool = all {
    s.decoderHealthy,
    s' = { ...s, decoderHealthy: validPersisted(s), proofs: Set(), joins: Set() }
  }
  // Historical broken route: the save refuses only AFTER the file is removed.
  // Deliberately excluded from step, used solely to show the counterexample.
  action brokenPrepare(k: int): bool = all {
    s.decoderHealthy, s.entries.get(k).live, s.proofs.contains(k), s.joins.contains(k),
    s' = { ...s, entries: s.entries.set(k, { ...s.entries.get(k), phase: Prepared }) }
  }
  action brokenFinish(k: int): bool = all {
    s.decoderHealthy, s.entries.get(k).lane == Typed, s.entries.get(k).phase == Prepared,
    s' = { ...s, decoderHealthy: false,
      entries: s.entries.set(k, { ...s.entries.get(k), file: false }) }
  }
  val typedCustody = keys.forall(k => s.entries.get(k).lane == Typed and not(s.entries.get(k).file) implies s.entries.get(k).cert)
  val ackAfterRetirement = keys.forall(k => s.entries.get(k).ack implies
    (if (s.entries.get(k).lane == Typed) s.entries.get(k).cert and s.entries.get(k).stage == AdmissionRetired
     else s.entries.get(k).phase == Released))
  val noReplay = s.replayCount == 0
  val projectedLegacyOnly = legacyRecords(s).forall(k => s.entries.get(k).lane == Legacy)
  action step: bool = any {
    observeProof(1), observeProof(2), observeProof(3),
    observeJoin(1), observeJoin(2), observeJoin(3),
    legacyPrepare(1), legacyPrepare(2), legacyPrepare(3),
    legacyFinish(1), legacyFinish(2), legacyFinish(3), legacyAck(1),
    exactTerminal(2,2), exactTerminal(3,3), typedFinish(2), typedFinish(3),
    typedAck(2), typedAck(3), injectCollision(2), injectCollision(3), restart
  }
}
