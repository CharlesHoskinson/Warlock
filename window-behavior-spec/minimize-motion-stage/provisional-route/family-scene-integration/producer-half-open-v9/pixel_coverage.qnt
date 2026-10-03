module pixel_coverage {
 type Event=Configure({lower:int,upper:int,uniforms:bool,source:bool})|Draw(int)|Fail
 type State={configured:bool,lower:int,upper:int,effect:bool,pixel:int,covered:bool,preserved:bool}
 var s:State
 pure def inside(p:int,l:int,u:int):bool=l<=2*p+1 and 2*p+1<u
 action init=s'={configured:false,lower:0,upper:0,effect:false,pixel:0,covered:false,preserved:true}
 action fire(e:Event):bool={val b={...s,effect:false};s'=match e {
  | Configure(c)=>{...b,configured:c.uniforms and c.source and c.lower<=c.upper,lower:c.lower,upper:c.upper}
  | Draw(p)=>if(s.configured and p>=0 and p<8){val covered=inside(p,s.lower,s.upper);{...b,effect:true,pixel:p,covered:covered,preserved:not(covered)}} else b
  | Fail=>{...b,configured:false}
 }}
 val allProps=s.effect implies(s.configured and s.covered==inside(s.pixel,s.lower,s.upper) and s.preserved==not(s.covered))
 action step={nondet e=Set(Configure({lower:3,upper:9,uniforms:true,source:true}),Configure({lower:3,upper:9,uniforms:false,source:true}),Configure({lower:3,upper:9,uniforms:true,source:false}),Configure({lower:9,upper:3,uniforms:true,source:true}),Draw(0),Draw(1),Draw(2),Draw(3),Draw(4),Draw(8),Fail).oneOf();fire(e)}
}
