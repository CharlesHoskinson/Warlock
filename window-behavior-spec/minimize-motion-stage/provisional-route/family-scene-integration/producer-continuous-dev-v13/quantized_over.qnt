module quantized_over {
 type State={generation:int,extent:int,read:int,write:int,prefix:int,red:int,alpha:int,draws:List[int],failed:bool,completed:bool}
 var s:State
 pure def nearest(n:int,d:int):int=(2*n+d)/(2*d)
 pure def over(source:int,alpha:int,destination:int):int=nearest(source*255+destination*(255-alpha),255)
 pure val colors=List({red:100,alpha:255},{red:10,alpha:128},{red:0,alpha:64})
 action reset(generation:int,extent:int):bool=s'={generation:generation,extent:extent,read:0,write:1,prefix:0,red:0,alpha:0,draws:List(),failed:false,completed:false}
 action init=reset(1,320)
 action pass(observedGeneration:int,observedExtent:int,attachment:int,index:int,blend:bool,overProgram:int,copyProgram:int,sourceTexture:int):bool={
  val valid=observedGeneration==s.generation and observedExtent==s.extent and attachment==s.write and s.read!=s.write and index==s.prefix and not(blend) and overProgram==8 and copyProgram==20 and sourceTexture!=s.read and sourceTexture!=s.write
  all{not(s.failed),not(s.completed),s.prefix<colors.length(),
      if(valid) all{val c=colors.nth(index);s'={...s,read:s.write,write:s.read,prefix:s.prefix+1,red:over(c.red,c.alpha,s.red),alpha:over(c.alpha,c.alpha,s.alpha),draws:s.draws.append(index)}}
      else s'={...s,failed:true}}
 }
 action complete=all{not(s.failed),s.prefix==colors.length(),s'={...s,completed:true}}
 val separateAttachments=s.read!=s.write
 val prefixOrdering=s.draws.indices().forall(i=>s.draws.nth(i)==i) and s.prefix==s.draws.length()
 val premultiplied=s.red>=0 and s.red<=s.alpha and s.alpha<=255
 val failureNoCompletion=not(s.failed and s.completed)
 val exactFinal=if(s.completed) s.red==45 and s.alpha==255 else true
 val allProps=separateAttachments and prefixOrdering and premultiplied and failureNoCompletion and exactFinal
 action step={nondet g=1.to(3).oneOf();nondet e=Set(320,480).oneOf();nondet a=Set(0,1).oneOf();nondet i=0.to(3).oneOf();nondet b=Set(false,true).oneOf();nondet over=Set(8,20,909).oneOf();nondet copy=Set(8,20,909).oneOf();nondet source=Set(0,1,2).oneOf();any{reset(g,e),pass(g,e,a,i,b,over,copy,source),complete}}
}
