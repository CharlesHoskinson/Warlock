module focus_observation {
  type State = { phase: int, core: bool, seat: bool, coreRaw: bool, seatRaw: bool,
    firstError: bool, secondError: bool, accepted: bool, deadline: bool, effects: int }
  type Event = Start | Core(bool) | Seat(bool) | Decide | CoreError | SeatError | Timeout
  var s: State
  action init = s' = { phase: 0, core: false, seat: false, coreRaw: false,
    seatRaw: false, firstError: false, secondError: false, accepted: false,
    deadline: false, effects: 0 }
  action fire(e: Event): bool = {
    s' = match e {
      | Start => if (s.phase == 0 and not(s.deadline)) { ...s, phase: 1 } else s
      | Core(v) => if (s.phase == 1) { ...s, phase: 2, core: v, coreRaw: true } else s
      | Seat(v) => if (s.phase == 2) { ...s, phase: 3, seat: v, seatRaw: true } else s
      | Decide => if (s.phase == 3) { ...s, phase: 4, accepted: s.core and s.seat and not(s.deadline) } else s
      | CoreError => if (s.phase == 1) { ...s, phase: 5, firstError: true } else s
      | SeatError => if (s.phase == 2) { ...s, phase: 5, secondError: true } else s
      // The inherited wait observes expiry between complete polls. This model
      // makes no new claim about a reader blocked across the wall-clock bound.
      | Timeout => if (s.phase == 0 or s.phase == 4 or s.phase == 5) { ...s, deadline: true, accepted: false } else s
    }
  }
  val safe = all {
    s.effects == 0,
    not(s.seatRaw) or s.coreRaw,
    not(s.accepted) or all { s.coreRaw, s.seatRaw, s.core, s.seat, not(s.deadline), s.phase == 4 },
    not(s.secondError) or all { s.coreRaw, not(s.seatRaw), not(s.accepted) },
    not(s.firstError) or all { not(s.coreRaw), not(s.seatRaw), not(s.accepted) }
  }
  action step = nondet e = Set(Start, Core(true), Core(false), Seat(true), Seat(false),
    Decide, CoreError, SeatError, Timeout).oneOf(); fire(e)
  action check(ok: bool): bool = all { assert(ok), s' = s }
  run positivePairTest = init.then(fire(Start)).then(fire(Core(true))).then(fire(Seat(true))).then(fire(Decide)).then(check(s.accepted and s.coreRaw and s.seatRaw))
  run coreMismatchStillRetainsSeatTest = init.then(fire(Start)).then(fire(Core(false))).then(fire(Seat(true))).then(fire(Decide)).then(check(not(s.accepted) and s.coreRaw and s.seatRaw))
  run seatMismatchRetainsPairTest = init.then(fire(Start)).then(fire(Core(true))).then(fire(Seat(false))).then(fire(Decide)).then(check(not(s.accepted) and s.coreRaw and s.seatRaw))
  run bothMismatchRetainedTest = init.then(fire(Start)).then(fire(Core(false))).then(fire(Seat(false))).then(fire(Decide)).then(check(not(s.accepted) and s.coreRaw and s.seatRaw))
  run firstFailureHasNoFabricatedPairTest = init.then(fire(Start)).then(fire(CoreError)).then(fire(Decide)).then(check(s.firstError and not(s.accepted) and not(s.coreRaw) and not(s.seatRaw)))
  run secondFailurePreservesFirstTest = init.then(fire(Start)).then(fire(Core(true))).then(fire(SeatError)).then(fire(Decide)).then(check(s.secondError and s.coreRaw and not(s.accepted) and not(s.seatRaw)))
  run noSeatDecisionCannotAcceptTest = init.then(fire(Start)).then(fire(Core(true))).then(fire(Decide)).then(check(not(s.accepted)))
  run expiryCannotStartNewPollTest = init.then(fire(Timeout)).then(fire(Start)).then(fire(Core(true))).then(fire(Seat(true))).then(fire(Decide)).then(check(not(s.accepted) and not(s.coreRaw) and not(s.seatRaw)))
}
