module production_pipeline_test {
 import production_pipeline.* from "./production_pipeline"
 action check(p:bool):bool=all{assert(p),s'=s}
 action production=fire(Launch({raster:false,manual:false,over:false,causal:false,readback:false}))
 action diagnostic=fire(Launch({raster:true,manual:false,over:false,causal:true,readback:true}))
 run noArgumentProductionUsesRepairedPipelineTest=init.then(production).then(check(s.launched and s.repaired and not(s.raster)))
 run defaultDiagnosticUsesSameRepairedPipelineTest=init.then(diagnostic).then(check(s.launched and s.repaired and s.raster))
 run configurationAloneNeverGrantsAuthorityTest=init.then(production).then(fire(Configure(true))).then(fire(PresentEndpoint)).then(check(not(s.effect)))
 run readyAloneCannotStartProductionTest=init.then(production).then(fire(Configure(true))).then(fire(Ready)).then(fire(Start)).then(check(not(s.running)))
 run ordinaryExactLedgerSequenceMayAuthorizeEndpointTest=init.then(production).then(fire(Configure(true))).then(fire(Ready)).then(fire(Validate)).then(fire(Start)).then(fire(PresentEndpoint)).then(check(s.effect and allProps))
 run acceptedRasterPixelsCannotAuthorizeNativeStartTest=init.then(diagnostic).then(fire(Configure(true))).then(fire(Ready)).then(fire(Validate)).then(fire(Start)).then(fire(PresentEndpoint)).then(check(not(s.validated) and not(s.running) and not(s.effect)))
 run ordinaryExperimentFlagCannotEnableRasterModeTest=init.then(fire(Launch({raster:false,manual:false,over:true,causal:false,readback:false}))).then(check(not(s.launched)))
 run productionCannotRequestCausalNoAuthorityScopeTest=init.then(fire(Launch({raster:false,manual:false,over:false,causal:true,readback:true}))).then(check(not(s.launched)))
 run stdinModeSpoofCannotChangeProductionScopeTest=init.then(production).then(fire(SpoofMode)).then(check(s.repaired and not(s.raster)))
 run shaderFailureCannotFallBackOrCommitTest=init.then(production).then(fire(Configure(true))).then(fire(Ready)).then(fire(Validate)).then(fire(Start)).then(fire(Fail)).then(fire(PresentEndpoint)).then(check(s.repaired and not(s.effect)))
 run duplicateLaunchCannotDowngradeProductionTest=init.then(production).then(diagnostic).then(check(s.repaired and not(s.raster)))
}
