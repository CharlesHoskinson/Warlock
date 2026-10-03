module c1_audit {
 type Frame = {generation:int,sequence:int,token:int,position:int,velocity:int,source:int}
 pure val blank={generation:1,sequence:0,token:1,position:0,velocity:0,source:1}
 var latest:Frame
 var swapped:Frame
 var submitted:Frame
 var origin:Frame
 var originAccepted:bool
 var complete:bool
 action init=all {latest'=blank,swapped'=blank,submitted'=blank,origin'=blank,originAccepted'=false,complete'=false}
 action idle=all {latest'=latest,swapped'=swapped,submitted'=submitted,origin'=origin,originAccepted'=originAccepted,complete'=complete}
 action submit(f:Frame):bool=all {latest'=latest,swapped'=swapped,submitted'=f,origin'=origin,originAccepted'=false,complete'=false}
 action swap(f:Frame,ok:bool):bool=all {latest'=latest,swapped'=if(ok and f==submitted)f else blank,submitted'=submitted,origin'=origin,originAccepted'=false,complete'=false}
 action present(f:Frame,accepted:bool):bool={
   val ok=accepted and f==swapped and f.sequence>latest.sequence and f.generation==latest.generation and f.source==latest.source
   all {latest'=if(ok)f else latest,swapped'=swapped,submitted'=submitted,origin'=origin,originAccepted'=false,complete'=false}
 }
 action retarget(f:Frame,sameDuration:bool,sameStart:bool):bool={
   val ok=f==latest and f.sequence>0 and sameDuration and sameStart
   all {latest'=latest,swapped'=swapped,submitted'=submitted,origin'=f,originAccepted'=ok,complete'=ok}
 }
 action close=init
 val invariant=all {originAccepted implies origin==latest and origin.sequence>0,complete implies originAccepted}
 pure val one={...blank,sequence:1,position:13,velocity:71}
 pure val faults=Set(one.with("velocity",72),one.with("position",14),one.with("generation",2),one.with("sequence",2),one.with("token",2),one.with("source",2))
 action step={nondet f=Set(one,blank).union(faults).oneOf();any {submit(f),swap(f,true),swap(f,false),present(f,true),present(f,false),retarget(f,true,true),retarget(f,false,true),retarget(f,true,false),close,idle}}
 run exactDisplayedPairTest=init.then(submit(one)).then(swap(one,true)).then(present(one,true)).then(retarget(one,true,true)).then(all {assert(complete and invariant),idle})
 run submittedOnlyRefusedTest=init.then(submit(one)).then(retarget(one,true,true)).then(all {assert(not(complete) and invariant),idle})
 run swapOnlyRefusedTest=init.then(submit(one)).then(swap(one,true)).then(retarget(one,true,true)).then(all {assert(not(complete) and invariant),idle})
 run failedSwapRefusedTest=init.then(submit(one)).then(swap(one,false)).then(present(one,true)).then(retarget(one,true,true)).then(all {assert(not(complete) and invariant),idle})
 run earlyFeedbackRefusedTest=init.then(submit(one)).then(present(one,false)).then(retarget(one,true,true)).then(all {assert(not(complete) and invariant),idle})
 run velocityChangeRefusedTest=init.then(submit(one)).then(swap(one,true)).then(present(one,true)).then(retarget(one.with("velocity",72),true,true)).then(all {assert(not(complete) and invariant),idle})
 run outputGenerationRefusedTest=init.then(submit(one)).then(swap(one,true)).then(present(one,true)).then(retarget(one.with("generation",2),true,true)).then(all {assert(not(complete) and invariant),idle})
 run differentDurationRefusedTest=init.then(submit(one)).then(swap(one,true)).then(present(one,true)).then(retarget(one,false,true)).then(all {assert(not(complete) and invariant),idle})
 run differentStartRefusedTest=init.then(submit(one)).then(swap(one,true)).then(present(one,true)).then(retarget(one,true,false)).then(all {assert(not(complete) and invariant),idle})
 run closeRevokesTest=init.then(submit(one)).then(swap(one,true)).then(present(one,true)).then(retarget(one,true,true)).then(close).then(all {assert(not(complete) and invariant),idle})
}
