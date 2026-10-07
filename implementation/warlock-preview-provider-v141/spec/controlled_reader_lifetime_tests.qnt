module controlled_reader_lifetime_tests {
 import controlled_reader_lifetime.* from "./controlled_reader_lifetime"
 action check(ok:bool)=all{assert(ok and readerSafety),s'=s,reader'=reader,probed'=probed,closes'=closes}
 run closeCannotSettleReader=initReader.then(admitted).then(hold).then(event(ClosePopup)).then(event(Drain)).then(event(Retire)).then(check(reader==HeldRevoked and s.duty and s.native and not(s.retired)))
 run pendingIntentKeepsOldDuty=initReader.then(admitted).then(hold).then(event(ClosePopup)).then(event(OpenIntent)).then(event(DOMReady)).then(event(Drain)).then(event(Retire)).then(event(Replace)).then(check(reader==HeldRevoked and s.popup and s.lease==2 and s.context==1 and s.epoch==1 and s.duty))
 run unprobedReaderCannotRelease=initReader.then(admitted).then(hold).then(event(ClosePopup)).then(release).then(check(reader==HeldRevoked and closes==0 and s.duty))
 run oneReleaseCannotSettleNative=initReader.then(admitted).then(hold).then(event(ClosePopup)).then(probe).then(release).then(release).then(check(reader==Released and closes==1 and s.duty and s.native))
 run pendingIntentAfterIndependentDrain=initReader.then(admitted).then(hold).then(event(ClosePopup)).then(event(OpenIntent)).then(probe).then(release).then(event(Drain)).then(event(Retire)).then(event(Replace)).then(event(DOMReady)).then(event(Admit)).then(event(Initialize)).then(event(Apply)).then(check(reader==Released and closes==1 and s.context==2 and s.epoch==2 and s.lease==2 and s.current and s.policy==1))
 run unknownKeepsOriginalCustody=initReader.then(admitted).then(hold).then(event(ClosePopup)).then(event(Unknown)).then(probe).then(release).then(event(Drain)).then(event(Retire)).then(event(Replace)).then(check(reader==HeldRevoked and s.duty and s.native and s.context==1 and s.uncertain and closes==0))
}
