module quantized_over_test {
 import quantized_over.* from "./quantized_over"
 action check(p:bool):bool=all{assert(p),s'=s}
 run quantizeAfterEveryLayerTest=init.then(pass(1,320,1,0,false,8,20,2)).then(check(s.red==100 and s.alpha==255)).then(pass(1,320,0,1,false,8,20,2)).then(check(s.red==60 and s.alpha==255)).then(pass(1,320,1,2,false,8,20,2)).then(complete).then(check(allProps and s.red==45))
 run sameReadWriteAttachmentRefusesTest=init.then(pass(1,320,0,0,false,8,20,2)).then(check(s.failed and s.prefix==0 and not(s.completed)))
 run changedOutputGenerationRefusesTest=init.then(pass(2,320,1,0,false,8,20,2)).then(check(s.failed and s.prefix==0))
 run changedBufferExtentRefusesTest=init.then(pass(1,480,1,0,false,8,20,2)).then(check(s.failed))
 run outOfOrderSourceRefusesTest=init.then(pass(1,320,1,1,false,8,20,2)).then(check(s.failed and s.draws.length()==0))
 run doubleBlendRefusesTest=init.then(pass(1,320,1,0,true,8,20,2)).then(check(s.failed))
 run resizeStartsTransparentNewPrefixTest=init.then(pass(1,320,1,0,false,8,20,2)).then(reset(2,480)).then(check(s.red==0 and s.alpha==0 and s.prefix==0 and s.generation==2))
 run incompletePrefixHasNoCompletionTest=init.then(pass(1,320,1,0,false,8,20,2)).then(check(not(s.completed) and s.prefix==1 and allProps))
 run differentOverProgramRefusesTest=init.then(pass(1,320,1,0,false,909,20,2)).then(check(s.failed and s.prefix==0))
 run copyOverProgramRoleSwapRefusesTest=init.then(pass(1,320,1,0,false,20,8,2)).then(check(s.failed and s.prefix==0))
 run sourceAliasesReadPrefixRefusesTest=init.then(pass(1,320,1,0,false,8,20,0)).then(check(s.failed and s.prefix==0))
 run sourceAliasesWritePrefixRefusesTest=init.then(pass(1,320,1,0,false,8,20,1)).then(check(s.failed and s.prefix==0))
}
