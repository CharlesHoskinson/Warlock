module physical_keyboard_test {
 import physical_keyboard.* from "./physical_keyboard"
 run planBeforeConnectionRequiredTest=init.then(fire(Connect({live:true,peer:true}))).then(fire(Press)).then(check(failed and presses==0))
 run denseEscapeAliasRefusedTest=init.then(fire(Plan({valid:true,physical:false}))).then(fire(Connect({live:true,peer:true}))).then(fire(Press)).then(check(failed and presses==0))
 run invalidTextNoSendTest=init.then(fire(Plan({valid:false,physical:true}))).then(fire(Press)).then(check(failed and presses==0))
 run peerMismatchNoSendTest=init.then(fire(Plan({valid:true,physical:true}))).then(fire(Connect({live:true,peer:false}))).then(fire(Press)).then(check(failed and presses==0))
 run changedLifetimeNoSendTest=init.then(ready).then(fire(Change)).then(fire(Press)).then(check(failed and presses==0))
 run keymapBeforePressTest=init.then(fire(Plan({valid:true,physical:true}))).then(fire(Connect({live:true,peer:true}))).then(fire(Press)).then(check(failed and presses==0))
 run missingKeymapAckNoSendTest=init.then(fire(Plan({valid:true,physical:true}))).then(fire(Connect({live:true,peer:true}))).then(fire(KeymapReady({valid:true,eof:false}))).then(fire(Press)).then(check(failed and presses==0))
 run exactPairOrderTest=init.then(ready).then(pair).then(check(presses==1 and releases==1 and index==1 and not(held)and not(failed)))
 run duplicatePressRefusedTest=init.then(ready).then(fire(Press)).then(fire(Press)).then(check(failed and presses==1 and held))
 run releaseWithoutPressRefusedTest=init.then(ready).then(fire(Release)).then(check(failed and releases==0))
 run advanceHeldRefusedTest=init.then(ready).then(fire(Press)).then(fire(Advance)).then(check(failed and index==0))
 run partialFailureNeverRetriesTest=init.then(ready).then(pair).then(fire(Error)).then(fire(Press)).then(check(failed and presses==1 and releases==1 and not(complete)))
 run partialHoldFailureSendsNoFurtherReleaseTest=init.then(ready).then(fire(Press)).then(fire(Error)).then(fire(Release)).then(fire(Press)).then(check(failed and presses==1 and releases==0 and held))
 run finishCannotInventMissingCharacterTest=init.then(ready).then(pair).then(fire(Finish)).then(check(failed and not(complete)))
 run exactlyElevenPairsCompleteOriginalPlanTest=init.then(ready).then(pair).then(pair).then(pair).then(pair).then(pair).then(pair).then(pair).then(pair).then(pair).then(pair).then(pair).then(fire(Finish)).then(check(complete and presses==11 and releases==11 and index==11 and not(held)))
}
