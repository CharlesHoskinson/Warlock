module retained_client_command_tests {
 import retained_client_command.* from "./retained_client_command"
 action check(accepted:bool,legacy:bool):bool=all{assert(s.accepted==accepted and s.legacy==legacy and safety),s'=s}
 run readyOriginalPacket=init.then(fire(Ready)).then(check(true,true))
 run lateOriginalOfferCleanup=init.then(fire(LateOffer)).then(check(true,false))
 run frontendTrueCannotGrantNativeReadiness=init.then(fire(NativeUnreadyTrue)).then(check(false,false))
 run frontendFalseCannotGrantNativeReadiness=init.then(fire(NativeUnreadyFalse)).then(check(false,false))
 run unownedPacketRefused=init.then(fire(Unowned)).then(check(false,false))
 run foreignJobRefused=init.then(fire(BadJob)).then(check(false,false))
 run foreignHandleRefused=init.then(fire(BadHandle)).then(check(false,false))
 run rewrittenExpiryRefused=init.then(fire(BadExpiry)).then(check(false,false))
 run rewrittenCoverageRefused=init.then(fire(BadCoverage)).then(check(false,false))
 run malformedFlagRefused=init.then(fire(FlagType)).then(check(false,false))
 run missingNativePacketRefused=init.then(fire(MissingPacket)).then(check(false,false))
 run foreignIdentityRefused=init.then(fire(BadIdentity)).then(check(false,false))
 run duplicateFlagRefused=init.then(fire(DuplicateFlag)).then(check(false,false))
 run extraFieldRefused=init.then(fire(ExtraField)).then(check(false,false))
}
