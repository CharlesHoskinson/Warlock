module legacy_counterexample {
 var focus:int
 action init=focus'=2
 action oldFilteredOwnerPress=focus'=focus // actual v18 !owner return
 run blockedAncestorMustRouteTest=init.then(oldFilteredOwnerPress).then(all{assert(focus==3),oldFilteredOwnerPress})
}
