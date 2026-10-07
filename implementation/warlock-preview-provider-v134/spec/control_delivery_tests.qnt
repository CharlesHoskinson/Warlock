module control_delivery_tests {
 import control_delivery.* from "./control_delivery"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run lostReceiptRetriesWithoutEffect=init.then(fire(Packet1)).then(fire(Finish)).then(fire(Packet1)).then(check(s.decision==2 and s.invoked==1 and s.receipt==1))
 run changedPacketCannotReuseOrdinal=init.then(fire(Packet1)).then(fire(Finish)).then(fire(Packet1Changed)).then(check(s.decision==0 and s.invoked==1))
 run inFlightPacketCannotReenter=init.then(fire(Packet1)).then(fire(Packet1)).then(check(s.decision==0 and s.invoked==1 and s.receipt==0))
 run missingPacketCannotBeSkipped=init.then(fire(Packet2)).then(check(s.decision==0 and s.invoked==0))
 run foreignReceiverCannotEnter=init.then(fire(WrongReceiver)).then(check(s.decision==0 and s.invoked==0))
 run foreignEpochCannotEnter=init.then(fire(WrongEpoch)).then(check(s.decision==0 and s.invoked==0))
 run foreignBindingCannotEnter=init.then(fire(WrongBinding)).then(check(s.decision==0 and s.invoked==0))
 run reloadCannotResetPrefix=init.then(fire(Packet1)).then(fire(Finish)).then(fire(Reinitialize)).then(check(s.decision==0 and s.delivered==1 and s.invoked==1))
 run finalOrdinalRetriesWithoutWrap=init.then(fire(Boundary)).then(fire(PacketMax)).then(fire(Finish)).then(fire(PacketMax)).then(check(s.decision==2 and s.invoked==1)).then(fire(Wrap)).then(check(s.decision==0 and s.delivered==maximum))
 run deliveryReceiptDoesNotOvertakeHandler=init.then(fire(Packet1)).then(fire(WrongFinish)).then(check(s.decision==0 and s.inFlight and s.receipt==0)).then(fire(Finish)).then(check(s.receipt==1))
 run laterDeliveryRejectsEarlierReplay=init.then(fire(Packet1)).then(fire(Finish)).then(fire(Packet2)).then(fire(Finish)).then(fire(Packet1)).then(check(s.decision==0 and s.delivered==2 and s.invoked==2))
 run malformedSizeCannotEnter=init.then(fire(Empty)).then(fire(Oversize)).then(check(s.invoked==0 and s.delivered==0))
}
