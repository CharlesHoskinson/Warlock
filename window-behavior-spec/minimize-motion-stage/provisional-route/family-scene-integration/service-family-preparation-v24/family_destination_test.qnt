module family_destination_test {
 import family_destination.* from "./family_destination"
 action check(condition:bool):bool=all{assert(condition),s'=s}
 run obsoleteWorkerAfterFreshCannotSelectDestinationTest=init.then(fire(Observe({epoch:1,ids:List(1,2,3),complete:true,edges:true}))).then(fire(Reserve)).then(fire(Destination({epoch:1,ids:List(1,2,3),complete:true,edges:true}))).then(check(not(s.effect)))
 run currentWorkerMaySelectWholeFamilyTest=init.then(fire(Destination({epoch:1,ids:List(1,2,3),complete:true,edges:true}))).then(check(s.effect and s.effectIds==List(1,2,3)))
 run reusedPeerRejectsOldDestinationTest=init.then(fire(Replace(1))).then(fire(Destination({epoch:2,ids:List(1,2,3),complete:true,edges:true}))).then(check(not(s.effect)))
 run incompleteNativeGraphCannotSelectDestinationTest=init.then(fire(Destination({epoch:1,ids:List(1,2,3),complete:false,edges:true}))).then(check(not(s.effect)))
}
