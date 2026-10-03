module raster_state {
 type Observation={generation:int,enabled:bool,error:bool}
 type Event=Context|Disable|Observe(Observation)|DitherChanged|Material(bool)|Upload|Draw
 type State={generation:int,dither:bool,inspected:int,material:bool,uploaded:bool,draw:bool}
 var s:State
 action init=s'={generation:1,dither:true,inspected:0,material:false,uploaded:false,draw:false}
 action fire(e:Event):bool={val b={...s,draw:false};s'=match e {
  | Context=>{...b,generation:s.generation+1,dither:true,inspected:0,material:false,uploaded:false}
  | Disable=>{...b,dither:false,inspected:0}
  | Observe(o)=>if(o.generation==s.generation and not(o.enabled) and not(o.error) and not(s.dither)){...b,inspected:s.generation} else {...b,inspected:0}
  | DitherChanged=>{...b,dither:true,inspected:0}
  | Material(m)=>{...b,material:m}
  | Upload=>if(s.inspected==s.generation and not(s.dither) and s.material){...b,uploaded:true} else b
  | Draw=>if(s.uploaded and s.inspected==s.generation and not(s.dither) and s.material){...b,draw:true} else b
 }}
 val allProps=s.draw implies (s.uploaded and s.material and not(s.dither) and s.inspected==s.generation)
 action step={nondet e=Set(Context,Disable,Observe({generation:s.generation,enabled:s.dither,error:false}),Observe({generation:s.generation-1,enabled:false,error:false}),Observe({generation:s.generation,enabled:false,error:true}),DitherChanged,Material(true),Material(false),Upload,Draw).oneOf();fire(e)}
}
