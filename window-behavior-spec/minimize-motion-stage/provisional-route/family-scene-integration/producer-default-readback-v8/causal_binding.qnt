module causal_binding {
 type State={scene:int,generation:int,sequence:int,prefix:int,members:int,rawScene:int,rawGeneration:int,rawSequence:int,rawPrefix:int,published:bool,swapped:bool,presented:bool,attributed:bool,authority:bool}
 var s:State
 action init=s'={scene:1,generation:1,sequence:1,prefix:0,members:3,rawScene:0,rawGeneration:0,rawSequence:0,rawPrefix:0,published:false,swapped:false,presented:false,attributed:false,authority:false}
 action capture(n:int):bool=all{n>=1,n<=s.members,s'={...s,rawScene:s.scene,rawGeneration:s.generation,rawSequence:s.sequence,rawPrefix:n,published:false,attributed:false}}
 val canPublish=s.rawScene==s.scene and s.rawGeneration==s.generation and s.rawSequence==s.sequence and s.rawPrefix>=1 and s.rawPrefix<=s.members
 action publish=all{canPublish,s'={...s,prefix:s.rawPrefix,published:true}}
 action swap=s'={...s,swapped:true}
 action present=all{s.swapped,s'={...s,presented:true}}
 val canAttribute=s.published and s.swapped and s.presented and s.rawScene==s.scene and s.rawGeneration==s.generation and s.rawSequence==s.sequence
 action attribute=all{canAttribute,s'={...s,attributed:true}}
 action replace=s'={...s,scene:s.scene+1,sequence:s.sequence+1,published:false,swapped:false,presented:false,attributed:false}
 action remove=s'={...s,generation:s.generation+1,published:false,swapped:false,presented:false,attributed:false}
 val exactObservation=s.published implies (s.rawScene==s.scene and s.rawGeneration==s.generation and s.rawSequence==s.sequence and s.prefix>=1 and s.prefix<=s.members)
 val noPrefixPresentationAuthority=not(s.authority)
 val attributedOnlyExactAcceptedFullScene=s.attributed implies (s.published and s.swapped and s.presented and s.rawScene==s.scene and s.rawGeneration==s.generation and s.rawSequence==s.sequence)
 val allProps=exactObservation and noPrefixPresentationAuthority and attributedOnlyExactAcceptedFullScene
 action step=any{capture(1),capture(2),capture(3),publish,swap,present,attribute,replace,remove}
}
