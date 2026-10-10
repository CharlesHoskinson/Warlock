module shortcut_output_test {
 import shortcut_output.* from "./shortcut-output"
 run currentRightOutputTest=init.then(press(2)).then(receive).then(all{assert(rightOpened and safety),s'=s})
 run retiredDestinationTest=init.then(press(2)).then(retire(2)).then(receive).then(all{assert(retiredRejected and s.owner==1 and safety),s'=s})
 run replacedDestinationTest=init.then(press(2)).then(replace(2)).then(receive).then(all{assert(s.refused==1 and s.opened==0 and s.owner==1 and safety),s'=s})
 run movedDestinationTest=init.then(press(2)).then(moveNative(2)).then(receive).then(all{assert(s.refused==1 and s.opened==0 and safety),s'=s})
 run ambiguousDestinationTest=init.then(press(2)).then(mirror).then(receive).then(all{assert(ambiguousRejected and s.owner==1 and safety),s'=s})
 run blockedDestinationTest=init.then(press(2)).then(block).then(receive).then(all{assert(blockedRejected and s.owner==1 and safety),s'=s})
 run duplicateCannotRelocateTest=init.then(press(2)).then(receive).then(mirror).then(all{assert(s.seen==s.event and s.opened==1 and s.owner==2 and safety),s'=s})
}
