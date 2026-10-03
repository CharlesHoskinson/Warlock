module helper_generations {
 var generation: int
 var hydrateDone: Set[int]
 var relayDone: Set[int]
 var closes: Set[int]
 var completedCloses: Set[int]
 var refused: bool
 var stopped: bool
 var accepted: bool
 action init = all {generation'=1,hydrateDone'=Set(),relayDone'=Set(),closes'=Set(),completedCloses'=Set(),refused'=false,stopped'=false,accepted'=false}
 action hydrate = all {not(stopped),not(hydrateDone.contains(generation)),hydrateDone'=hydrateDone.union(Set(generation)),generation'=generation,relayDone'=relayDone,closes'=closes,completedCloses'=completedCloses,refused'=refused,stopped'=stopped,accepted'=accepted}
 action relay = all {not(stopped),not(relayDone.contains(generation)),relayDone'=relayDone.union(Set(generation)),generation'=generation,hydrateDone'=hydrateDone,closes'=closes,completedCloses'=completedCloses,refused'=refused,stopped'=stopped,accepted'=accepted}
 action reload = all {generation<10,hydrateDone.contains(generation),relayDone.contains(generation),not(refused),not(stopped),generation'=generation+1,hydrateDone'=hydrateDone,relayDone'=relayDone,closes'=closes,completedCloses'=completedCloses,refused'=refused,stopped'=stopped,accepted'=accepted}
 action observeLifetime = {nondet lifetime=Set(1,2,3,4,5).oneOf();all {not(stopped),not(closes.contains(lifetime)),closes'=closes.union(Set(lifetime)),generation'=generation,hydrateDone'=hydrateDone,relayDone'=relayDone,completedCloses'=completedCloses,refused'=refused,stopped'=stopped,accepted'=accepted}}
 action close = {nondet lifetime=closes.oneOf();all {not(completedCloses.contains(lifetime)),completedCloses'=completedCloses.union(Set(lifetime)),generation'=generation,hydrateDone'=hydrateDone,relayDone'=relayDone,closes'=closes,refused'=refused,stopped'=stopped,accepted'=accepted}}
 action refuse = all {refused'=true,accepted'=false,generation'=generation,hydrateDone'=hydrateDone,relayDone'=relayDone,closes'=closes,completedCloses'=completedCloses,stopped'=stopped}
 action stop = all {stopped'=true,generation'=generation,hydrateDone'=hydrateDone,relayDone'=relayDone,closes'=closes,completedCloses'=completedCloses,refused'=refused,accepted'=accepted}
 action accept = all {stopped,not(refused),hydrateDone.contains(generation),relayDone.contains(generation),completedCloses==closes,accepted'=true,generation'=generation,hydrateDone'=hydrateDone,relayDone'=relayDone,closes'=closes,completedCloses'=completedCloses,refused'=refused,stopped'=stopped}
 action idle = all {generation'=generation,hydrateDone'=hydrateDone,relayDone'=relayDone,closes'=closes,completedCloses'=completedCloses,refused'=refused,stopped'=stopped,accepted'=accepted}
 action step = any {hydrate,relay,reload,observeLifetime,close,refuse,stop,accept,idle}
 val invariant = all {generation>=1,generation<=10,1.to(generation-1).forall(g=>hydrateDone.contains(g) and relayDone.contains(g)),completedCloses.subseteq(closes),accepted implies all {stopped,not(refused),hydrateDone.contains(generation),relayDone.contains(generation),completedCloses==closes}}
 run actualLoadBeforeReloadTest = init.then(hydrate).then(relay).then(reload).then(all {assert(generation==2 and invariant),idle})
 run priorLifetimeRegistrationRetainedTest = init.then(observeLifetime).then(hydrate).then(relay).then(reload).then(all {assert(closes.size()==1 and invariant),idle})
 run incompleteNewGenerationCannotAcceptTest = init.then(hydrate).then(relay).then(reload).then(stop).then(all {assert(not(accepted) and invariant),idle})
 run refusalBlocksNextGenerationAcceptanceTest = init.then(hydrate).then(relay).then(refuse).then(stop).then(all {assert(not(accepted) and invariant),idle})
 run refusalDoesNotSkipNormalShutdownTest = init.then(hydrate).then(relay).then(refuse).then(stop).then(all {assert(stopped and not(accepted) and invariant),idle})
}
