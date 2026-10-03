module exit_ack_test {
 import exit_ack.* from "./exit_ack"
 run explicitExitTest=init.then(request).then(acknowledge).then(stop).then(exit).then(all {assert(ack and exited),exit})
 run beforeAckQuitRefusedTest=init.then(request).then(all {assert(not(canQuit)),acknowledge})
 run ackBeforeQuitTest=init.then(request).then(acknowledge).then(all {assert(ack and not(quit)),stop})
 run noRequestEOFTest=init.then(stop).then(exit).then(all {assert(exited and not(ack)),exit})
 run localVFSNoDaemonTest=init.then(fileInit).then(all {assert(not(activated)),fileInit})
 run repeatedFileInitNoDaemonTest=init.then(fileInit).then(fileInit).then(all {assert(not(activated)),fileInit})
}
