module physical_code {
 type Code={symbol:int,wire:int,xkb:int,name:int,mods:int,layout:int}
 pure val codes=Map(45->12,48->11,49->2,50->3,51->4,52->5,53->6,54->7,55->8,56->9,57->10,97->30,98->48,99->46,100->32,101->18,102->33,103->34,104->35,105->23,106->36,107->37,108->38,109->50,110->49,111->24,112->25,113->16,114->19,115->31,116->20,117->22,118->47,119->17,120->45,121->21,122->44,65361->105)
 def valid(c:Code):bool=codes.keys().contains(c.symbol)and c.wire==codes.get(c.symbol)and c.xkb==c.wire+8 and c.name==c.symbol and c.mods==0 and c.layout==0
 var accepted:bool
 var last:Code
 action init=all{accepted'=false,last'={symbol:45,wire:0,xkb:0,name:0,mods:0,layout:0}}
 action admit(c:Code):bool=all{accepted'=valid(c),last'=c}
 val allProps=accepted implies codes.keys().contains(last.symbol)and last.wire==codes.get(last.symbol)and last.xkb==last.wire+8 and last.mods==0 and last.layout==0 and last.name==last.symbol
 action step={nondet symbol=Set(45,48,97,65361,27,999).oneOf();nondet wire=Set(0,1,12,30,105,1000).oneOf();nondet offset=Set(7,8,9).oneOf();nondet mods=Set(0,1).oneOf();admit({symbol:symbol,wire:wire,xkb:wire+offset,name:symbol,mods:mods,layout:0})}
 action check(v:bool):bool=all{assert(v),accepted'=accepted,last'=last}
}
