module pin_input_episode_test {
 import pin_input_episode.* from "./pin_input_episode"
 action check(v:bool):bool=all{assert(v),s'=s}
 pure def row(code:int,state:int):Row={code:code,state:state,owner:true,scope:true,typed:true,fresh:true}
 action mouse=fire(Plan(1)).then(fire(Begin)).then(fire(Deliver(row(272,1)))).then(fire(Deliver(row(272,0))))
 action finish=fire(Finish).then(fire(Receipt(true))).then(fire(Observe(true))).then(fire(Accept))
 run exactDeliveredMouseAcceptsTest=init.then(mouse).then(finish).then(check(s.accepted))
 run writesAndDriverExitCannotSupplyDeliveryTest=init.then(fire(Plan(1))).then(fire(Begin)).then(fire(Write)).then(fire(DriverExit)).then(finish).then(check(not(s.accepted)))
 run missingReleaseRefusesTest=init.then(fire(Plan(1))).then(fire(Begin)).then(fire(Deliver(row(272,1)))).then(finish).then(check(not(s.accepted)))
 run upBeforeDownRefusesTest=init.then(fire(Plan(1))).then(fire(Begin)).then(fire(Deliver(row(272,0)))).then(fire(Deliver(row(272,1)))).then(finish).then(check(not(s.accepted)))
 run duplicateDownRefusesTest=init.then(fire(Plan(1))).then(fire(Begin)).then(fire(Deliver(row(272,1)))).then(fire(Deliver(row(272,1)))).then(finish).then(check(not(s.accepted)))
 run extraInputRefusesTest=init.then(mouse).then(fire(Deliver(row(272,0)))).then(finish).then(check(not(s.accepted)))
 run wrongWindowRefusesTest=init.then(fire(Plan(1))).then(fire(Begin)).then(fire(Deliver({...row(272,1),owner:false}))).then(fire(Deliver(row(272,0)))).then(finish).then(check(not(s.accepted)))
 run foreignCompositorRefusesTest=init.then(fire(Plan(1))).then(fire(Begin)).then(fire(Deliver({...row(272,1),scope:false}))).then(fire(Deliver(row(272,0)))).then(finish).then(check(not(s.accepted)))
 run stalePrefixRefusesTest=init.then(fire(Plan(1))).then(fire(Begin)).then(fire(Deliver({...row(272,1),fresh:false}))).then(fire(Deliver(row(272,0)))).then(finish).then(check(not(s.accepted)))
 run numericAliasRefusesTest=init.then(fire(Plan(1))).then(fire(Begin)).then(fire(Deliver({...row(272,1),typed:false}))).then(fire(Deliver(row(272,0)))).then(finish).then(check(not(s.accepted)))
 run wrongButtonRefusesTest=init.then(fire(Plan(1))).then(fire(Begin)).then(fire(Deliver(row(273,1)))).then(fire(Deliver(row(273,0)))).then(finish).then(check(not(s.accepted)))
 run episodeWithoutCaptureRefusesTest=init.then(fire(Deliver(row(272,1)))).then(fire(Deliver(row(272,0)))).then(finish).then(check(not(s.accepted)))
 run eventAfterAcceptedEpisodeInvalidatesTest=init.then(mouse).then(finish).then(fire(Deliver(row(272,1)))).then(check(not(s.accepted) and not(s.valid)))
 run changedRouteCannotReuseEpisodeTest=init.then(mouse).then(fire(Plan(2))).then(finish).then(check(not(s.accepted)))
 run wrongNativeReceiptRefusesTest=init.then(mouse).then(fire(Finish)).then(fire(Receipt(false))).then(fire(Observe(true))).then(fire(Accept)).then(check(not(s.accepted)))
 run changedWindowStateRefusesTest=init.then(mouse).then(fire(Finish)).then(fire(Receipt(true))).then(fire(Observe(false))).then(fire(Accept)).then(check(not(s.accepted)))
 run exactSuperPDeliveryAcceptsTest=init.then(fire(Plan(2))).then(fire(Begin)).then(fire(Deliver(row(125,1)))).then(fire(Deliver(row(25,1)))).then(fire(Deliver(row(25,0)))).then(fire(Deliver(row(125,0)))).then(finish).then(check(s.accepted))
 run exactSuperCtrlTDeliveryAcceptsTest=init.then(fire(Plan(3))).then(fire(Begin)).then(fire(Deliver(row(125,1)))).then(fire(Deliver(row(29,1)))).then(fire(Deliver(row(20,1)))).then(fire(Deliver(row(20,0)))).then(fire(Deliver(row(29,0)))).then(fire(Deliver(row(125,0)))).then(finish).then(check(s.accepted))
}
