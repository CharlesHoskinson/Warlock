module causal_target {
 type State={generation:int,extent:int,prefix:int,framebuffer:int,defaultFormat:int,copyPrefix:int,reads:List[int],failed:bool}
 var s:State
 action init=s'={generation:1,extent:320,prefix:3,framebuffer:202,defaultFormat:32993,copyPrefix:0,reads:List(),failed:false}
 action copy(generation:int,extent:int,prefix:int,target:int,error:bool):bool={
  val valid=generation==s.generation and extent==s.extent and prefix==s.prefix and target==0 and not(error)
  s'=if(valid) {...s,framebuffer:0,copyPrefix:prefix} else {...s,failed:true}
 }
 action read(native:bool,observedTarget:int,format:int,error:bool):bool={
  val valid=not(s.failed) and s.copyPrefix==s.prefix and s.framebuffer==0 and observedTarget==0 and not(error) and format==(if(native)s.defaultFormat else 6408)
  s'=if(valid) {...s,reads:s.reads.append(format)} else {...s,failed:true}
 }
 action reset(generation:int,extent:int,format:int):bool=s'={...s,generation:generation,extent:extent,defaultFormat:format,framebuffer:202,copyPrefix:0,reads:List(),failed:false}
 val sameTarget=s.reads.length()>0 implies s.framebuffer==0
 val noPrefixMutation=s.prefix==3
 val nativePairBound=s.reads.indices().forall(i=>s.reads.nth(i)==6408 or s.reads.nth(i)==s.defaultFormat)
 val allProps=sameTarget and noPrefixMutation and nativePairBound
 action step={nondet generation=1.to(2).oneOf();nondet extent=Set(320,480).oneOf();nondet prefix=Set(2,3).oneOf();nondet target=Set(0,202).oneOf();nondet format=Set(6408,32993).oneOf();nondet error=Set(false,true).oneOf();nondet native=Set(false,true).oneOf();any{copy(generation,extent,prefix,target,error),read(native,target,format,error),reset(generation,extent,format)}}
}
