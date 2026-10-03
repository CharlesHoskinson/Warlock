module raster_state_test {
 import raster_state.* from "./raster_state"
 action check(p:bool):bool=all{assert(p),s'=s}
 run defaultDitherCannotUploadOrDrawTest=init.then(fire(Material(true))).then(fire(Upload)).then(fire(Draw)).then(check(not(s.draw) and not(s.uploaded)))
 run disabledAndActuallyInspectedContextAllowsDrawTest=init.then(fire(Material(true))).then(fire(Disable)).then(fire(Observe({generation:1,enabled:false,error:false}))).then(fire(Upload)).then(fire(Draw)).then(check(s.draw))
 run oldContextStateObservationCannotEnableNewContextTest=init.then(fire(Material(true))).then(fire(Disable)).then(fire(Observe({generation:1,enabled:false,error:false}))).then(fire(Context)).then(fire(Observe({generation:1,enabled:false,error:false}))).then(fire(Upload)).then(check(not(s.uploaded)))
 run reenabledDitherCannotDrawExistingUploadTest=init.then(fire(Material(true))).then(fire(Disable)).then(fire(Observe({generation:1,enabled:false,error:false}))).then(fire(Upload)).then(fire(DitherChanged)).then(fire(Draw)).then(check(not(s.draw)))
}
