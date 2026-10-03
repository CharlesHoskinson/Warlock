module production_pipeline {
 type Event=Launch({raster:bool,manual:bool,over:bool,causal:bool,readback:bool})|Configure(bool)|Ready|Validate|Start|PresentEndpoint|SpoofMode|Fail
 type State={launched:bool,raster:bool,repaired:bool,configured:bool,ready:bool,validated:bool,running:bool,endpoint:bool,effect:bool}
 var s:State
 action init=s'={launched:false,raster:false,repaired:false,configured:false,ready:false,validated:false,running:false,endpoint:false,effect:false}
 action fire(e:Event):bool={val b={...s,effect:false};s'=match e {
  | Launch(p)=>if(not(s.launched) and not(p.manual and p.over) and (not(p.manual or p.over) or p.raster and p.causal and p.readback) and (not(p.causal) or p.raster and p.readback) and (not(p.readback) or p.raster)) {...b,launched:true,raster:p.raster,repaired:not(p.manual) or p.over} else b
  | Configure(ok)=>if(s.launched){...b,configured:ok} else b
  | Ready=>if(s.launched and s.configured){...b,ready:true} else b
  | Validate=>if(s.launched and not(s.raster) and s.repaired and s.ready){...b,validated:true} else b
  | Start=>if(s.validated and not(s.raster) and s.repaired and s.configured){...b,running:true} else b
  | PresentEndpoint=>if(s.running and s.configured and s.ready and s.validated and not(s.raster)){...b,endpoint:true,effect:true} else b
  | SpoofMode=>b
  | Fail=>{...b,configured:false,ready:false,validated:false,running:false,endpoint:false}
 }}
 val allProps=(s.launched and not(s.raster) implies s.repaired) and (s.raster implies not(s.validated) and not(s.running) and not(s.effect)) and (s.effect implies(s.repaired and s.configured and s.ready and s.validated and s.running and s.endpoint and not(s.raster)))
 action step={nondet e=Set(Launch({raster:false,manual:false,over:false,causal:false,readback:false}),Launch({raster:true,manual:false,over:false,causal:true,readback:true}),Launch({raster:true,manual:true,over:false,causal:true,readback:true}),Launch({raster:true,manual:false,over:true,causal:true,readback:true}),Launch({raster:false,manual:false,over:true,causal:false,readback:false}),Launch({raster:false,manual:false,over:false,causal:true,readback:true}),Configure(true),Configure(false),Ready,Validate,Start,PresentEndpoint,SpoofMode,Fail).oneOf();fire(e)}
}
