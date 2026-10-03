module renderer_terminal_test {
 import renderer_terminal.* from "./renderer_terminal"
 action check(p:bool):bool=all{assert(p),s'=s}
 action finish=retire.then(ack).then(dispose)
 run zombieExactPidfdIsTerminalTest=init.then(observe(Zombie,true,true)).then(helper(true,false)).then(finish).then(check(s.disposed and not(s.write)))
 run absentOldLifetimeIsTerminalTest=init.then(observe(Absent,true,true)).then(helper(true,false)).then(finish).then(check(s.disposed))
 run reusedPidDoesNotWriteReplacementTest=init.then(observe(Reused,true,true)).then(helper(true,false)).then(finish).then(check(s.disposed and not(s.write)))
 run liveSameLifetimeRefusesTest=init.then(observe(Live,true,true)).then(helper(true,false)).then(finish).then(check(not(s.ack)))
 run unboundTerminalWitnessRefusesTest=init.then(observe(Zombie,false,true)).then(helper(true,false)).then(finish).then(check(not(s.ack)))
 run unreadableWitnessRefusesTest=init.then(observe(Zombie,true,false)).then(helper(true,false)).then(finish).then(check(not(s.ack)))
 run modernZombieWithoutHelperClosureRefusesTest=init.then(observe(Zombie,true,true)).then(helper(false,false)).then(finish).then(check(not(s.ack)))
 run terminalRendererDoesNotClearNativeUncertaintyTest=init.then(helper(true,true)).then(observe(Zombie,true,true)).then(helper(true,false)).then(finish).then(check(s.uncertain and not(s.ack)))
 run physicalExitWithoutDurableRetiredCannotAcknowledgeTest=init.then(observe(Zombie,true,true)).then(helper(true,false)).then(ack).then(dispose).then(check(not(s.ack) and not(s.disposed)))
 run terminalSnapshotCannotBlessLaterLiveObservationTest=init.then(observe(Zombie,true,true)).then(helper(true,false)).then(retire).then(observe(Live,true,true)).then(ack).then(dispose).then(check(not(s.ack)))
}
