module pointer_syntax_test {
 import pointer_syntax.* from "./pointer_syntax"
 pure val good={x:Integer(605),y:Integer(450),exactTwo:true}
 run exactIntegersTest=init.then(send(good)).then(all{assert(wrote),init})
 run fractionalFirstRefusedTest=init.then(send({...good,x:Fractional})).then(all{assert(not(wrote)),init})
 run fractionalSecondRefusedTest=init.then(send({...good,y:Fractional})).then(all{assert(not(wrote)),init})
 run missingFirstRefusedTest=init.then(send({...good,x:Missing})).then(all{assert(not(wrote)),init})
 run missingSecondRefusedTest=init.then(send({...good,y:Missing})).then(all{assert(not(wrote)),init})
 run extraTokenRefusedTest=init.then(send({...good,exactTwo:false})).then(all{assert(not(wrote)),init})
 run nonfiniteRefusedTest=init.then(send({...good,x:Nonfinite})).then(all{assert(not(wrote)),init})
 run booleanRefusedTest=init.then(send({...good,x:Boolean})).then(all{assert(not(wrote)),init})
 run negativeRefusedTest=init.then(send({...good,x:Integer(-1)})).then(all{assert(not(wrote)),init})
 run xExtentRefusedTest=init.then(send({...good,x:Integer(1600)})).then(all{assert(not(wrote)),init})
 run yExtentRefusedTest=init.then(send({...good,y:Integer(1000)})).then(all{assert(not(wrote)),init})
 run injectionTextRefusedTest=init.then(send({...good,y:Text})).then(all{assert(not(wrote)),init})
}
