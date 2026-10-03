module callback_fixture_completion_test {
 import callback_fixture_completion.* from "./callback_fixture_completion"
 action check(p:bool):bool=all{assert(p),s'=s}
 run failedCueWithoutReceiptRefusesTest=init.then(fire(Failure)).then(fire(Inspect)).then(check(s.failed and s.receipts==0 and not(s.accepted) and allProps))
 run startedCallbackWithoutReceiptRefusesTest=init.then(fire(Failure)).then(fire(StartCallback)).then(fire(Inspect)).then(check(not(s.accepted) and allProps))
 run exactlyOneGenuineReceiptPassesTest=init.then(fire(Failure)).then(fire(StartCallback)).then(fire(ReturnCallback)).then(fire(Inspect)).then(check(s.accepted and allProps))
 run duplicateReceiptNeverPassesExactAssertionTest=init.then(fire(Failure)).then(fire(StartCallback)).then(fire(ReturnCallback)).then(fire(Duplicate)).then(fire(Inspect)).then(check(not(s.accepted) and allProps))
 run callbackWithoutFailureHasNoReceiptAuthorityTest=init.then(fire(StartCallback)).then(fire(ReturnCallback)).then(fire(Inspect)).then(check(not(s.accepted) and allProps))
 run failedSendStillRefusesTest=init.then(fire(Failure)).then(fire(StartCallback)).then(fire(ReturnCallback)).then(fire(Send)).then(check(s.sendRefused and allProps))
 run failedNormalCloseStillRefusesTest=init.then(fire(Failure)).then(fire(StartCallback)).then(fire(ReturnCallback)).then(fire(Close)).then(check(s.normalCloseRefused and allProps))
 run lateCallbackCannotBorrowNewDeadlineTest=init.then(fire(Failure)).then(fire(StartCallback)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(Tick)).then(fire(ReturnCallback)).then(fire(Inspect)).then(check(s.expired and not(s.accepted) and allProps))
}
