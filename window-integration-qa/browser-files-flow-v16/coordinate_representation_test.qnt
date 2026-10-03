module coordinate_representation_test {
 import coordinate_representation.* from "./coordinate_representation"
 run integerExactTest=init.then(all{assert(wire(605,1)==605*256),step})
 run halfAwayTest=init.then(all{assert(wire(1025,512)==513),step})
 run belowHalfTest=init.then(all{assert(wire(2049,1024)==512),step})
 run aboveHalfTest=init.then(all{assert(wire(2051,1024)==513),step})
 run fractionalExactTest=init.then(all{assert(wire(4097,256)==4097),step})
 run zeroDenominatorRefusedTest=init.then(all{assert(not(valid(1,0))),step})
 run surfaceEdgeRefusedTest=init.then(all{assert(not(valid(0,1)) and not(valid(1600,1))),step})
 run integerInteriorTest=init.then(all{assert(inside(286,285*256+244,747*256+244)),step})
 run fractionalCommandNotInteriorAuthorityTest=init.then(all{assert(not(inside(285,285*256+244,747*256+244))),step})
}
