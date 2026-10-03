module physical_code_test {
 import physical_code.* from "./physical_code"
 pure val minus={symbol:45,wire:12,xkb:20,name:45,mods:0,layout:0}
 run exactMinusPhysicalCodeTest=init.then(admit(minus)).then(check(accepted))
 run denseFirstEscapeAliasRefusedTest=init.then(admit({...minus,wire:1,xkb:9})).then(check(not(accepted)))
 run unknownLogicalSymbolRefusedTest=init.then(admit({...minus,symbol:999})).then(check(not(accepted)))
 run xkbOffsetMismatchRefusedTest=init.then(admit({...minus,xkb:12})).then(check(not(accepted)))
 run wrongPhysicalNameRefusedTest=init.then(admit({...minus,name:27})).then(check(not(accepted)))
 run modifiersRefusedTest=init.then(admit({...minus,mods:1})).then(check(not(accepted)))
 run layoutMismatchRefusedTest=init.then(admit({...minus,layout:1})).then(check(not(accepted)))
 run exactLeftPhysicalCodeTest=init.then(admit({symbol:65361,wire:105,xkb:113,name:65361,mods:0,layout:0})).then(check(accepted))
 run negativeWireRefusedTest=init.then(admit({...minus,wire:-12,xkb:-4})).then(check(not(accepted)))
 run zeroWireRefusedTest=init.then(admit({...minus,wire:0,xkb:8})).then(check(not(accepted)))
}
