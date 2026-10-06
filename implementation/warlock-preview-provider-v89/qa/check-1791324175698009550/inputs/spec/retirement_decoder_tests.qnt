module retirement_decoder_tests {
 import retirement_decoder.* from "./retirement_decoder"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run freshNativeActive=init.then(fire(Active)).then(check(s.accepted==1 and s.status=="Active"))
 run laterNativeRetired=init.then(fire(Active)).then(fire(Retired)).then(check(s.sequence==2 and s.status=="Retired"))
 run futureZeroFrontier=init.then(fire(FutureZero)).then(check(s.status=="Future" and s.issued==0))
 run foreignBindingRefused=init.then(fire(Active)).then(fire(WrongBinding)).then(check(s.sequence==1 and s.status=="Invalid"))
 run foreignClockRefused=init.then(fire(Active)).then(fire(WrongClock)).then(check(s.sequence==1 and s.status=="Invalid"))
 run wrongRequestRefused=init.then(fire(WrongRequest)).then(check(s.accepted==0))
 run wrongSubjectRefused=init.then(fire(WrongSubject)).then(check(s.accepted==0))
 run replayCannotAdvanceCursor=init.then(fire(Active)).then(fire(Replay)).then(check(s.sequence==1 and s.accepted==1))
 run backwardClockCannotAdvanceCursor=init.then(fire(Active)).then(fire(EarlierNow)).then(check(s.now==10 and s.sequence==1))
 run backwardFrontierCannotAdvanceCursor=init.then(fire(Active)).then(fire(EarlierFrontier)).then(check(s.issued==3 and s.sequence==1))
 run retiredAboveFrontierRefused=init.then(fire(RetiredAbove)).then(check(s.accepted==0))
 run futureBelowFrontierRefused=init.then(fire(FutureBelow)).then(check(s.accepted==0))
 run unknownStateRefused=init.then(fire(Unknown)).then(check(s.accepted==0))
}
