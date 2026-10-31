// Bounded registration correspondence model; see README.md for actual evidence.
module current_registration {
  type RPhase = Empty | Reserved | Published | Retired
  type ScopeMode = Absent | Built | Live | Draining | Closed
  type Peer = Good | CrossUser | ForeignSession | ExpiredSession | WrongSender | WrongStart | WrongExecutable | WrongEndpoint | MixedFragments
  type Registration = { phase: RPhase, generation: int, scope: ScopeMode, busy: bool, unreaped: bool }
  type State = { first: Registration, second: Registration, nextGeneration: int, high: int, current: int,
    peer: Peer, checkedFor: int, claims: int, delivered: int, lastClaimSafe: bool, sourceFault: bool }
  var s: State
  pure val emptyReg: Registration = {phase: Empty, generation: 0, scope: Absent, busy: false, unreaped: true}
  pure def selected(x: State, who: int): Registration = if (who == 1) x.first else x.second
  pure def changed(x: State, who: int, regValue: Registration): State = if (who == 1) {...x, first: regValue} else {...x, second: regValue}
  pure def retireScope(regValue: Registration): Registration = {...regValue, scope: if (regValue.scope == Live and regValue.busy) Draining else if (regValue.scope == Live) Closed else regValue.scope}
  pure def validPeer(x: State): bool = x.peer == Good and not(x.sourceFault)
  pure def canReserve(x: State, who: int): bool = (who == 1 or who == 2) and selected(x,who).phase == Empty and x.nextGeneration > 0
  pure def doReserve(x: State, who: int): State = {
    val regValue = selected(x,who)
    val withItem = changed(x,who,{...regValue, phase: Reserved, generation: x.nextGeneration})
    {...withItem, nextGeneration: if (x.nextGeneration == 2) 0 else x.nextGeneration + 1}
  }
  pure def canInstall(x: State, who: int): bool = selected(x,who).phase == Reserved and selected(x,who).scope == Built and selected(x,who).generation > x.high
  pure def doInstall(x: State, who: int): State = {
    val revoked = if (x.current == 0) x else changed(x,x.current,retireScope(selected(x,x.current)))
    val regValue = selected(revoked,who)
    val installed = changed(revoked,who,{...regValue, phase: Published, scope: Live})
    {...installed, current: who, high: regValue.generation}
  }
  pure def doRetire(x: State, who: int): State = {
    val regValue = selected(x,who)
    val updated = changed(x,who,{...retireScope(regValue), phase: Retired})
    {...updated, current: if (x.current == who) 0 else x.current}
  }
  action init: bool = s' = {first: emptyReg, second: emptyReg, nextGeneration: 1, high: 0, current: 0, peer: Good, checkedFor: 0, claims: 0, delivered: 0, lastClaimSafe: true, sourceFault: false}
  action reserve(who: int): bool = all {canReserve(s,who), s' = doReserve(s,who)}
  // Scope construction performs observations outside registration authority lock.
  action buildScope(who: int): bool = all {selected(s,who).phase == Reserved, selected(s,who).scope == Absent,
    s' = changed(s,who,{...selected(s,who), scope: Built})}
  action install(who: int): bool = all {canInstall(s,who), s' = doInstall(s,who)}
  action retireRegistration(who: int): bool = all {who == 1 or who == 2,
    s' = doRetire(s,who)}
  // Symbolic peer/credential cases represent facts established by OS and owner.
  action present(peerValue: Peer): bool = all {s.checkedFor == 0, s' = {...s, peer: peerValue, sourceFault: false}}
  action switchFragment: bool = all {s.checkedFor == 0, s' = {...s, sourceFault: true}}
  // authenticateFragment/current is outside the final Scope admission MVar.
  action checkPeer(who: int): bool = all {s.checkedFor == 0, validPeer(s), s.current == who, selected(s,who).scope == Live, selected(s,who).unreaped,
    s' = {...s, checkedFor: who}}
  action rejectPeer(who: int): bool = all {s.checkedFor == 0, (not(validPeer(s)) or s.current != who or selected(s,who).scope != Live), s' = {...s, checkedFor: -1}}
  // Final claim and retirement use the same scope gate; callback is outside.
  action claim(who: int): bool = all {s.checkedFor == who, selected(s,who).scope == Live, not(selected(s,who).busy),
    s' = {...changed(s,who,{...selected(s,who), busy: true}), checkedFor: 0, claims: s.claims + 1,
      lastClaimSafe: s.current == who and validPeer(s) and selected(s,who).unreaped}}
  action refuseClaim(who: int): bool = all {s.checkedFor == who, selected(s,who).scope != Live,
    s' = {...s, checkedFor: -1}}
  action callbackDone(who: int): bool = all {selected(s,who).busy, selected(s,who).unreaped,
    s' = {...changed(s,who,{...selected(s,who), busy: false, scope: if (selected(s,who).scope == Draining) Closed else selected(s,who).scope}), delivered: s.delivered + 1}}
  action reap(who: int): bool = all {selected(s,who).scope == Closed, not(selected(s,who).busy), selected(s,who).unreaped,
    s' = changed(s,who,{...selected(s,who), unreaped: false})}
  // Concrete bounded exhaustion fixture; normal generation maximum is Word64.
  action nearExhaustion: bool = all {s.first.phase == Empty, s.second.phase == Empty, s.nextGeneration == 1, s.high == 0,
    s' = {...s, nextGeneration: 2}}
  val oneLive: bool = not(s.first.scope == Live and s.second.scope == Live)
  val currentIsPublished: bool = s.current == 0 or (selected(s,s.current).phase == Published and selected(s,s.current).scope == Live)
  val claimWasCurrent: bool = s.claims == 0 or s.lastClaimSafe
  val noReapInFlight: bool = (s.first.busy implies s.first.unreaped) and (s.second.busy implies s.second.unreaped)
  val monotoneHigh: bool = s.current == 0 or selected(s,s.current).generation == s.high
  // Mutants are deliberately excluded from normal step.
  action brokenPublishBeforeRevoke(who: int): bool = all {canInstall(s,who), s.current != 0,
    s' = {...changed(s,who,{...selected(s,who), phase: Published, scope: Live}), current: who, high: selected(s,who).generation}}
  action brokenOldCleanup: bool = all {s.current == 2, s.first.phase == Published,
    s' = {...doRetire(s,1), current: 0}}
  action brokenUidOnly(who: int): bool = all {selected(s,who).scope == Live, s.peer == WrongSender,
    s' = {...s, claims: s.claims + 1, lastClaimSafe: false}}
  action brokenCreatorOnly(who: int): bool = all {selected(s,who).scope == Live, s.peer == WrongSender,
    s' = {...s, claims: s.claims + 1, lastClaimSafe: false}}
  action brokenStaleClaim(who: int): bool = all {s.checkedFor == who, selected(s,who).scope != Live,
    s' = {...s, claims: s.claims + 1, lastClaimSafe: false}}
  action step: bool = any {reserve(1),reserve(2),buildScope(1),buildScope(2),install(1),install(2),retireRegistration(1),retireRegistration(2),
    present(Good),present(CrossUser),present(ForeignSession),present(ExpiredSession),present(WrongSender),present(WrongStart),present(WrongExecutable),present(WrongEndpoint),present(MixedFragments),
    switchFragment,checkPeer(1),checkPeer(2),rejectPeer(1),rejectPeer(2),claim(1),claim(2),refuseClaim(1),refuseClaim(2),callbackDone(1),callbackDone(2),reap(1),reap(2),nearExhaustion}
  val liveIsCurrent = (s.first.scope == Live implies s.current == 1) and (s.second.scope == Live implies s.current == 2)
  val safety = oneLive and currentIsPublished and liveIsCurrent and claimWasCurrent and noReapInFlight and monotoneHigh
  val witnessReserved = s.first.phase == Reserved or s.second.phase == Reserved
  val witnessBuilt = s.first.scope == Built or s.second.scope == Built
  val witnessLive = s.first.scope == Live or s.second.scope == Live
  val witnessChecked = s.checkedFor > 0
  val witnessClaim = s.claims > 0
  val witnessDelivered = s.delivered > 0
  val witnessRetired = s.first.phase == Retired or s.second.phase == Retired
  val witnessReaped = not(s.first.unreaped) or not(s.second.unreaped)
  val witnessExhausted = s.nextGeneration == 0
  val witnessRefused = s.checkedFor == -1
  val witnessMixed = s.sourceFault
}
