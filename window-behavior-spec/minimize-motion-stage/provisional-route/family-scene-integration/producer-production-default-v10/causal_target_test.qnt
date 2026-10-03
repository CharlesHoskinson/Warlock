module causal_target_test {
 import causal_target.* from "./causal_target"
 action check(p:bool):bool=all{assert(p),s'=s}
 run defaultCopyBeforeBothReadsTest=init.then(copy(1,320,3,0,false)).then(read(false,0,6408,false)).then(read(true,0,32993,false)).then(check(not(s.failed) and s.reads==List(6408,32993) and allProps))
 run rawPrefixCannotReadBeforeDefaultCopyTest=init.then(read(false,202,6408,false)).then(check(s.failed and s.reads.length()==0 and allProps))
 run wrongCopyTargetRefusesTest=init.then(copy(1,320,3,202,false)).then(check(s.failed and s.reads.length()==0))
 run fboNativePairCannotSubstituteDefaultPairTest=init.then(copy(1,320,3,0,false)).then(read(true,0,6408,false)).then(check(s.failed and s.reads.length()==0))
 run oldGenerationCopyRefusesTest=init.then(copy(2,320,3,0,false)).then(check(s.failed and s.copyPrefix==0))
 run oldExtentCopyRefusesTest=init.then(copy(1,480,3,0,false)).then(check(s.failed and s.copyPrefix==0))
 run incompletePrefixCopyRefusesTest=init.then(copy(1,320,2,0,false)).then(check(s.failed and s.copyPrefix==0))
 run copyErrorHasNoReadAuthorityTest=init.then(copy(1,320,3,0,true)).then(read(true,0,32993,false)).then(check(s.failed and s.reads.length()==0))
 run readErrorHasNoReadAuthorityTest=init.then(copy(1,320,3,0,false)).then(read(true,0,32993,true)).then(check(s.failed and s.reads.length()==0))
 run supportedDefaultRGBAPairRemainsExactTest=init.then(reset(2,480,6408)).then(copy(2,480,3,0,false)).then(read(false,0,6408,false)).then(read(true,0,6408,false)).then(check(not(s.failed) and allProps))
}
